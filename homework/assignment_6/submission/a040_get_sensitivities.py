"""
Script to compute spline sensitivities for each plotting point.
"""
import pickle

import numpy as np

import local
from raytape import spline_vals


def compute_spline_sensitivity(data):
    lats, lons = local.get_map_coords_grid()
    shape = np.shape(lats)

    # Compute design matrix for expanding a function in terms of splines;
    # this is needed to view the tomographic models that we generate at the end.
    B = np.zeros(list(shape) + [data.nspline])

    for ii in range(data.nspline):
        ff = spline_vals(
            data.qlons[ii], data.qlats[ii], local.spline_order, lons.flatten(), lats.flatten(), 1)
        B[:, :, ii] = ff[:, 0].reshape(shape)
    return B


if __name__ == "__main__":
    data = local.load_data()
    # load observed data
    with open(local.damped_delta_m_path, 'rb') as fi:
        damped_delta_m = pickle.load(fi)

    spline_sense = compute_spline_sensitivity(data)
    np.save(local.spline_sensitivity_path, spline_sense)
