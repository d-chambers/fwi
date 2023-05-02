"""
Examples of modifying the control.
"""
import shutil
from pathlib import Path

import local
import matplotlib.pyplot as plt
import specster as sp

if __name__ == "__main__":
    import specster as sp

    path = Path("outputs/run_example")

    control = sp.Control2d(path).copy()

    control.stations = control.stations[:1]

    new_source = control.sources[0].copy()
    new_source.xs, new_source.zs = 1500.0, 1500.0
    control.sources.append(new_source)

    control.write(overwrite=True)

    fig, _ = control.plot_geometry(kernel=["vs", "vp"])
    fig.savefig(local.modified_geometry, bbox_inches="tight", pad_inches=0)
