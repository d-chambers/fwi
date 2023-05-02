"""
Generate the intial model.
"""

import local
import specster as sp

if __name__ == "__main__":
    control = (
        sp.Control2d(local.true_workspace)
        .copy(local.initial_workspace)
        .prepare_fwi_forward()
    )
    # set velocity in S
    model = control.models[0]
    model.Vs *= 0.975
    # run forward
    control.run(output_path=local.initial_output)
