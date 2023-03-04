"""
Calculate the True model seismograms.
"""

import local

if __name__ == "__main__":
    ws = local.get_workspace()
    ws.refresh()

    # Set the True velocity
    ws.replace_par_line(262, local.true_material)
    ws.run_forward(output_name=local.true_model_output)
