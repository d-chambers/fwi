"""
Plot the initial waveforms.
"""
import local
import specster as sp

if __name__ == "__main__":
    control = sp.Control2d(local.initial_workspace)
    out = control.output
    st = out.get_waveforms()

    breakpoint()
