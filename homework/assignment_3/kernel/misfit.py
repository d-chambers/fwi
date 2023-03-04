"""
Modules for storing various misfit functions.
"""
import abc
from functools import cache
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import obspy
from matplotlib.lines import Line2D
from scipy.integrate import simps

from utils import (
    read_trace,
    save_trace,
)

matplotlib.rcParams.update({"font.size": 14})


class _BaseMisFit(abc.ABC):

    _component_colors = {
        'Z': "orange",
        "X": "cyan",
        "Y": "Red"

    }

    def __init__(self, observed_path, synthetic_path):
        """Read in the streams for each directory."""
        self.st1 = self.load_streams(observed_path)
        self.st2 = self.load_streams(synthetic_path)
        self.validate_streams()

    def preprocess(self, st):
        """Preprocess the streams."""
        import local
        freq_min = local.bandwidth[0]
        freq_max = local.bandwidth[1]

        out = (
            st.detrend("linear")
            .taper(0.05)
            .filter("bandpass", freqmin=freq_min, freqmax=freq_max)
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

    def save_adjoint_sources(self, path="SEM"):
        """Save adjoint sources to disk."""
        path = Path(path)
        path.mkdir(exist_ok=True, parents=True)
        for tr in self.get_adjoint_sources():
            stats = tr.stats
            name = f"{stats.network}.{stats.station}.{stats.channel}.adj"
            new_path = path / name
            save_trace(tr, new_path)

    @abc.abstractmethod
    def calc_misfit(self) -> dict[str, float]:
        """Calculate the misfit between streams."""

    @abc.abstractmethod
    def get_adjoint_sources(self) -> obspy.Stream:
        """Return the adjoint source trace."""

    def plot(self, station=None):
        """Create a plot of observed/synthetic."""

        def add_legends(ax):
            """Add the legends for component and synth/observed."""
            line1 = Line2D([0], [0], color='0.5', ls='--', label="predicted")
            line2 = Line2D([0], [0], color='0.5', ls='-', label="observed")

            # Create a legend for the first line.
            _ = ax.legend(handles=[line1, line2], loc='upper right')

            color_lines = [
                Line2D([0], [0], color=self._component_colors[x],
                ls='-', label=f"{x} component")
                for x in self._component_colors
            ]
            _ = ax.legend(handles=color_lines, loc='upper left')


        fig, (wf_ax, ad_ax) = plt.subplots(2, 1, sharex=True, figsize=(10, 5))

        unique_stations = {tr.stats.station for tr in self.st1}
        station = list(unique_stations)[0] if station is None else station

        adjoint = self.get_adjoint_sources()

        for num, (tr1, tr2) in enumerate(self.iterate_streams()):
            if tr1.stats.station != station:
                continue
            ad_tr = adjoint[num]
            # make plots of observed/synthetics
            color = self._component_colors[tr1.stats.component]
            wf_ax.plot(tr1.times(), tr1.data, '-', color=color)
            wf_ax.plot(tr2.times(), tr2.data, '--', color=color)
            add_legends(wf_ax)
            ad_ax.plot(ad_tr.times(), ad_tr.data, '-', color=color)

        wf_ax.set_title("Waveforms")
        ad_ax.set_title("Adjoint Source")

        ad_ax.set_xlabel('Time (s)')
        fig.supylabel("Displacement (m)")


        breakpoint()
        # tr1, tr2 = self.st1[trace_index], self.st2[trace_index]

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





class WaveformMisFit(_BaseMisFit):
    """
    Container class to calculate misfits and adjoint sources.

    Parameters
    ----------
    observed_path
        The directory containing the observed data.
    synthetic_path
        The directory containing the synthetic data.
    """
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