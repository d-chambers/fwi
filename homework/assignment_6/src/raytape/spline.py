"""
Module for computing the spline values.
"""
import numpy as np


def spline_vals(clon, clat, scale, lon_vec, lat_vec, cols):
    """
    Given a spline gridpoint, this returns the value of the spline
    at all the input datapoints.

    Parameters
    ----------
    clon
        The longitude of the gridpoint
    clat
        The latitude of the gridpoint
    scale
        The scale of the spline (0-10)
    lon_vec
        The longitudes of the datapoints
    lat_vec
        The latitudes of the datapoints
    cols
        The number of columns of ff to return.
        Columns 1-5 correspond to:
            'f', 'df/d phi', 'df/d theta', 'laplacian(f)', '|grad(f)|'

    Returns
    -------
    value of the spline function (and derivatives) evaluated at
    the specified lon-lat points.

    """
    lon_vec, lat_vec = np.array(lon_vec), np.array(lat_vec)
    # convert to theta-phi
    deg = 180 / np.pi
    ph = clon / deg
    th = (90 - clat) / deg
    ph_vec = lon_vec / deg
    th_vec = (90 - lat_vec) / deg

    # options and parameters -- q controls the scale (width) of the spline
    nf = 2 ** scale
    c72 = np.cos(72 / deg)
    base = np.arccos(c72 / (1 - c72))
    db = base / nf
    zeps = 1e-3 * base  # determines whether a datapoint is ON a gridpoint

    # datapoint locations
    costh = np.cos(th_vec)
    sinth = np.sin(th_vec)
    ndata = len(th_vec)

    # r : delta/delta-bar in WD95
    del_ = np.arccos(
        np.cos(th) * costh + np.sin(th) * sinth * np.cos(ph - ph_vec)
    )
    r = del_ / db
    dif = r - 1

    # separate r into three parts: assign each element to one of four regions
    inds1 = np.where(dif > 1)[0]  # outside outer circle
    inds2 = np.where((dif <= 1) & (dif >= 0))[0]  # within outer ring
    inds3 = np.where((dif > -1 + zeps) & (dif < 0))[0]  # within inner circle
    inds4 = np.where(dif <= -1 + zeps)[0]  # ON the center point

    ind_list = (len(x) for x in [inds1, inds2, inds3, inds4])
    # check
    if sum(ind_list) != len(dif):
        raise ValueError("datapoints have not been partitioned properly")

    ff = np.zeros((ndata, cols))

    if cols == 1:
        part1 = (-0.25 * dif[inds2] + 0.75) * dif[inds2] - 0.75
        ff[inds2, 0] = (part1 * dif[inds2] + 0.25)
        sub1 = 0.75 * r[inds3] - 1.5
        ff[inds3, 0] = sub1 * r[inds3] ** 2 + 1
        ff[inds4, 0] = 1

    else:
        cosdel = np.cos(th) * costh + np.sin(th) * sinth * np.cos(ph - ph_vec)
        sindel = np.sqrt(1 - cosdel ** 2)
        cotdel = cosdel / sindel

        # delta: arc-distance from test-point to gridpoints
        # adist = np.arccos(cosdel)

        # ddelta/dphi and ddelta/dtheta (see MMA file wang_arc.nb)
        dadp = (np.sin(th) * sinth * np.sin(ph_vec - ph)) / sindel
        dadt = (
                       np.cos(th) * sinth - costh * np.sin(th) * np.cos(ph - ph_vec)
               ) / sindel

        # db : delta-bar in WD95
        # d_near varies for each gridpoint, due to irregularities in grids
        dq = 1 / db
        # datapoint is outside the outer circle

        # datapoint is within the outer ring
        ff[inds2, 0] = ((-0.25 * dif[inds2] + 0.75) * dif[inds2] - 0.75) * dif[inds2] + 0.25
        ff[inds2, 1] = dq * (-0.75 + 1.5 * dif[inds2] - 0.75 * dif[inds2] ** 2) * dadp[inds2]
        ff[inds2, 2] = dq * (-0.75 + 1.5 * dif[inds2] - 0.75 * dif[inds2] ** 2) * dadt[inds2]
        if cols >= 4:
            sub1 = (-0.75 + 1.5 * dif[inds2] - 0.75 * dif[inds2] ** 2)
            ff[inds2, 3] = dq * (3 - 1.5 * r[inds2] + cotdel[inds2] * sub1)
            ff[inds2, 4] = 0.75 * db ** -3 * (2 * db - del_[inds2]) ** 2

            # datapoint is within the inner circle
        ff[inds3, 0] = (0.75 * r[inds3] - 1.5) * (r[inds3] ** 2) + 1
        ff[inds3, 1] = dq * (-3 * r[inds3] + 2.25 * r[inds3] ** 2) * dadp[inds3]
        ff[inds3, 2] = dq * (-3 * r[inds3] + 2.25 * r[inds3] ** 2) * dadt[inds3]
        if cols >= 4:
            ff[inds3, 3] = dq * (-3 + 4.5 * r[inds3] + cotdel[inds3] * (-3 * r[inds3] + 2.25 * r[inds3] ** 2))
            ff[inds3, 4] = 0.75 * db ** -3 * (4 * db - 3 * del_[inds3]) * del_[inds3]

        # datapoint is in the vicinity of the target spline centerpoint
        # FIX THIS: see Wang & Dahlen (1995)
        # here we simply assign it the closest value
        if len(inds4) > 0:
            if cols > 3:
                igood = np.where(dif > -1 + zeps)[0]
                imin = np.argmin(r[igood])
                d2val = ff[imin, 3]
                tvec = np.zeros(cols)
                tvec[0] = 1
                tvec[-1] = d2val
                ff[inds4, 0:cols] = np.tile(tvec, (len(inds4), 1))
            elif cols == 3:
                ff[inds4, 0:3] = np.array([1, 0, 0])
            elif cols == 1:
                ff[inds4, 0] = 1

    return ff
