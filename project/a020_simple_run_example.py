"""
Run the true model.
"""
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import specster as sp

import local


if __name__ == "__main__":
    import specster as sp

    path = Path("outputs/run_example")

    if path.is_dir():
        shutil.rmtree(path)

    control = (
        sp.Control2d()
        .copy(path)
        .prepare_fwi_forward()  # forward FWI run
    )
