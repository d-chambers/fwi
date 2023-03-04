"""
Calculate the waveform misfit kernel and make associated plots.
"""
import shutil

import local
from misfit import WaveformMisFit


def refresh_output():
    """Refresh the output folder, set to initial output."""
    output_path = local.output_path / "OUTPUT_FILES"
    if output_path.exists():
        shutil.rmtree(output_path)
    shutil.copytree(ws.work_path / local.initial_model_output, output_path)


if __name__ == "__main__":
    ws = local.get_workspace()
    refresh_output()

    # get misfit and plot
    misfit_wf = WaveformMisFit(
        ws.work_path / local.true_model_output,
        ws.work_path / local.initial_model_output,
    )

    misfit_wf.plot()

    # misfit_wf.calc_misfit()
    # adj = misfit_wf.calc_misfit()
    # Run adjoint
    # out = ws.run_adjoint(misfit_wf, "OUTPUT_FILES_ADJ_WF")

    # --- plot kernel
    keeper = KernelKeeper(ws.work_path / "OUTPUT_FILES_ADJ_WF")
    fig, _ = keeper.plot()
    plt.tight_layout()
    breakpoint()
