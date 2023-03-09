"""
Calculate the True model seismograms.
"""


import local

if __name__ == "__main__":
    ws = local.get_workspace()
    ws.replace_par_line(262, local.initial_material)
    ws.set_source_type(2)
    ws.run_forward(output_name=local.initial_model_output)