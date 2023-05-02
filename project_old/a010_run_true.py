"""
Run the true model.
"""
import local
import specster as sp

if __name__ == "__main__":
    control = (
        sp.Control2d(local.true_input).copy(local.true_workspace).prepare_fwi_forward()
    )
    control.clear_outputs()
    # run forward
    control.run(output_path=local.true_output)
