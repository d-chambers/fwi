"""
Generate the intial model.
"""

import specster as sp

import local

if __name__ == "__main__":
    control = sp.load_2d_example('Tromp2005', new_path=local.true_workspace)
    # set to use s-h
    control.par.p_sv = False
    control.sources[0].time_function_type = '1'
    control.run(output_path=local.true_output)
