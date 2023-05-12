"""
Examples of modifying the control.
"""
import shutil
from pathlib import Path

import local
import matplotlib.pyplot as plt
import specster as sp

if __name__ == "__main__":

    control = sp.Control2d().copy()
    # double the velocities in the first material
    control.par.material_models.models[3].Vp *= 2
    control.par.material_models.models[3].Vs *= 2
    control.write(overwrite=True)
    fig, ax = control.plot_geometry(kernel=("vp", "vs"))
    fig.savefig(local.material_modified_path, bbox_inches="tight", pad_inches=0)
