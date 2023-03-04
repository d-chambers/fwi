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
import pandas as pd
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


class KernelKeeper:
    """A simple class for managing kernels."""

    def __init__(self, output_directory):
        self.kernel_files = list(Path(output_directory).rglob('*kernel.dat'))
        # find rho alpha beta and load it
        out = [x for x in self.kernel_files if 'rhop_alpha_beta' in x.name]
        assert len(out) == 1, "only one such kernel should exist."
        self.rho_alpha_beta = self.load_kernel_file(out[0])

    def load_kernel_file(self, file_path):
        """Load a particular kernel file into a dataframe."""
        names = ['x', 'z'] + list(file_path.name.split('_')[1:-1])
        df = pd.read_csv(file_path, delim_whitespace=True, names=names, header=None)
        return df

    def plot(self, columns=('rhop', 'alpha', 'beta')):
        """
        Plot several kernels.
        """
        fig, axes = plt.subplots(1, len(columns), figsize=(4*len(columns), 4))
        for ax, column in zip(axes.flatten(), columns):
            self.plot_single(column, ax=ax)
        return fig, axes

    def plot_single(self, column, ax=None, scale=0.15):
        """Plot Rho, Alpha, Beta"""
        df = self.rho_alpha_beta
        data = self.rho_alpha_beta[column]
        abs_max_val = np.abs(data).max()
        min_val, max_val = -abs_max_val * scale, abs_max_val * scale

        # extract/format data
        x_vals, z_vals, data = grid(df['x'], df['z'], df[column])
        extent = [df['x'].min(), df['x'].max(), df['z'].min(), df['z'].max()]

        # Setup figure
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))

        # plot, set labels etc.
        im = ax.imshow(data, extent=extent, cmap="seismic_r", vmin=min_val, vmax=max_val)
        ax.set_xlabel("X (m)")
        ax.set_ylabel("Z (m)")
        ax.set_title(f"{column.title()} Kernel")

        # Plot source and station
        ax.scatter(1000, 2000, 1000, marker="*", color="black", edgecolor="white")
        ax.scatter(3000, 2000, 450, marker="v", color="black", edgecolor="white")

        plt.colorbar(im, ax=ax)
        ax.tick_params(axis='both', which='major', labelsize=14)
        return ax


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
    ws.refresh()

    # --- Run True model

    # Set the True velocity
    new_line = "1 1 2700.d0 3000.d0 1820.d0 0 0 9999 9999 0 0 0 0 0 0 \n"
    ws.replace_par_line(262, new_line)
    # ws.run_forward(output_name="OUTPUT_FILES_TRUE")

    # Perturb the velocity
    new_line = "1 1 2650.d0 2950.d0 1770.d0 0 0 9999 9999 0 0 0 0 0 0 \n"
    ws.replace_par_line(262, new_line)
    # ws.run_forward(output_name="OUTPUT_FILES_INITIAL")

    # --- Run waveform adjoint
    # get misfit
    misfit_wf = MisFit(
        ws.work_path / "OUTPUT_FILES_TRUE",
        ws.work_path / "OUTPUT_FILES_INITIAL",
    )
    # misfit_wf.calc_misfit()
    # adj = misfit_wf.calc_misfit()
    # Run adjoint
    # out = ws.run_adjoint(misfit_wf, "OUTPUT_FILES_ADJ_WF")

    # --- plot kernel
    keeper = KernelKeeper(ws.work_path / "OUTPUT_FILES_ADJ_WF")
    fig, _ = keeper.plot()
    plt.tight_layout()
    breakpoint()
