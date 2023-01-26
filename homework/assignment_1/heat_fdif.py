"""
Finite difference solutions to the heat equation.
"""
import dataclasses
from functools import cached_property
from typing import Union, Dict, List, Callable, Literal, Optional

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
import pandas as pd


@dataclasses.dataclass
class Simulation1D:
    """
    Finite difference 1D geometry and results.

    Defines input parameters for evenly sampled grids.

    Parameters
    ----------
    x_min
        The min value of the x grid.
    x_max
        The max value of the x grid.
    dx
        The step size on x axis.
    time_min
        The minimum time value.
    time_max
        The max time values.
    dt
        The time step.
    bc_func
        A callable which takes the output of the simulation at each time
        step and enforces boundary conditions.
    initial_func
        Callable which takes the x array and returns initial conditions.
    times_to_save
        A list of dt values to save as snap shots. Can also be a literal
        string "all" to save all output.
    """
    # x coordinate definitions
    x_min: float
    x_max: float
    dx: float
    # y coordinate definitions
    time_min: float
    time_max: float
    dt: float
    # other inputs
    bc_func: Optional[Callable] = None
    initial_func: Optional[callable] = None
    times_to_save: Union[List[float], Literal['all']] = 'all'
    # outputs defined by solvers
    # results_: Optional[pd.DataFrame]

    def __post_init__(self):
        # init a temporary cache for storing intermediate outcomes.
        self._temp_cache = {}

    @cached_property
    def x_grid(self):
        """Return the spatial coordinates of the simulation."""
        x_grid = np.arange(self.x_min, self.x_max + self.dx, self.dx)
        return x_grid

    @cached_property
    def t_grid(self):
        """Return the time coordinates of the simulation."""
        t_grid = np.arange(self.time_min, self.time_max + self.dt, self.dt)
        return t_grid

    @property
    def results_(self):
        """Get the results stored so far, clear intermediate cache."""
        results = pd.DataFrame(self._temp_cache)
        results.columns.name = 't'
        results.index.name = 'x'
        self._temp_cache = {}
        return results

    def apply_boundary_conditions(self, array):
        """Apply boundary conditions after time step."""
        if self.bc_func is not None:
            array = self.bc_func(array)
        return array

    def get_initial_values(self):
        """Get the values at the first timestep (t=tmin)"""
        x_vals = self.x_grid
        if self.initial_func is not None:
            return self.initial_func(x_vals)
        return np.zeros_like(x_vals)

    def maybe_store_results(self, time, results):
        """Maybe store the results is specified by times_to_save."""
        save_all = self.times_to_save == 'all'
        if save_all or time in self.times_to_save:
            self._temp_cache[time] = results


def moving_window(ar, stencil, zero_edge_effects=True):
    """Apply the convolution on array."""
    # need to time reverse stencil
    out = np.convolve(ar, stencil[::-1], mode='same')
    # zero edges
    if zero_edge_effects:
        end_in = len(stencil) // 2
        out[:end_in] = 0
        out[-end_in:] = 0
    return out


def heat_ftcs(
        sim: Simulation1D,
        density=1.0,
        specific_heat=1.0,
        thermal_conductivity=1.0,
) -> pd.DataFrame:
    """
    Run 1D finite difference heat equation.

    Simply uses forward difference in time and central difference in space.

    Parameters
    ----------
    sim
        The simulation parameters.
    density
        The density in kg/m^3
    specific_heat
        The specific heat in J/(kg K)
    thermal_conductivity
        The thermal conductivity in W / (K m)
    """
    # Get initial values.
    x_vals, t_vals = sim.x_grid, sim.t_grid
    dt, dx = sim.dt, sim.dx
    temp_current = sim.get_initial_values()
    thermal = np.broadcast_to(thermal_conductivity, np.shape(temp_current))
    # since thermal conductivity cant change with time, just calc once.
    dk_dx = moving_window(thermal, [-1, 0, 1])
    diffusivity = thermal / (density * specific_heat)
    # coefficient multiplying A
    coef_A = diffusivity * (dt / dx**2)
    coef_B = dk_dx * (dt / (4 * dx**2 * density * specific_heat))
    # Run simulation.
    for time in t_vals:
        sim.maybe_store_results(time, temp_current)
        dT_dx2 = moving_window(temp_current, [1, -2, 1])
        dT_dx = moving_window(temp_current, [-1, 0, 1])
        temp_next = temp_current + coef_A * dT_dx2 + coef_B * dT_dx
        temp_current = temp_next
    return sim.results_


def make_A(C, x_vals):
    """Makes the A matrix which needs to be inverted."""
    if np.shape(C):
        C = C.flat[0]
    out = np.zeros((len(x_vals), len(x_vals)))
    center = np.arange(len(x_vals))
    # Fill in diags
    out[center, center] = 2*C + 1
    # now off diags
    out[center[:-1], center[1:]] = -C
    out[center[1:], center[:-1]] = -C
    return out 

def make_D(C, x_vals):
    """Makes the A matrix which needs to be inverted."""
    if np.shape(C):
        C = C.flat[0]
    out = np.zeros((len(x_vals), len(x_vals)))
    center = np.arange(len(x_vals))
    # Fill in diags
    out[center, center] = 1 + C
    # now off diags
    out[center[:-1], center[1:]] = -C/2
    out[center[1:], center[:-1]] = -C/2
    return out 

def make_E(C, x_vals):
    """Makes the A matrix which needs to be inverted."""
    if np.shape(C):
        C = C.flat[0]
    out = np.zeros((len(x_vals), len(x_vals)))
    center = np.arange(len(x_vals))
    # Fill in diags
    out[center, center] = 1 - C
    # now off diags
    out[center[:-1], center[1:]] = C/2
    out[center[1:], center[:-1]] = C/2
    return out 


def heat_btcs(
        sim: Simulation1D,
        density=1.0,
        specific_heat=1.0,
        thermal_conductivity=1.0,
) -> pd.DataFrame:
    """
    Run 1D finite difference heat equation.

    Uses the implicit scheme with backward time central difference in space.

    Parameters
    ----------
    sim
        The simulation parameters.
    density
        The density in kg/m^3
    specific_heat
        The specific heat in J/(kg K)
    thermal_conductivity
        The thermal conductivity in W / (K m)
    """
    # Get initial values.
    x_vals, t_vals = sim.x_grid, sim.t_grid
    dt, dx = sim.dt, sim.dx
    temp_current = sim.get_initial_values()
    thermal = np.broadcast_to(thermal_conductivity, np.shape(temp_current))
    diffusivity = thermal / (density * specific_heat)
    C = (diffusivity * dt) / (dx ** 2)
    A = make_A(C, x_vals)
    A_inv = np.linalg.inv(A)
    # Run simulation.
    for time in t_vals:
        sim.maybe_store_results(time, temp_current)
        temp_next = A_inv @ temp_current
        temp_current = temp_next
    return sim.results_


def heat_crank_nicolson(
        sim: Simulation1D,
        density=1.0,
        specific_heat=1.0,
        thermal_conductivity=1.0,
) -> pd.DataFrame:
    """
    Run 1D finite difference heat equation.

    Uses the implicit scheme with backward time central difference in space.

    Parameters
    ----------
    sim
        The simulation parameters.
    density
        The density in kg/m^3
    specific_heat
        The specific heat in J/(kg K)
    thermal_conductivity
        The thermal conductivity in W / (K m)
    """
    # Get initial values.
    x_vals, t_vals = sim.x_grid, sim.t_grid
    dt, dx = sim.dt, sim.dx
    temp_current = sim.get_initial_values()
    thermal = np.broadcast_to(thermal_conductivity, np.shape(temp_current))
    diffusivity = thermal / (density * specific_heat)
    C = (diffusivity * dt) / (dx ** 2)
    D = make_D(C, x_vals)
    E = make_E(C, x_vals)
    D_inv_E = np.linalg.inv(D) @ E
    # Run simulation.
    for time in t_vals:
        sim.maybe_store_results(time, temp_current)
        temp_next = D_inv_E @ temp_current
        temp_current = temp_next
    return sim.results_
