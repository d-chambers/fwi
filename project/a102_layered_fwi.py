"""
Setup-up a layered inversion.
"""

import matplotlib.pyplot as plt
import specster as sp
from specster.fwi.misfit import WaveformMisfit

import local

if __name__ == "__main__":
    if local.layered_fwi_path.exists():
        inverter = sp.Inverter.load_inverter(local.layered_fwi_path)
    else:
        control_initial = sp.Control2d(local.layered_initial_path)
        control_true = sp.Control2d(local.layered_true_path)
        inverter = sp.Inverter(
            # Specifies where true data are found
            observed_data_path=control_true.each_source_path,
            # The initial control is used to setup the inversion
            control=control_initial,
            # A "true" control object is needed to compare model misfit
            true_control=control_true,
            # The working_path optionally specifies where the inverter does its work
            working_path=local.layered_fwi_path,
            misfit=WaveformMisfit(),
            kernels=("beta",),
        )
    inverter._max_iteration_change = .05
    for _ in range(10):
        inverter.run_iteration()

    fig1, _ = local.plot_model_updates(inverter)
    plt.tight_layout()
    fig1.savefig(local.layered_fwi_path / "model_updates.png", bbox_inches="tight", pad_inches=0)
    # now plot final model.
    fig2, ax = local.plot_final_model(inverter)
    plt.tight_layout()
    fig2.savefig(local.layered_fwi_path / "final_model.png", bbox_inches="tight", pad_inches=0)
    # plot misfit by iteration.
    fig3, ax = local.plot_misfit(inverter)
    plt.tight_layout()
    fig3.savefig(local.layered_fwi_path / "mode_convergence.png")