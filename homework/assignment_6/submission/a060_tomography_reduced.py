"""
Script for running reduced version of the tomography problem.
"""
import pickle
from pathlib import Path

import local
import numpy as np
from raytape import spline_vals

if __name__ == "__main__":
    # load observed data
    data = local.load_data()
    measured = np.loadtxt(local.tt_diff_path, unpack=True)

    # load G
    design_matrix = np.load(local.design_matrix_path)

    # trim design matrix to only include first 5 events.
    end_index = data.nrec * 5
    design_matrix = design_matrix[:end_index, :]
    measured = measured[:end_index]

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

    with open(local.damped_delta_m_reduced_path, "wb") as fi:
        pickle.dump(out, fi)
