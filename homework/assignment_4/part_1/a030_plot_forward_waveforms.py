"""
Calculate the True model seismograms.
"""
import matplotlib.pyplot as plt
import obspy

import local
from utils import read_trace, read_source_time_function


def add_phases(ax):
    """Add phases and labels. These are just based on observation."""
    ylims = ax.get_ylim()
    diff = max(ylims) - min(ylims)
    offset = min(ylims) + diff * 0.05

    # annotate S
    s_arrival = 37
    ax.axvline(s_arrival, ls='--', color='red')
    ax.annotate('S', (s_arrival, offset))

    # ax.axvline(37, ls='--', color='blue')
    s_s_arrival = 46.4
    ax.axvline(s_s_arrival, ls='--', color='orange')
    ax.annotate('S-S', (s_s_arrival, offset))


if __name__ == "__main__":
    ws = local.get_workspace()
    # load forward waveform
    st_forward = obspy.Stream(
        [read_trace(x) for x in ws.output_path.glob("*semd")]
    )
    # load source time function
    st_stf = obspy.Stream(
        [read_source_time_function(x) for x in ws.output_path.glob("plot_source_time*")]
    )
    # init mpl stuff
    fig, axes = plt.subplots(2, 1, sharex=True)

    # plot source time function
    axes[0].plot(st_stf[0].times(), st_stf[0].data)
    axes[0].set_title("Source Time Function")

    # plot Y component
    axes[1].plot(st_forward[0].times(), st_forward[0].data)
    axes[1].set_title("Station Recording")
    axes[1].set_xlabel("Simulation Time (s)")
    add_phases(axes[1])

    fig.savefig(local.true_waveforms_plot)
