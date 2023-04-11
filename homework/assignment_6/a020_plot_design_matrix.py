"""
Makes a plot of the design matrix to make sure t
"""
import random
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

import local
from raytape.viz import plot_design_matrix


if __name__ == "__main__":
    data = local.load_data()


    ar = np.load("outputs/G.npy")

    out_path = Path("outputs/ray_plots")
    out_path.mkdir(exist_ok=True, parents=True)

    # first save the figure from first ray path to use in report
    fig, ax = plot_design_matrix(data.qlats, data.qlons, data.slats, data.slons, data.rlats, data.rlons, ar, index=0)
    fig.savefig(out_path / f"example.png")

    # then save several others.
    for i in random.sample(range(data.nsrc * data.nrec), 10):
        fig, ax = plot_design_matrix(data.qlats, data.qlons, data.slats, data.slons, data.rlats, data.rlons, ar, index=i)
        fig.savefig(out_path / f"{i:04d}.png")
