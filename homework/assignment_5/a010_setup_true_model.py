"""
Generate the intial model.
"""
import local
import numpy as np
import specster as sp
from specster.d2.io.parfile import Station2D


def create_stations():
    """Create stations."""
    mesh = np.meshgrid(range(10_000, 200_000, 10_000), range(10_000, 80_000, 10_000))
    out = []
    for name, (x, z) in enumerate(zip(mesh[0].flatten(), mesh[1].flatten())):
        sta = Station2D(
            xs=x,
            zs=z,
            station=f"{name:05d}",
            network="UU",
        )
        out.append(sta)
    return out


if __name__ == "__main__":
    control = sp.load_2d_example("Tromp2005", new_path=local.true_workspace)
    # setup run
    control.par.receivers.save_binary_seismograms_single = False
    control.sources[0].xs, control.sources[0].zs = 100_000, 40_000
    control.par.p_sv = False
    control.sources[0].time_function_type = "1"
    control.par.internal_meshing.absorbtop = True
    control.par.receivers.use_existing_stations = True
    control.stations = create_stations()

    control.clear_outputs()
    control.run(output_path=local.true_output)
