"""
Create and plot as single station/event kernel.
"""
from pathlib import Path

import matplotlib.pyplot as plt

import local

if __name__ == "__main__":
    import specster as sp
    from specster.fwi.misfit import WaveformMisFit


    # true_path = local.single_single_kernel_true_path
    #
    # control_true = sp.load_2d_example("homogeneous_2d").copy(true_path)
    #
    #
    # control_true.stations = control_true.stations[:1]
    # control_true.prepare_fwi_forward().write(overwrite=True)
    #
    # fig, _ = control_true.plot_geometry(kernel='vp')
    # fig.savefig(local.sing_single_geometry_path)
    #
    # control_true.run()
    #
    # control_initial = control_true.copy(local.single_single_kernel_initial_path)
    # control_initial.par.material_models.models[0].Vs *= 0.98
    # control_initial.prepare_fwi_forward().write(overwrite=True)
    # control_initial.run()
    #
    # # load seismograms as Streams
    # st_true = control_true.output.get_waveforms()
    # st_initial = control_initial.output.get_waveforms()
    #
    # # calculate adjoint source
    # misfitter = WaveformMisFit(st_true, st_initial)
    # adjoint_source = misfitter.get_adjoint_sources()
    # adjoint_source.plot(outfile=local.adjoint_plot_path, show=False)
    #
    # # write adjoints to initial and run
    # control_initial.write_adjoint_sources(adjoint_source)
    # control_initial.prepare_fwi_adjoint()
    # control_initial.run()
    #
    #
    # #
    control_initial = sp.Control2d(local.single_single_kernel_initial_path)
    output = control_initial.output
    fig, *_ = output.plot_kernel(kernel='beta')
    fig.savefig(local.sing_sing_banana_donut)


