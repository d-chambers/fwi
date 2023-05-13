"""
Create a split of the inclusion with homogeneous velocity.
"""
from pathlib import Path

import local
import matplotlib.pyplot as plt
import specster as sp

if __name__ == "__main__":
    control_initial = (
        sp.load_2d_example("inclusion_2d")
        .copy(local.inclusion_2d_initial_path)
        .prepare_fwi_forward()
    )
    local.create_initial_model(control_initial)

    fig, *_ = control_initial.plot_geometry(kernel="vs", overwrite=True)

    fig.savefig(
        local.inclusion_initial_geometry_path, bbox_inches="tight", pad_inches=0
    )
    control_initial.run_each_source()
