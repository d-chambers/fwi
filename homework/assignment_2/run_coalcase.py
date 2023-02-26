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
    fig, ax = plot_traces(x_traces, color="blue")
    fig.savefig("COALCASE1/OUTPUT_FILES/X_trace_plot.png")
    #
    fig, ax = plot_traces(z_traces, color="red")
    fig.savefig("COALCASE1/OUTPUT_FILES/z_trace_plot.png")


if __name__ == "__main__":
    control = specster.Control2d('COALCASE1')
    # control.clear_outputs()
    if control.empty_output:
        control.xmeshfem2d()
        control.xspecfem2d()
    st = control.get_waveforms()
    make_waveform_plot(st)




