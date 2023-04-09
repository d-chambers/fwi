"""
Script to compute G.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from raytape.compute_gik_ray import calc_G

if __name__ == "__main__":
    # load sources
    data_path = Path('inputs')
    slons, slats, _ = np.loadtxt(data_path / 'events_lonlat.dat', skiprows=1, unpack=True)
    nsrc = len(slats)

    # load receivers
    rlons, rlats, _ = np.loadtxt(data_path / 'recs_lonlat.dat', skiprows=1, unpack=True)
    nrec = len(rlats)

    # load spline centers
    qlons, qlats = np.loadtxt(data_path / 'con_lonlat_q08.dat', unpack=True)
    nspline = len(qlats)

    # Set the velocity. Can be a scalar or an array of shape nspline.
    velocity = 3500

    out = calc_G(
        slats, slons, rlats, rlons, qlats, qlons, velocity,
        npts=1000, scale=8,
    )
    df = pd.DataFrame(out, columns=range(out.shape[1]), index=range(out.shape[0]))
    df.to_csv("outputs/G.csv")
