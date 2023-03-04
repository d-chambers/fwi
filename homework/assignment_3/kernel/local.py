"""
A project for extracting info from mine map.

Notes:
    Microphone array broke around 2022-08-03T06

    panline break occurs around meter 532.
"""
from pathlib import Path

# setup paths
here = Path(__file__).absolute().parent
input_path = here / Path('inputs')
output_path = here / Path('outputs')
output_path.mkdir(exist_ok=True)

# define source receiver geometry
source_location = (1_000, 2_000)
station_location = (3_000, 2_000)
x_lims = [0, 4_000]
z_lims = [0, 4_000]

# bandwidth resolvable in simulation
bandwidth = [0.03, 29]

true_material = "1 1 2700.d0 3000.d0 1820.d0 0 0 9999 9999 0 0 0 0 0 0 \n"
initial_material = "1 1 2650.d0 2950.d0 1770.d0 0 0 9999 9999 0 0 0 0 0 0 \n"


# output files
model_geometry = output_path / "a010_model_geometry.png"

true_model_output = "a020_true_model_outputs"

initial_model_output = 'a030_initial_outputs'


def get_workspace():
    """Get the workspace. """
    from misfit_kernel import Workspace
    ws = Workspace(
        work_path=output_path,
        bin_path=Path("/media/data/Gits/specfem2d/bin"),
        template_path=here / "Examples" / "DATA_Example01",
    )
    return ws





