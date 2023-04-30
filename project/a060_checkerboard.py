"""
Create and plot as single station/event kernel.
"""
from pathlib import Path

import matplotlib.pyplot as plt

import local

if __name__ == "__main__":
    import specster as sp
    from specster.fwi.misfit import WaveformMisFit

    control = sp.load_2d_example("checkerboard_2d")
    control.plot_geometry(kernel='vs')
    breakpoint()

