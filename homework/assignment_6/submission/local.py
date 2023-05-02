"""
Project for reproducing tromp et al., 2005 figures
"""
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import numpy as np
import obspy

# setup paths
here = Path(__file__).absolute().parent
input_path = here / Path("inputs")
output_path = here / Path("outputs")
output_path.mkdir(exist_ok=True)

tt_diff_path = input_path / "measure_vec.dat"

design_matrix_path = output_path / "G.npy"  # output for design matrix

damped_delta_m_path = output_path / "damped_delta_m.pkl"

spline_sensitivity_path = output_path / "spline_sensitivity.npy"

velocity_change_directory = output_path / "a050_velocity_change_plots"
velocity_change_directory.mkdir(exist_ok=True, parents=True)

damped_delta_m_reduced_path = output_path / "damped_delta_reduced_m.pkl"

velocity_change_reduced_directory = output_path / "a070_velocity_change_reduced_plots"
velocity_change_reduced_directory.mkdir(exist_ok=True, parents=True)

map_extents = [-121, -114, 31, 37]
spline_order = 8


@dataclass
class LoadedData:
    slats: np.ndarray
    slons: np.ndarray

    rlats: np.ndarray
    rlons: np.ndarray

    qlats: np.ndarray
    qlons: np.ndarray

    @property
    def nsrc(self):
        return len(self.slons)

    @property
    def nrec(self):
        return len(self.rlons)

    @property
    def nspline(self):
        return len(self.qlats)


@cache
def get_map_coords(numx=100, numy=100):
    """Get labels for latitude/longitude"""
    lons = np.linspace(map_extents[0], map_extents[1], numx)
    lats = np.linspace(map_extents[2], map_extents[3], numy)
    return lats, lons


@cache
def get_map_coords_grid():
    """Get grid coords for latitude/longitude"""
    lats, lons = get_map_coords()
    lonplot, latplot = np.meshgrid(lons, lats)
    return latplot, lonplot


def load_data():
    data_path = Path("inputs")
    slons, slats, _ = np.loadtxt(
        data_path / "events_lonlat.dat", skiprows=1, unpack=True
    )

    # load receivers
    rlons, rlats, _ = np.loadtxt(data_path / "recs_lonlat.dat", skiprows=1, unpack=True)

    # load spline centers
    qlons, qlats = np.loadtxt(data_path / "con_lonlat_q08.dat", unpack=True)

    return LoadedData(
        slons=slons,
        slats=slats,
        rlons=rlons,
        rlats=rlats,
        qlons=qlons,
        qlats=qlats,
    )
