"""
Create a split of the inclusion with homogeneous velocity.
"""

import local
import matplotlib.pyplot as plt
import pandas as pd
import specster as sp
from specster.core.plotting import plot_single_gll





if __name__ == "__main__":
    inverter = sp.Inverter.load_inverter(local.fwi_work_path)
    # plot model updates.
    fig1, _ = local.plot_model_updates(inverter)
    fig1.savefig(local.model_update_path, bbox_inches="tight", pad_inches=0)
    # now plot final model.
    fig2, ax = local.plot_final_model(inverter)
    fig2.savefig(local.final_model_path, bbox_inches="tight", pad_inches=0)
    # plot misfit by iteration.
    fig3, ax = local.plot_misfit(inverter)
