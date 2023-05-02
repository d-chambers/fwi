"""
Create a split of the inclusion with homogeneous velocity.
"""
from pathlib import Path

import local
import matplotlib.pyplot as plt
import specster as sp
from specster.fwi.misfit import WaveformMisFit

if __name__ == "__main__":
    control_initial = sp.Control2d(local.inclusion_2d_initial_path)
    control_true = sp.Control2d(local.inclusion_2d_true_path)
    if local.fwi_work_path.exists():
        inverter = sp.Inverter.load_inverter(local.fwi_work_path)
    else:
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
            kernels=("beta",),
        )
    for _ in range(10):
        inverter.run_iteration()
