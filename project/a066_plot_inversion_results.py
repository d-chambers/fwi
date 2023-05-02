"""
Create a split of the inclusion with homogeneous velocity.
"""
from pathlib import Path

import local
import matplotlib.pyplot as plt
import pandas as pd
import specster as sp
from specster.core.plotting import plot_single_gll
from specster.fwi.misfit import WaveformMisFit


def load_model_updates(inverter):
    """Load all the model updates into a dataframe."""
    out = {}
    for it in range(1, 100):
        base_path = inverter._get_iteration_directory(it)
        path = base_path / inverter._iteration_kernel_file_name
        if not path.exists():
            break
        out[it] = pd.read_parquet(path)
    return out


def plot_model_updates(inverter):
    """First load all the update dataframes."""
    models = load_model_updates(inverter)
    fig, axes = plt.subplots(len(models), 1, figsize=(4, 6))
    for (iteration, model), ax in zip(models.items(), axes):
        df = model.reset_index()
        ax = plot_single_gll(ax, df, "beta", ("x", "z"), 6)
        ax.set_title(f"Beta: {iteration}")
    plt.tight_layout()
    return fig, axes


def plot_final_model(inverter):
    """Plot final and correct model together."""
    #
    iteration = len(inverter.iteration_results)
    base_path = inverter._get_iteration_directory(iteration)
    path = base_path / inverter._material_model_file_name
    assert path.exists()

    df = pd.read_parquet(path)
    true_mod = inverter._true_model

    vlims = [3180, 3220]

    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1 = plot_single_gll(ax1, df, "vs", ("x", "z"), 6, vlims=vlims)
    ax2 = plot_single_gll(ax2, true_mod, "vs", ("x", "z"), 6, vlims=vlims)

    return fig, (ax1, ax2)

def plot_misfit(inverter):
    """Make a plot of the misfit functions."""
    it_res = inverter.iteration_results
    misfits = [x.data_misfit for x in it_res]
    iterations = range(1, len(it_res) + 1)
    fig, ax = plt.subplots(1, 1)
    ax.plot(iterations, misfits, '.')
    return fig, ax


if __name__ == "__main__":
    inverter = sp.Inverter.load_inverter(local.fwi_work_path)
    # plot model updates.
    fig1, _ = plot_model_updates(inverter)
    fig1.savefig(local.model_update_path, bbox_inches="tight", pad_inches=0)
    # now plot final model.
    fig2, ax = plot_final_model(inverter)
    fig2.savefig(local.final_model_path, bbox_inches="tight", pad_inches=0)
    # plot misfit by iteration.
    fig3, ax = plot_misfit(inverter)
