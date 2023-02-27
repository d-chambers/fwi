"""
Script to run the coal stuff.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import specster


def read_stations(path="COALCASE1/OUTPUT_FILES/output_list_stations.txt"):
    """Read the station files."""
    path = Path(path)
    df = pd.read_csv(path, header=None, delim_whitespace=True)
    df.columns = ["station", "network", "x", "z"]
    return df


def make_waveform_plot(st, event_location=(2000, 1500), amplification=120):
    """Make a plot of waveforms."""

    def set_ylims(ax1, ax2):
        y1 = ax1.get_ylim()
        y2 = ax2.get_ylim()
        min_low = min([y1[0], y2[0]])
        max_high = max([y1[1], y2[1]])
        ax1.set_ylim([min_low, max_high])
        ax2.set_ylim([min_low, max_high])

    def get_distance(tr):
        """Get coordinates of the station of trace. """
        sta, net = tr.stats.station, tr.stats.network
        ser = df[(df['station']==sta) & (df['network']==net)].iloc[0]

        dist = np.linalg.norm(np.array(event_location) - ser[['x', 'z']].values)
        return dist

    def plot_traces(traces, color='blue'):
        fig, ax = plt.subplots(1, 1)
        max_amp = np.max([np.max(np.abs(tr.data)) for tr in traces])
        for tr in traces:
            distance = get_distance(tr)
            data = (tr.data / max_amp) * amplification
            ax.plot(data + distance, color=color)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel("Source Receiver Distance (m)")
        return fig, ax

    st = st.detrend('linear')
    x_traces = [tr for tr in st if tr.stats.channel == 'BXX']
    z_traces = [tr for tr in st if tr.stats.channel == "BXZ"]
    df = read_stations()
    fig1, ax1 = plot_traces(x_traces, color="blue")
    fig2, ax2 = plot_traces(z_traces, color="red")
    set_ylims(ax1, ax2)

    fig1.savefig("COALCASE1/OUTPUT_FILES/X_trace_plot.png")
    fig2.savefig("COALCASE1/OUTPUT_FILES/z_trace_plot.png")


def plot_points(path="COALCASE1/OUTPUT_FILES/points_per_wavelength_histogram_S_in_solid.txt"):
    """Plot the histogram of GLLs per wavelength. """
    path = Path(path)
    df = pd.read_csv(path, delim_whitespace=True, header=None)
    df.columns = ['gll', 'percentage']
    plt.close('all')
    fig, ax = plt.subplots(1, 1)
    # ax.plot(, df['gll'], '.')
    ax.bar(df['gll'], df['percentage'], edgecolor='black', width=0.16)
    ax.set_xlabel('GLL per S Wavelength')
    ax.set_ylabel("% of Pixels")
    fig.savefig("COALCASE1/OUTPUT_FILES/GLL_histogram.png")



if __name__ == "__main__":
    control = specster.Control2d('COALCASE1')
    # control.clear_outputs()
    if control.empty_output:
        control.xmeshfem2d()
        control.xspecfem2d()

    # get waveforms, plot them
    st = control.get_waveforms()
    # Apply bandpass filter based on output file recommendations
    min_freq = 0.05
    max_freq = 20.0
    st_filtered = st.filter('bandpass', freqmin=min_freq, freqmax=max_freq)
    make_waveform_plot(st)

    # plot the points
    plot_points()




