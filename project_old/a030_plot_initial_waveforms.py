"""
Plot the initial waveforms.
"""
import specster as sp

import local

if __name__ == "__main__":
    control = sp.Control2d(local.initial_workspace)
    out = control.output
    st = out.get_waveforms()

    breakpoint()
