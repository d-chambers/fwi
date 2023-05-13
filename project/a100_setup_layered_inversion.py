"""
Setup-up a layered inversion.
"""

import specster as sp
from specster.d2.io.parfile import Source

import local
#
def add_sources(control):
    """Add sources to control."""
    out = []
    coords = [
        (1000, 2500),
        (1000, 1000),
        (2000, 2500),
        (3000, 2500),
        (3000, 500),
        (3200, 1600),
        (3700, 1550),
        (3700, 550),
        (3700, 550),
        (3700, 2550),
        (2000, 1500),
        (2500, 1500),
    ]
    for (xs, zs) in coords:
        new = Source(
            xs=xs,
            zs=zs,
            mxx=1,
            mzz=1,
            mxz=0,
            source_type="2",
            time_function_type="1",
            f0=7,
        )
        out.append(new)
    control.sources = out
    return control


if __name__ == "__main__":
    true_cont = sp.Control2d().copy(local.layered_true_path)
    add_sources(true_cont)
    true_cont.par.visualizations.postscript.output_postscript_snapshot = False
    true_cont.par.nstep = 2000
    true_cont.write(overwrite=True)
    true_cont.run_each_source()

    true_cont.prepare_fwi_forward().run()

    init_cont = true_cont.copy(local.layered_initial_path)
    init_cont.regions[3].material_number = 2
    init_cont.write(overwrite=True)
    init_cont.run_each_source()
