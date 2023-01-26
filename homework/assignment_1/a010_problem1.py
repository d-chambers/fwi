"""
Script to run the first problem of the homework.
"""
from functools import partial

import matplotlib.pyplot as plt
import numpy as np

from heat_fdif import Simulation1D, heat_ftcs
from plotting import plot_simulations


def zero_ends(ar):
    """Function to enforce BCs of zero at ends."""
    ar[0], ar[-1] = 0, 0
    return ar


def init_ar(ar, spike=1):
    """Function to add a spike to center of array"""
    zeroes = np.zeros_like(ar)
    center = len(ar) // 2
    zeroes[center] = spike
    return zeroes


def get_plot_columns(results):
    """Get the columns that should be plotted."""
    cols = results.columns
    pcount = len(axes)
    idx = np.round(np.linspace(0, len(cols) - 1, pcount)).astype(int)
    cols_to_plot = cols[idx]
    return cols_to_plot


if __name__ == "__main__":
    dx = 1
    x_max = 100
    dt_vals = [0.4, 0.45, 0.55, 0.6]
    x_count = x_max / dx + 1
    fig, axes = plt.subplots(8, len(dt_vals), sharex=True, figsize=(8.5, 11))

    for dt, sub_axes in zip(dt_vals, axes.T):
        sim = Simulation1D(
            x_min=0,
            x_max=x_max,
            dx=dx,
            time_min=0,
            time_max=dt * 300,
            dt=dt,
            bc_func=zero_ends,
            initial_func=partial(init_ar, spike=400),
        )
        out = heat_ftcs(sim)
        cols_to_plot = get_plot_columns(out)
        fig, _ = plot_simulations(out, axes=sub_axes, fig=fig, cols_to_plot=cols_to_plot)
        sub_axes[0].set_title(f"dt={dt:.02f}" + r"$\frac{\Delta x^2}{D}$")
    # label time steps
    for ax, dt in zip(axes[:, 0], cols_to_plot.values):
        ax.set_ylabel(f"t={int(dt):d}s")

    plt.tight_layout()
    fig.savefig('problem_1.png', dpi=300)
