"""
Script to run the coal stuff.
"""
import specster

if __name__ == "__main__":
    control = specster.Control2d('COALCASE1')
    control.clear_outputs()
    if control.empty_output:
        control.xmeshfem2d()
        control.xspecfem2d()
    st = control.get_waveforms()
    breakpoint()


