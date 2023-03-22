"""
Generate the model geometry figure.
"""
import matplotlib.pyplot as plt

import specster

import local


if __name__ == "__main__":
    fig, ax = plt.subplots(1, 1)
    sta = local.station_location
    source = local.source_location

    ax.scatter(source[0], source[1], 1000, marker="*", color="black", edgecolor="white")
    ax.scatter(sta[0], sta[1], 450, marker="v", color="black", edgecolor="white")
    ax.set_xlim(*local.x_lims)
    ax.set_ylim(*local.z_lims)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_title("Model Geometry")
    plt.savefig(local.model_geometry)

