"""
Script for running
"""
import pickle
from pathlib import Path

import local
import numpy as np
from raytape import spline_vals

if __name__ == "__main__":
    # load observed data
    measured = np.loadtxt(local.tt_diff_path, unpack=True)

    # load G
    design_matrix = np.load(local.design_matrix_path)

    # setup inversion for different damping parameters
    GtG = design_matrix.T @ design_matrix
    Gtd = design_matrix.T @ measured

    # find
    out = {}
    lambdas = 10 ** (np.linspace(np.log10(0.1), np.log10(40.0), 6))
    for lam in lambdas:
        inv = np.linalg.inv(GtG + np.eye(len(Gtd)) * lam**2)
        delta_m = inv @ Gtd
        out[lam] = delta_m

    with open(local.damped_delta_m_path, "wb") as fi:
        pickle.dump(out, fi)
