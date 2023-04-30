"""
Create a split of the inclusion with homogeneous velocity.
"""
from pathlib import Path
import specster as sp
from specster.fwi.misfit import WaveformMisFit

import matplotlib.pyplot as plt

import local

if __name__ == "__main__":
    control_initial = sp.Control2d(local.inclusion_2d_initial_path)
    control_true = sp.Control2d(local.inclusion_2d_true_path)

    inverter = sp.Inverter(
        # Specifies where true data are found
        observed_data_path=control_true.each_source_path,
        # The initial control is used to setup the inversion
        control=control_initial,
        # A "true" control object is needed to compare model misfit
        true_control=control_true,
        # The working_path optionally specifies where the inverter does its work
        working_path=local.fwi_work_path,
        misfit=WaveformMisFit,
    )

    breakpoint()
    inverter.run_inversion_iteration()
    # set model number 2 to have the same properties as mod 1
    # this homogenises the model
    models = control.par.material_models.models
    models[1].Vs = models[0].Vs
    models[1].Vp = models[0].Vp
    models[1].rho = models[0].rho

    control.write(overwrite=True)
    fig, *_ = control.plot_geometry(kernel='vs', overwrite=True)

    fig.savefig(local.inclusion_initial_geometry_path, bbox_inches='tight', pad_inches=0)

    control.run_each_source()
