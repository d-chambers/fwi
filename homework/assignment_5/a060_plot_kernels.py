"""
Plot the kernels.
"""
import numpy as np
import pandas as pd
import specster as sp
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr  # has classes for tick-locating and -formatting

import local


def numfmt(x, pos):  # your custom formatter function: divide by 100.0
    s = '{}'.format(x / 1000.0)
    return s


def mute_stations_events_kernel(kernel, control, buff_dist=0.0075):
    """Mute the stations and events in the kernel."""
    def _get_source_receiver_locs(control):
        loc_list = ['xs', 'zs']
        station_df = control.get_station_df()[loc_list]
        event_df = control.get_source_df()[loc_list]
        locations = np.vstack([station_df.values, event_df.values])
        return locations

    def _get_min_dist(control):
        """Get the max distance from point to mute."""
        lims = control.output.lims
        diffs = [x[1]-x[0] for x in lims.values()]
        return np.linalg.norm(diffs)

    out = kernel.copy().set_index(['x', 'z'])
    array = out.values
    kernel_locs = kernel[['x', 'z']]
    limit = _get_min_dist(control) * buff_dist
    for loc in _get_source_receiver_locs(control):
        dist = np.linalg.norm(kernel_locs - loc, axis=1)
        should_mute = dist <= limit
        muted_region = array[should_mute]
        array[should_mute] = muted_region[np.argmin(np.abs(muted_region))]
    return pd.DataFrame(array, index=out.index, columns=out.columns).reset_index()


def plot_kernel(output, kernel, output_path):
    """Plot the kernel."""
    fig, ax = output.plot_kernels(columns=['beta'], kernel_df=kernel)
    # polish the figure and save.
    fig.set_size_inches(7.5, 3)
    ax.invert_yaxis()
    ax.set_title(f"SH Beta Kernel: {misfit_name}")
    # set x/Z labels to km to be less confusing.
    ax.set_xlabel('X (km)')
    ax.set_ylabel("Z (km)")
    yfmt = tkr.FuncFormatter(numfmt)
    ax.yaxis.set_major_formatter(yfmt)
    ax.xaxis.set_major_formatter(yfmt)
    ax.set_title('')
    if output_path:
        plt.tight_layout()
        output_path.parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(output_path)

    return fig, ax


if __name__ == "__main__":

    for misfit_path in local.kernel_paths.glob('*'):
        assert misfit_path.is_dir()
        misfit_name = misfit_path.name

        control = sp.Control2d(misfit_path)
        out = control.output
        kernel = out.load_kernel()

        # first plot un-muted
        out_path = local.kernel_plot / f"{misfit_name}_raw.png"
        plot_kernel(out, kernel, out_path)

        # then muted
        kernel_muted = mute_stations_events_kernel(kernel, control)
        out_path = local.kernel_plot / f"{misfit_name}_muted.png"
        plot_kernel(out, kernel_muted, out_path)
