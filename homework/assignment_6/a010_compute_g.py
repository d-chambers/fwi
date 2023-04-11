"""
Script to compute G.
"""

import numpy as np

import local
from raytape.compute_gik_ray import calc_G

if __name__ == "__main__":
    data = local.load_data()

    # Set the velocity. Can be a scalar or an array of shape nspline.
    velocity = 3500

    out = calc_G(
        data.slats, data.slons, data.rlats, data.rlons, data.qlats, data.qlons, velocity,
        npts=1000, scale=8,
    )

    np.save("outputs/G.npy", out)
