"""
Create a split of the inclusion with homogeneous velocity.
"""
from pathlib import Path

import local
import matplotlib.pyplot as plt
import specster as sp
from specster.fwi.misfit import WaveformMisfit

if __name__ == "__main__":
    control_initial = sp.Control2d(local.inclusion_2d_initial_path)
    control_true = sp.Control2d(local.inclusion_2d_true_path)
    if local.fwi_smoothed_work_path.exists():
        inverter = sp.Inverter.load_inverter(local.fwi_smoothed_work_path)
    else:
        inverter = sp.Inverter(
            # Specifies where true data are found
            observed_data_path=control_true.each_source_path,
            # The initial control is used to setup the inversion
            control=control_initial,
            # A "true" control object is needed to compare model misfit
            true_control=control_true,
            smoothing_sigma=10,
            # The working_path optionally specifies where the inverter does its work
            working_path=local.fwi_smoothed_work_path,
            misfit=WaveformMisfit(),
            kernels=("beta",),
        )
    inverter._max_iteration_change = .05
    # breakpoint()
    # for _ in range(10):
        # inverter.run_iteration()


    # inverter = sp.Inverter.load_inverter(local.fwi_work_path)
    # plot model updates.
    fig1, _ = local.plot_model_updates(inverter)
    plt.tight_layout()
    fig1.savefig(local.fwi_smoothed_work_path / "model_updates.png", bbox_inches="tight", pad_inches=0)
    # now plot final model.
    fig2, ax = local.plot_final_model(inverter)
    plt.tight_layout()
    fig2.savefig(local.fwi_smoothed_work_path / "final_model.png", bbox_inches="tight", pad_inches=0)
    # plot misfit by iteration.
    fig3, ax = local.plot_misfit(inverter)
    plt.tight_layout()
    fig3.savefig(local.fwi_smoothed_work_path / "mode_convergence.png")

