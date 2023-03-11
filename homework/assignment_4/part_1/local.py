"""
Project for reproducing tromp et al., 2005 figures
"""
import shutil
from pathlib import Path

# setup paths
here = Path(__file__).absolute().parent
input_path = here / Path('inputs')
output_path = here / Path('outputs')
output_path.mkdir(exist_ok=True)

# define source receiver geometry
source_location = (50_000, 40_000)
station_location = (150_000, 40_000)
x_lims = [0, 200_000]
z_lims = [0, 80_000]

# bandwidth resolvable in simulation
bandwidth = [0.03, 29]

# initial and true model
true_material = "1 1 2600.d0 5800.d0 3198.6d0 0 0 10.d0 10.d0 0 0 0 0 0 0\n"
initial_material = "1 1 2600.d0 5800.d0 3100.0d0 0 0 10.d0 10.d0 0 0 0 0 0 0\n"

# source type
source_type = 2

# output files
model_geometry = output_path / "a010_model_geometry.png"

true_model_output = "a020_true_model_outputs"

true_waveforms_plot = "a030_true_waveforms.png"

initial_model_output = 'a040_initial_outputs'

wf_misfit_waveform_plot = output_path / "a040_wf_misfit_waveforms.png"
wf_adjoint_output = "a040_wf_adjoint_outputs"
wf_kernel_plot = output_path / "a040_wf_kernel.png"

tt_misfit_waveform_plot = output_path / "a050_tt_misfit_waveforms.png"
tt_adjoint_output = "a050_tt_adjoint_outputs"
tt_kernel_plot = output_path / "a050_tt_kernel.png"

amp_misfit_waveform_plot = output_path / "a060_amp_misfit_waveforms.png"
amp_adjoint_output = "a060_amp_adjoint_outputs"
amp_kernel_plot = output_path / "a060_amp_kernel.png"


# --- helper functions

def get_workspace():
    """Get the workspace. """
    from misfit_kernel import Workspace
    ws = Workspace(
        work_path=output_path,
        bin_path=Path("/media/data/Gits/specfem2d/bin"),
        template_path=here / "base_example" / "DATA",
    )
    return ws


def reset_output_to_initial(ws):
    """Refresh the output folder, set to initial output."""
    output = output_path / "OUTPUT_FILES"
    if output_path.exists():
        shutil.rmtree(output)
    shutil.copytree(ws.work_path / initial_model_output, output)
