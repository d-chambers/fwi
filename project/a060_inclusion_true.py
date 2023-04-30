"""
Create and plot as single station/event kernel.
"""
from pathlib import Path


import matplotlib.pyplot as plt
import specster as sp

import local

if __name__ == "__main__":
    control = sp.load_2d_example("inclusion_2d").copy(local.inclusion_2d_true_path)
    fig, *_ = control.plot_geometry(kernel='vs')

    fig.savefig(local.inclusion_true_geometry_path, bbox_inches='tight', pad_inches=0)

    control.run_each_source()

