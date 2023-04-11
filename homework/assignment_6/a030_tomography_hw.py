"""
Script for running
"""
from pathlib import Path

import numpy as np
from raytape import spline_vals


if __name__ == "__main__":
    ax1 = [-121, -114, 31, 37]  # lon-lat plotting dimensions

    # load sources
    data_path = Path('inputs')
    slons, slats, _ = np.loadtxt(data_path / 'events_lonlat.dat', skiprows=1, unpack=True)

    # load receivers
    rlons, rlats, _ = np.loadtxt(data_path / 'recs_lonlat.dat', skiprows=1, unpack=True)

    # load spline centers
    qlons, qlats = np.loadtxt(data_path / 'con_lonlat_q08.dat', unpack=True)

    # load observed data
    data = np.loadtxt(data_path / "measure_vec.dat", unpack=True)

    # load G
    design_matrix = np.load("outputs/G.npy")

    GtG = design_matrix.T @ design_matrix
    Gtd = design_matrix.T @ data
    breakpoint()
    delta_m = np.linalg.inv(GtG) @ Gtd
    breakpoint()

    # LOAD DATA
    breakpoint()

    # load sources
    slon, slat, sind = np.loadtxt('events_lonlat.dat', unpack=True, skiprows=1)

    nsrc = len(slat)

    # load receivers
    rlon, rlat, rind = np.loadtxt('recs_lonlat.dat', unpack=True, skiprows=1)

    nrec = len(rlat)

    # load spline centers
    qlon, qlat = np.loadtxt('con_lonlat_q08.dat', unpack=True, skiprows=0)

    # load recorded data
    data = np.loadtxt()

    nspline = len(qlat)

    # =======================================================================
    # lon-lat gridpoints for plotting

    numx = 100

    lonplot, latplot = np.meshgrid(np.linspace(ax1[0], ax1[1], numx), np.linspace(ax1[2], ax1[3], numx))

    nplot = lonplot.size

    # Compute design matrix for expanding a function in terms of splines;
    # this is needed to view the tomographic models that we generate at the end.
    B = np.zeros((nplot, nspline))

    for ii in range(nspline):
        ff = spline_vals(qlon[ii], qlat[ii], q, lonplot, latplot, {1})
        B[:, ii] = ff.ravel()

    # -----------------------------------------
    # INVERSE PROBLEM HERE


    # ======================================================
