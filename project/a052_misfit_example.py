"""Module for making example plot of waveform misfit and adjoint source."""
from pathlib import Path

import local
import matplotlib.pyplot as plt

if __name__ == "__main__":
    import specster as sp
    from specster.fwi.misfit import WaveformMisfit

    control_true = sp.Control2d(local.single_single_kernel_true_path)
    control_initial = control_true.copy(local.single_single_kernel_initial_path)
    control_initial.par.material_models.models[0].Vs *= 0.98
    control_initial.prepare_fwi_forward().write(overwrite=True)
    control_initial.run()

    # load seismograms as Streams
    st_true = control_true.output.get_waveforms()
    st_initial = control_initial.output.get_waveforms()

    # calculate adjoint source
    misfitter = WaveformMisfit()
    fig, (ax1, ax2) = misfitter.plot(st_true, st_initial)
    fig.savefig(local.adjoint_misfit_plot_path)
