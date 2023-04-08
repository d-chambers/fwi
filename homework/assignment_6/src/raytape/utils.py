"""
Utils for the tape module.
"""
from functools import cache
import numpy as np

from scipy.interpolate import griddata

import pyproj


@cache
def get_geode():
    """Return a Geod object."""
    return pyproj.Geod(ellps='WGS84')


def get_waypoints(latlon_1, latlon_2, npts):
    """
    Get npts between latitude/longitude pairs.

    Parameters
    ----------
    latlon_1
        A 2D array of latitude longitude.
    latlon_2
        A 2D array of latitude longitude.
    npts
        The number of points between latlon1 and latlon2.

    Returns
    -------
    A 2D array of lat/lon values of length npts.
    """
    assert npts >= 3, "Must specify at least 3 points."
    geod = get_geode()
    lat1, lon1 = latlon_1
    lat2, lon2 = latlon_2
    # calculate line string along path with segments <= 1 km
    lonlats = geod.npts(lon1, lat1, lon2, lat2, npts - 2)
    # npts doesn't include start/end points, so prepend/append them
    lonlats.insert(0, (lon1, lat1))
    lonlats.append((lon2, lat2))
    return np.array(lonlats)[:, (1, 0)]  # order lat/lon


def grid_to_vector(x_min, x_max, x_num, y_min, y_max):
    """
    Creates a grid of points and returns the x and y coordinates as vectors.

    Spacing is set as equal in x and y directions.

    Parameters
    ----------
    x_min
        The minimum x value
    x_max
        the maximum x value
    x_num
        The number of x values
    y_min
        The minimum y value
    y_max

    Examples
    --------
    >>> xvec, yvec = grid_to_vector(0, 1, 2, 0, 1, 2)
    >>> xvec
    array([0. , 0.5, 1. , 0. , 0.5, 1. , 0. , 0.5, 1. ])
    >>> yvec
    array([0., 0., 0., 0.5, 0.5, 0.5, 1., 1., 1.])
    """
    xvec0 = np.linspace(x_min, x_max, x_num)
    dx = xvec0[1] - xvec0[0]
    yvec0 = np.arange(y_min, y_max, dx)
    X, Y = np.meshgrid(xvec0, yvec0, indexing='ij')
    xvec = X.flatten()
    yvec = Y.flatten()

    return xvec, yvec


def get_random_vector(min_value, max_value, n):
    """
    Returns a random vector of length n between min_value and max_value.

    Parameters
    ----------
    min_value
        The minimum value
    max_value
        The maximum value
    n
        The length of the vector

    Examples
    --------
    >>> min_value = 0
    >>> max_value = 1
    >>> n = 2
    >>> get_random_vector(min_value, max_value, n)
    array([0.53876639, 0.52646292])
    """
    return np.random.rand(n) * (max_value - min_value) + min_value


def grid_extrapolate(
        xvec, yvec, zvec, npts, interpolation_type='linear',
):
    """
    Interpolates data on a 2D grid.

    Parameters
    ----------
    xvec
        The x coordinates
    yvec
        The y coordinates
    zvec
        The z coordinates
    npts
        The number of points to interpolate
    interpolation_type
        The type of interpolation to use. Default is linear. Other options are
        'nearest', 'cubic', and 'quintic'.

    Notes
    -----
    griddata returns slightly different values than matlab's griddata; we just
    have to deal with it.
    """
    # Construct mesh with UNIFORM spacing in x and y directions
    xlin = np.linspace(np.min(xvec), np.max(xvec), npts)
    dx = xlin[1] - xlin[0]
    ylin = np.arange(np.min(yvec), np.max(yvec) + dx, dx)
    X, Y = np.meshgrid(xlin, ylin)

    # Interpolate data onto the grid
    points = np.column_stack((xvec, yvec))
    Z = griddata(points, zvec, (X, Y), method=interpolation_type)
    return X, Y, Z
