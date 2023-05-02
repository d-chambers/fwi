"""
Run the initial model.
"""

import local
import specster as sp

if __name__ == "__main__":
    breakpoint()
    control = (
        sp.Control2d(local.initial_input)
        .copy(local.initial_workspace)
        .prepare_fwi_forward()
    )
    control.clear_outputs()
    # run forward
    control.run(output_path=local.initial_output)
