"""
Examples of modifying the control.
"""
import shutil
from pathlib import Path

import local
import matplotlib.pyplot as plt
import specster as sp

if __name__ == "__main__":
    import numpy as np
    import specster as sp

    control = sp.Control2d().copy()
    # get current material properties as a dataframe.
    # index is x/z coordinates and columns are material values.
    df = control.get_material_model_df()
    # get coords of each gll point and location of center
    coords = df.reset_index()[["x", "z"]].values
    center = np.mean(coords, axis=0)
    # find points which are within 500m of center
    distances = np.linalg.norm(coords - center, axis=1)
    in_distance = np.abs(distances) < 500
    # update P/S velocities by making points in distance 50% slower
    new_vp = df["vp"].values
    new_vp[in_distance] *= 0.5
    df["vp"] = new_vp
    # now set model and plot
    control.set_material_model_df(df)

    fig, ax = control.plot_geometry(kernel=("vp", "vs"))
    fig.savefig(local.material_df_modified_path, bbox_inches="tight", pad_inches=0)
