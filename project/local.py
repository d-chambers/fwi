"""
Project for reproducing tromp et al., 2005 figures
"""
from pathlib import Path

import obspy

# setup paths
here = Path(__file__).absolute().parent
input_path = here / Path("inputs")
output_path = here / Path("outputs")
output_path.mkdir(exist_ok=True)

true_input = input_path / "true"
initial_input = input_path / "initial"

basic_plot_path = output_path / "a010_basic_plot.png"

stream_plot_path = output_path / "a030_stream_plot.png"
gll_hist_plot = output_path / "a030_gll_hist.png"


true_workspace = output_path / "a010_base_specfem"
true_output = output_path / "a010_true_output"

initial_workspace = output_path / "a020_initial_specfem"
initial_output = output_path / "a020_initial_output"

modified_geometry = output_path / "a040_modified_geometry.png"

material_modified_path = output_path / "a042_material_modified.png"

material_df_modified_path = output_path / "a044_material_df_modified.png"


single_single_kernel_true_path = output_path / "a050_single_single_true"
sing_single_geometry_path = output_path / "a050_single_single_geometry.png"
single_single_kernel_initial_path = output_path / "a050_single_single_initial"
adjoint_plot_path = output_path / "a050_adjoint_plot.png"
sing_sing_banana_donut = output_path / "a050_sing_single_donut.png"

adjoint_misfit_plot_path = output_path / "a052_adjoint_plot.png"

inclusion_2d_true_path = output_path / "a060_inclusion_2d_true"
inclusion_true_geometry_path = output_path / "a060_inclusion_geometry.png"

inclusion_2d_initial_path = output_path / "a062_inclusion_2d_initial"
inclusion_initial_geometry_path = output_path / "a062_inclusion_geometry.png"

fwi_work_path = output_path / "a064_fwi_workpath"

model_update_path = output_path / "a066_model_updates.png"
final_model_path = output_path / "a066_final_model.png"
misfit_plot_path = output_path / "a066_misfit_plot.png"

fwi_tt_work_path = output_path / "a070_fwi_workpath_travel_time"

tt_model_update_path = output_path / "a072_model_updates.png"
tt_final_model_path = output_path / "a072_final_model.png"
tt_misfit_plot_path = output_path / "a072_misfit_plot.png"


# --- helper functions


def get_preprocessing_func(output):
    """Get a sane pre-processing function based on output of intial run."""

    def preprocess(st):
        """Preprocess streams."""
        out = (
            st.detrend("linear")
            .taper(0.05)
            .filter("lowpass", freq=output.stats.max_frequency_resolved)
            .taper(0.05)
        )
        return out

    return preprocess


def load_phases(phase_directory, pre_proc=None):
    """Loads the streams related to different phases."""
    for phase_path in Path(phase_directory).glob("*"):
        phase_name = phase_path.name
        out = {}
        for path in phase_path.glob("*.mseed"):
            name = path.name.split(".")[0]
            st = obspy.read(path)
            if pre_proc:
                st = pre_proc(st)
            out[name] = st
        yield phase_name, out
