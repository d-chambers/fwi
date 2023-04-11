"""
Plot the inverted velocities.
"""

import pickle
import numpy as np

from raytape.viz import plot_velocity_changes
import local

if __name__ == "__main__":
    with open(local.damped_delta_m_path, 'rb') as fi:
        delta_m = pickle.load(fi)

    sensitivity = np.load(local.spline_sensitivity_path)
    lats, lons = local.get_map_coords()

    for lam, ar in delta_m.items():
        vel_by_spline = ar[None, None, :] * sensitivity
        vel = np.sum(vel_by_spline, axis=-1)
        fig, ax = plot_velocity_changes(lats, lons, vel, clim=[-0.1, 0.1])
        ax.set_title(f"$\lambda={lam:.02f}$")
        out_path = local.velocity_change_directory / f"lambda={lam:.02f}.png"
        fig.savefig(out_path)


