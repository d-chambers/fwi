"""
Module for computing G_{ik}.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from raytape.spline import spline_vals
from raytape.utils import get_distance, get_distances, get_waypoints


def _get_ray_points(slats, slons, rlats, rlons, npts):
    """
    Get the points between sources and receivers.

    Output dimensions are (source X receiver, point, lat/lon)
    """
    size = (len(slats) * len(rlats), npts, 2)
    out = np.ones(size) * np.NAN
    for snum, (slat, slon) in enumerate(zip(slats, slons)):
        for rnum, (rlat, rlon) in enumerate(zip(rlats, rlons)):
            pts = get_waypoints((slat, slon), (rlat, rlon), npts)
            i = snum * len(rlats) + rnum
            out[i, :, :] = pts
    assert not np.isnan(out).any()
    return out


def calc_G(
    slats, slons, rlats, rlons, qlats, qlons, velocity, npts=1000, scale=8
) -> pd.DataFrame:
    """Calculate the design matrix G."""
    assert len(slats) == len(slons)
    assert len(rlats) == len(rlons)
    assert len(qlats) == len(qlons)

    nsources, nreceivers = len(slats), len(rlats)
    nsplines = len(qlats)

    velocity = np.broadcast_to(velocity, qlats.shape)

    way_points = _get_ray_points(slats, slons, rlats, rlons, npts)
    wp_flat = way_points.reshape(-1, 2)
    distances = get_distances(
        way_points[:, 0, 0],
        way_points[:, 0, 1],
        way_points[:, -1, 0],
        way_points[:, -1, 1],
    )[:, None]
    ray_distances = distances / npts

    out = np.empty((nsources * nreceivers, nsplines)) * np.NAN

    # because spline_vals is expensive, calculate it once for each
    # spline for all ray paths.
    for sp_num, (qlat, qlon) in enumerate(zip(qlats, qlons)):
        svals = spline_vals(qlon, qlat, scale, wp_flat[:, 1], wp_flat[:, 0], 1).reshape(
            -1, npts
        )
        out[:, sp_num] = np.sum(svals * (ray_distances / velocity[sp_num]), axis=1)
    assert not np.isnan(out).any()
    df = pd.DataFrame(out, columns=range(out.shape[1]), index=range(out.shape[0]))
    return df
