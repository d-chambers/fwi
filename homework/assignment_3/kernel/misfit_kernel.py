"""
2D Kernel with SPECFEM2D
Based on a notebook by Andrea R.
Utility functions written by Ridvan Orsvuran.
Following file structure as in the Seisflows example (By Bryant Chow)
"""
import os
import shutil
from functools import cache
from pathlib import Path
from subprocess import run

import fwi_plot
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import obspy
from pydantic import Field
from pydantic.dataclasses import dataclass
from scipy.integrate import simps
from utils import (
    grid,
    read_trace,
    replace_line,
    save_trace,
    specfem2D_prep_adjoint,
    specfem2D_prep_save_forward,
)

matplotlib.rcParams.update({"font.size": 14})


class ExecutionError(Exception):
    """Raised when something goes wrong running binary."""


@dataclass
class Workspace:
    """
    A workspace for keeping track of various parameters.
    """

    bin_path: Path
    template_path: Path
    work_path: Path = Field(default_factory=os.getcwd)

    # --- Path and directory setup methods.

    @property
    def data_path(self):
        return self.work_path / "DATA"

    @property
    def par_file_path(self):
        return self.data_path / "Par_file"

    @property
    def output_path(self):
        out = self.work_path / "OUTPUT_FILES"
        out.mkdir(exist_ok=True, parents=True)
        return out

    def refresh(self, only_data=False):
        """
        Refresh the workspace.

        Deletes data and output files, re-copies template directory.
        """
        refresh_directory(self.data_path, make_new=False)
        shutil.copytree(self.template_path, self.data_path)
        if not only_data:
            refresh_directory(self.output_path)

    # --- Functions for running specfem programs.

    def xmesh(self):
        """Run the mesher"""
        return self._run_command("xmeshfem2D")

    def xspec(self):
        """Run the forward solver"""
        return self._run_command("xspecfem2D")

    # --- various simulation functions

    def run(self, output_name=None):
        """Run mesher and specfem."""
        _ = self.xmesh()
        spec = self.xspec()
        if output_name:
            output_path = self.work_path / output_name
            if output_path.exists() and output_path.is_dir():
                shutil.rmtree(output_path)
            self._copy_input_to_output()
            shutil.copytree(self.output_path, output_path)
        return spec

    def run_forward(self, output_name=None):
        """Run the forward simulations."""
        specfem2D_prep_save_forward(self.par_file_path)
        return self.run(output_name=output_name)

    def run_adjoint(self, misfit: "MisFit", output_name=None, previous_output=None):
        """Run the adjoint."""
        # deal with specific initial model
        if previous_output:
            self.refresh(only_data=True)
            path = self.work_path / previous_output
            shutil.copytree(path, self.data_path)
        specfem2D_prep_adjoint(self.par_file_path)
        misfit.save_adjoint_sources(self.work_path / "SEM")
        return self.run(output_name=output_name)

    def replace_par_line(self, line_number, text):
        """Replace a line in the parfile."""
        replace_line(self.par_file_path, line_number, text)

    # --- Private utils

    def _run_command(self, name):
        """Run a generic command in bin directory."""
        bin_path = self.bin_path / name
        assert bin_path.exists(), f"No such binary file {bin_path}"
        output = run(bin_path, cwd=self.work_path, capture_output=True)
        output_path = self.output_path / f"{name}.txt"
        with output_path.open("w") as fi:
            fi.write(output.stdout.decode("UTF8"))
        if output.returncode != 0:
            msg = output.stderr.decode("UTF8")
            raise ExecutionError(msg)
        return output

    def _copy_input_to_output(self):
        """Copies all input data files to output directory."""
        for path in self.data_path.glob("*"):
            new_path = self.output_path / path.name
            if path.is_file():
                shutil.copy2(path, new_path)
            else:
                shutil.copytree(path, new_path)


class MisFit:
    """
    Container class to calculate misfits and adjoint sources.

    Parameters
    ----------
    observed_path
        The directory containing the observed data.
    synthetic_path
        The directory containing the synthetic data.
    """

    def __init__(self, observed_path, synthetic_path):
        """Read in the streams for each directory."""
        self.st1 = self.load_streams(observed_path)
        self.st2 = self.load_streams(synthetic_path)
        self.validate_streams()

    def preprocess(self, st):
        """Preprocess the streams."""
        out = (
            st.detrend("linear")
            .taper(0.05)
            .filter("bandpass", freqmin=0.01, freqmax=20)
        )
        return out

    def validate_streams(self):
        """Custom validation for streams."""
        st1 = self.st1
        st2 = self.st2
        assert len(st1) == len(st2)
        assert {tr.id for tr in st1} == {tr.id for tr in st2}

    def load_streams(self, directory_path):
        """Load all streams in a directory."""
        traces = []
        for path in Path(directory_path).rglob("*semd*"):
            traces.append(read_trace(str(path)))
        st = self.preprocess(obspy.Stream(traces).sort())
        return st

    def iterate_streams(self):
        """Iterate streams, yield corresponding traces"""
        st1, st2 = self.st1, self.st2
        for tr1, tr2 in zip(st1, st2):
            assert tr1.id == tr2.id
            assert tr1.stats.sampling_rate == tr2.stats.sampling_rate
            yield tr1, tr2

    @cache
    def calc_misfit(self):
        """Calculate the misfit between streams."""
        out = {}
        for tr1, tr2 in self.iterate_streams():
            misfit = simps((tr2.data - tr1.data) ** 2, dx=tr1.stats.delta)
            out[tr1.id] = misfit
        return out

    @cache
    def get_adjoint_sources(self):
        """Return the adjoint source trace."""
        out = []
        for tr1, tr2 in self.iterate_streams():
            new = tr1.copy()
            new.data = tr2.data - tr1.data
            out.append(new)
        return out

    def save_adjoint_sources(self, path="SEM"):
        """Save adjoint sources to disk."""
        path = Path(path)
        path.mkdir(exist_ok=True, parents=True)
        for tr in self.get_adjoint_sources():
            stats = tr.stats
            name = f"{stats.network}.{stats.station}.{stats.channel}.adj"
            new_path = path / name
            save_trace(tr, new_path)

    def plot(self, trace_index=0):
        """Create a plot of observed/synthetic."""
        # tr1, tr2 = self.st1[trace_index], self.st2[trace_index]
        # breakpoint()

        # fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, figsize=(20, 8))
        # ax1.plot(obsd.times() + obsd.stats.b, obsd.data, "b", label="obsd")
        # ax1.plot(synt.times() + synt.stats.b, synt.data, "r", label="synt")
        # ax1.set_xlim(obsd.stats.b, obsd.times()[-1] + obsd.stats.b)
        # ax1.legend()
        # ax1.legend(frameon=False)
        # ax1.set_ylabel("Displacement (m)")
        #
        # ax2.plot(adj.times() + adj.stats.b, adj.data, "g", label="Adjoint Source")
        # ax2.legend()
        # ax2.legend(frameon=False)
        # ax2.set_xlabel("Time (s)")
        # ax.tick_params(axis="both", which="major", labelsize=14)


def refresh_directory(dir_path: Path, make_new=True):
    """Make a fresh directory, delete old contents."""
    dir_path = Path(dir_path)
    if dir_path.exists():
        shutil.rmtree(dir_path)
    if make_new:
        dir_path.mkdir(exist_ok=True, parents=True)
    return dir_path


if __name__ == "__main__":
    ws = Workspace(
        work_path=Path(os.getcwd()) / "work",
        bin_path=Path("/media/data/Gits/specfem2d/bin"),
        template_path=Path(os.getcwd()) / "Examples" / "DATA_Example01",
    )
    # refresh the simulation
    # ws.refresh()

    # --- Run True model

    # # perturb velocity
    new_line = "1 1 2700.d0 3000.d0 1800.d0 0 0 9999 9999 0 0 0 0 0 0 \n"
    ws.replace_par_line(262, new_line)
    ws.run_forward(output_name="OUTPUT_FILES_TRUE")
    #
    # # --- Run forward initial model
    # # reset velocity
    new_line = "1 1 2700.d0 3000.d0 1800.d0 0 0 9999 9999 0 0 0 0 0 0 \n"
    ws.replace_par_line(262, new_line)
    ws.run_forward(output_name="OUTPUT_FILES_INITIAL")

    # --- Run waveform adjoint
    # get misfit
    misfit_wf = MisFit(
        ws.work_path / "OUTPUT_FILES_TRUE",
        ws.work_path / "OUTPUT_FILES_INITIAL",
    )
    # misfit_wf.calc_misfit()
    # adj = misfit_wf.calc_misfit()
    # Run adjoint
    # breakpoint()
    out = ws.run_adjoint(misfit_wf, "OUTPUT_FILES_ADJ_WF")
