"""
Create and plot as single station/event kernel.
"""

import local
import specster as sp

if __name__ == "__main__":
    control = sp.load_2d_example("inclusion_2d").copy(local.inclusion_2d_true_path)
    fig, *_ = control.plot_geometry(kernel="vs")

    fig.savefig(local.inclusion_true_geometry_path, bbox_inches="tight", pad_inches=0)

    control.run_each_source()
