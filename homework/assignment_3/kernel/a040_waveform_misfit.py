"""
Calculate the waveform misfit kernel and make associated plots.
"""

import local
from misfit import WaveformMisFit
from misfit_kernel import KernelKeeper

if __name__ == "__main__":
    ws = local.get_workspace()
    local.reset_output_to_initial(ws)

    # -- get misfit and plot
    misfit_wf = WaveformMisFit(
        ws.work_path / local.true_model_output,
        ws.work_path / local.initial_model_output,
    )
    fig, _ = misfit_wf.plot(out_file=local.wf_misfit_waveform_plot)

    # --- Run adjoint with wf misfit
    ws.run_adjoint(misfit_wf, output_name=local.wf_adjoint_output)

    # --- plot kernel
    keeper = KernelKeeper(
        ws.work_path / local.wf_adjoint_output,
        sources=[local.source_location],
        receivers=[local.station_location],
    )
    fig, _ = keeper.plot(out_file=local.wf_kernel_plot, scale=0.01)
