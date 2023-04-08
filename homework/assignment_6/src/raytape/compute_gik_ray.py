"""
Module for computing G_{ik}.
"""
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from raytape.utils import get_waypoints
from raytape.spline import spline_vals


def plot_center_spline_points(qlats, qlons):
    """Visualize the center points for spline functions."""
    fig, ax = plt.subplots(1, 1)
    ax.plot(qlons, qlats, '.')
    for i in range(nspline):
        plt.text(qlons[i], qlats[i], str(i + 1), fontsize=6)
    ax.set_aspect('equal')
    ax.set_xlabel(' Longitude')
    ax.set_ylabel(' Latitude')
    ax.set_title(' Center-points of spherical spline basis functions')
    return fig, ax


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


def calc_G(slats, slons, rlats, rlons, qlats, qlons, velocity, npts=1000, scale=8):
    """Calculate the design matrix G."""
    assert len(slats) == len(slons)
    assert len(rlats) == len(rlons)
    assert len(qlats) == len(qlons)

    nsources, nreceivers = len(slats), len(rlats)
    nsplines = len(qlats)

    velocity = np.broadcast_to(velocity, qlats.shape)

    way_points = _get_ray_points(slats, slons, rlats, rlons, npts)

    out = np.empty((nsources * nreceivers, nsplines))
    for i, wpt in enumerate(way_points):
        for sp_num, (qlat, qlon) in enumerate(zip(qlats, qlons)):
            svals = spline_vals(qlon, qlat, scale, wpt[:, 1], wpt[:, 0], 1)
            out[i, sp_num] = np.sum(svals / velocity[sp_num])
            print(i, sp_num)

    breakpoint()
    #
    #
    # # test the ordering scheme for the rows of G
    # print('     i   isrc  irec ')
    # for isrc, (slat, slon) in enumerate(zip(slats, slons)):
    #     for irec, (rlat, rlon) in range(zip(rlats, rlons)):
    #         for qlat, qlon in zip(qlats, qlons):
    #
    #
    #
    #         i = isrc * nrec + irec
    #         print('{:6d}{:6d}{:6d}'.format(i, isrc, irec))
    #


if __name__ == "__main__":
    # load sources
    data_path = Path(__file__).parent / 'data'
    slons, slats, _ = np.loadtxt(data_path / 'events_lonlat.dat', skiprows=1, unpack=True)
    nsrc = len(slats)

    # load receivers
    rlons, rlats, _ = np.loadtxt(data_path / 'recs_lonlat.dat', skiprows=1, unpack=True)
    nrec = len(rlats)

    # load spline centers
    qlons, qlats = np.loadtxt(data_path / 'con_lonlat_q08.dat', unpack=True)
    nspline = len(qlats)

    # THIS MAY BE DIFFERENT FROM ONE MODEL TO THE NEXT
    velocity = 3500

    out = calc_G(
        slats, slons, rlats, rlons, qlats, qlons, velocity,
        npts=1000, scale=8,
    )

    breakpoint()

    # -----------------------------
    # compute ray paths (great circles)

    # spline evaluations
    columns = 1
    order = 8

    # number of points along each ray path
    nump = 1000

    # test the ordering scheme for the rows of G
    print('     i   isrc  irec ')
    for isrc in range(nsrc):
        for irec in range(nrec):
            i = isrc * nrec + irec
            print('{:6d}{:6d}{:6d}'.format(i, isrc, irec))

    # compute design matrix
    # TODO

    # save design matrix
    # np.save('Amat_ray.npy', Amat_ray)
