"""
Tests for spline_vals.py.

This is a plotting test function for spline_vals.m, which returns a
spherical spline basis function at specified lat-lon points.  It also
returns the spatial derivatives of the basis function, which are useful
for representing derivatives of target functions, as well as for
damping.

calls spline_vals.m
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata

from raytape.utils import grid_to_vector, grid_extrapolate
from raytape import spline_vals


def plot_spline(clon, clat, scale, lon, lat, ncol):
    """
    Plot a spherical spline basis function
    """
    ff = spline_vals(clon, clat, scale, lon, lat, ncol)
    X, Y, Z = grid_extrapolate(lon, lat, ff[:, 0], 100, 'cubic')
    fig, ax = plt.subplots()
    pc = ax.pcolor(X, Y, Z)
    ax.set_aspect('equal')
    ax.axis(ax1)
    fig.colorbar(pc)
    ax.set_xlabel('Longitude (deg)')
    ax.set_ylabel('Latitude (deg)')
    ax.set_title(f"Spherical spline basis function, order q={scale}, centered at lon = {clon:.2f}, lat = {clat:.2f}")
    return fig, ax




def plot_surface_gradient(clon, clat, scale, ncol, lonmin, lonmax, latmin, latmax, title):
    """A work in progress, probably not needed."""
    # create sample data

    X, Y, Z = grid_extrapolate(lon, lat, ff[:, 4])
    lon, lat = np.meshgrid(lon, lat)
    ff = spline_vals(clon, clat, scale, lon.flatten(), lat.flatten(), ncol)
    ff = np.reshape(ff, (lon.shape[0], lon.shape[1], -1))

    # plot the surface gradient
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
    ax = axs[0]
    X, Y = np.meshgrid(lon, lat)
    Z = ff[:, :, 4]
    Z_interp = griddata((lon.flatten(), lat.flatten()), Z.flatten(), (X, Y), method='cubic')
    pcm = ax.pcolormesh(X, Y, Z_interp, shading='interp')
    fig.colorbar(pcm, ax=ax, orientation='horizontal')


    ax = axs[1]
    breakpoint()
    Z = np.sqrt(ff[:, :, 2] ** 2 + ff[:, :, 3] ** 2)
    Z_interp = griddata((lon.flatten(), lat.flatten()), Z.flatten(), (X, Y), method='cubic')
    Q = ax.quiver(lon, lat, ff[:, :, 2], -ff[:, :, 3], Z_interp, cmap='coolwarm')
    fig.colorbar(Q, ax=ax, orientation='horizontal')
    ax.set_title('surface gradient vector field, along with the magnitude')
    ax.axis('equal')

    return fig


if __name__ == '__main__':

    # create sample data
    num_x = 200  # KEY COMMAND
    ax1 = [-122, -114, 32, 37]
    lonmin = ax1[0]
    lonmax = ax1[1]
    latmin = ax1[2]
    latmax = ax1[3]
    lon, lat = grid_to_vector(lonmin, lonmax, num_x, latmin, latmax)

    # select sample spline
    scale = 6  # KEY: determines the scale length of the spline (q = 0-10)
    # clat = get_random_vector(np.min(lat), np.max(lat), 1)
    # clon = get_random_vector(np.min(lon), np.max(lon), 1)

    clat = 35
    clon = -118

    fig, ax = plot_spline(clon, clat, scale, lon, lat, ncol=1)
    # Path("figures").mkdir(exist_ok=True, parents=True)
    # fig.savefig('figures/spline_test.png')

    # ----------------------------
    ncol = 5
    ff = spline_vals(clon, clat, scale, lon, lat, ncol)

    dfdp = ff[:, 1]
    dfdt = ff[:, 2]
    th = np.deg2rad(90 - lat)

    # magnitude of surface gradient of spline
    # check the computation return spline_vals.m
    dfmag = np.sqrt(dfdt ** 2 + ((1 / np.sin(th)) * dfdp) ** 2)
    np.linalg.norm(dfmag - ff[:, 4])
    new_diff = dfmag - ff[:, 4]

    d1max = max([np.max(np.abs(dfdp)), np.max(np.abs(dfdt))])

    # plot
    fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(8, 6))
    stitd = ['f', 'df/d phi', 'df/d theta', 'laplacian(f)', '|grad(f)|']

    for ii in range(len(stitd)):
        X, Y, Z = grid_extrapolate(lon, lat, ff[:, ii], 100, 'cubic')
        ax = axs.ravel()[ii]
        clim = np.array([-1, 1]) * d1max if ii in {1, 2} else None
        pcm = ax.pcolor(X, Y, Z, clim=clim)
        fig.colorbar(pcm, ax=ax)
        ax.set_title(stitd[ii])
        ax.set_aspect('equal')
        ax.axis(ax1)
    fig.tight_layout()
    axs[-1, -1].set_axis_off()
    # fig.savefig("figures/spline_test2.png")

    plt.show()
    # ------------------------------------
    # plot the surface gradient
    # fig = plot_surface_gradient(clon, clat, scale, ncol, lonmin, lonmax, latmin, latmax, title=stitd[-1])
