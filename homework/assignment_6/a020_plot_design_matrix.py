"""
Makes a plot of the design matrix to make sure t
"""
import random
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from raytape.viz import plot_design_matrix


if __name__ == "__main__":
    data_path = Path('inputs')
    slons, slats, _ = np.loadtxt(data_path / 'events_lonlat.dat', skiprows=1, unpack=True)
    nsrc = len(slats)

    # load receivers
    rlons, rlats, _ = np.loadtxt(data_path / 'recs_lonlat.dat', skiprows=1, unpack=True)
    nrec = len(rlats)

    # load spline centers
    qlons, qlats = np.loadtxt(data_path / 'con_lonlat_q08.dat', unpack=True)
    nspline = len(qlats)

    ar = np.load("outputs/G.npy")

    out_path = Path("outputs/ray_plots")
    out_path.mkdir(exist_ok=True, parents=True)

    for i in random.sample(range(nsrc * nrec), 10):
        fig, ax = plot_design_matrix(qlats, qlons, slats, slons, rlats, rlons, ar, index=i)
        fig.savefig(out_path / f"{i:04d}.png")
