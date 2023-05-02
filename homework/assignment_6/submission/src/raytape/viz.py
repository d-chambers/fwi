"""
Visualization module.
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_center_spline_points(qlats, qlons):
    """Visualize the center points for spline functions."""
    fig, ax = plt.subplots(1, 1)
    ax.plot(qlons, qlats, ".")
    for i in range(len(qlats)):
        plt.text(qlons[i], qlats[i], str(i + 1), fontsize=6)
    ax.set_aspect("equal")
    ax.set_xlabel(" Longitude")
    ax.set_ylabel(" Latitude")
    ax.set_title(" Center-points of spherical spline basis functions")
    return fig, ax


def plot_velocity_changes(lats, lons, velocity_change, clim=None):
    """Plot the change in velocity."""
    fig, ax = plt.subplots(1, 1)

    # Plot the map using imshow and set extent
    im = ax.imshow(
        velocity_change, cmap="viridis", extent=[lons[0], lons[1], lats[0], lats[1]]
    )
    im.set_clim(clim)
    # Add a colorbar to show the values represented by the colors in the plot
    cbar = fig.colorbar(im, ax=ax)

    # Set the title and axis labels
    ax.set_title("Map Example")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    return fig, ax


def plot_design_matrix(qlats, qlons, slats, slons, rlats, rlons, ar, index=0):
    """Plot an index of the design matrix."""
    # create figure and axes
    fig, ax = plt.subplots(1, 1)
    # get indices
    rind = index % len(rlats)
    sind = index // len(rlats)
    # plot raypath
    ax.plot([slons[sind], rlons[rind]], [slats[sind], rlats[rind]])
    # get colors (0 to 1
    color = ar[index, :] / np.max(ar[index, :])
    # ax.plot(qlons, qlats, '.')
    ax.scatter(qlons, qlats, c=color, alpha=0.95, cmap=plt.cm.get_cmap("binary"))

    ax.plot(slons[sind], slats[sind], "*")
    ax.plot(rlons[rind], rlats[rind], "^")

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(f"Index: {index}")

    return fig, ax
