"""
Create a split of the inclusion with homogeneous velocity.

This time, however, use randomly distributed sources and receivers.
"""
from pathlib import Path

import numpy as np

import local
import matplotlib.pyplot as plt
import specster as sp
from specster.fwi.misfit import WaveformMisfit


def randomize_source_receivers(control, start=10_000, end=90_000):
    """overwrite source locations to random between 10_000 and 90_000 meters."""
    station_coords = np.random.rand(len(control.stations), 2) * (end - start) + start
    for new_coord, sta in zip(station_coords, control.stations):
        sta.xs, sta.zs = new_coord

    source_coords = np.random.rand(len(control.sources), 2) * (end - start) + start
    for new_coord, source in zip(source_coords, control.sources):
        source.xs, source.zs = new_coord

    return control


def assert_df_coords_same(df1, df2):
    """The coordinates should be the same. """
    assert df1[['xs', 'zs']].equals(df2[['xs', 'zs']])


if __name__ == "__main__":
    if not local.inclusion_2d_initial_random_path.exists():
        control_true = (
            sp.Control2d(local.inclusion_2d_true_path)
            .copy(local.inclusion_2d_true_random_path)
        )
        randomize_source_receivers(control_true)
        control_true.prepare_fwi_forward().run()
        control_initial = control_true.copy(local.inclusion_2d_initial_random_path)
        local.create_initial_model(control_initial)
        control_initial.prepare_fwi_forward().run()
    else:
        control_true = sp.Control2d(local.inclusion_2d_true_random_path)
        control_initial = sp.Control2d(local.inclusion_2d_initial_random_path)
    # ensure station/source locations are identical
    sta1, sta2 = control_initial.get_station_df(), control_true.get_station_df()
    assert_df_coords_same(sta1, sta2)
    df1, df2 = control_initial.get_source_df(), control_true.get_source_df()
    assert_df_coords_same(df1, df2)
    if local.fwi_random_path.exists():
        inverter = sp.Inverter.load_inverter(local.fwi_random_path)
    else:
        inverter = sp.Inverter(
            # Specifies where true data are found
            observed_data_path=control_true.each_source_path,
            # The initial control is used to setup the inversion
            control=control_initial,
            # A "true" control object is needed to compare model misfit
            true_control=control_true,
            # The working_path optionally specifies where the inverter does its work
            working_path=local.fwi_random_path,
            misfit=WaveformMisfit(normalize=False),
            kernels=("beta",),
        )
    inverter._max_iteration_change = .05
    # for _ in range(10):
    #     inverter.run_iteration()

    fig1, _ = local.plot_model_updates(inverter)
    plt.tight_layout()
    fig1.savefig(local.fwi_random_path / "model_updates.png", bbox_inches="tight", pad_inches=0)
    # now plot final model.
    fig2, ax = local.plot_final_model(inverter)
    plt.tight_layout()
    fig2.savefig(local.fwi_random_path / "final_model.png", bbox_inches="tight", pad_inches=0)
    # plot misfit by iteration.
    fig3, ax = local.plot_misfit(inverter)
    plt.tight_layout()
    fig3.savefig(local.fwi_random_path / "mode_convergence.png")