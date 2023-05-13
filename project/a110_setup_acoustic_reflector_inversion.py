"""
Setup-up a layered inversion.
"""

import specster as sp
from specster.d2.io.parfile import Source

import matplotlib.pyplot as plt

import local
#

if __name__ == "__main__":
    true_cont = sp.load_2d_example("acoustic_reflector").copy(local.acoustic_reflector_true_path)
    true_cont.par.visualizations.postscript.output_postscript_snapshot = False
    true_cont.par.nstep = 2200
    true_cont.write(overwrite=True)
    true_cont.run_each_source()
    true_cont.prepare_fwi_forward().run()

    fig, *_ = true_cont.plot_geometry(kernel=('vp',))
    fig.savefig(local.acoustic_reflector_true_path / "geometry.png")

    init_cont = sp.load_2d_example("acoustic_reflector").copy(local.acoustic_reflector_initial_path)
    init_cont.par.visualizations.postscript.output_postscript_snapshot = False
    init_cont.par.nstep = 2200
    init_cont.regions[0].material_number = 2
    init_cont.write(overwrite=True)

    fig, *_ = init_cont.plot_geometry(kernel=('vp',))
    fig.savefig(local.acoustic_reflector_initial_path / "geometry.png")

    init_cont.prepare_fwi_forward().run()
    init_cont.run_each_source()
