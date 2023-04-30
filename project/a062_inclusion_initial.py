"""
Create a split of the inclusion with homogeneous velocity.
"""
from pathlib import Path
import specster as sp

import matplotlib.pyplot as plt

import local

if __name__ == "__main__":
    control = (
        sp.Control2d(local.inclusion_2d_true_path)
        .copy(local.inclusion_2d_initial_path)
    )
    # set model number 2 to have the same properties as mod 1
    # this homogenises the model
    models = control.par.material_models.models
    models[1].Vs = models[0].Vs
    models[1].Vp = models[0].Vp
    models[1].rho = models[0].rho

    control.write(overwrite=True)
    fig, *_ = control.plot_geometry(kernel='vs', overwrite=True)

    fig.savefig(local.inclusion_initial_geometry_path, bbox_inches='tight', pad_inches=0)
    breakpoint()
    control.run_each_source()
