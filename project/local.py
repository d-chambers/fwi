"""
Project for reproducing tromp et al., 2005 figures
"""
from pathlib import Path

import obspy

import matplotlib.pyplot as plt
import pandas as pd
from specster.core.plotting import plot_single_gll

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

inclusion_2d_true_random_path = output_path / "a080_inclusion_2d_random_true"
inclusion_2d_initial_random_path = output_path / "a080_inclusion_2d_random_initial"
fwi_random_path = output_path / "a080_random_fwi_workpath"

fwi_smoothed_work_path = output_path / "a090_fwi_smooth_workpath"

layered_true_path = output_path / "a100_layered_true"
layered_initial_path = output_path / "a100_layered_initial"

acoustic_reflector_true_path = output_path / "a110_acoustic_ref_true"
acoustic_reflector_initial_path = output_path / "a110_acoustic_ref_initial"

acoustic_reflector_fwi_path = output_path / 'a112_acoustic_ref_fwi'
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


def create_initial_model(control):
    """Create the initial model from true model."""
    models = control.par.material_models.models
    models[1].Vs = models[0].Vs
    models[1].Vp = models[0].Vp
    models[1].rho = models[0].rho
    control.write(overwrite=True)
    control.run_each_source()


def load_model_updates(inverter):
    """Load all the model updates into a dataframe."""
    out = {}
    for it in range(1, 100):
        base_path = inverter._get_iteration_directory(it)
        path = base_path / inverter._iteration_kernel_file_name
        if not path.exists():
            break
        out[it] = pd.read_parquet(path)
    return out


def plot_model_updates(inverter, kernel='beta'):
    """First load all the update dataframes."""
    models = load_model_updates(inverter)
    fig, axes = plt.subplots(len(models), 1)
    if isinstance(axes, plt.Axes):
        axes = [axes]
    for (iteration, model), ax in zip(models.items(), axes):
        df = model.reset_index()
        ax = plot_single_gll(ax, df, kernel, ("x", "z"), 6)
        ax.set_title(f"{kernel.capitalize()}: {iteration}")
    plt.tight_layout()
    return fig, axes


def plot_final_model(inverter):
    """Plot final and correct model together."""
    #
    iteration = len(inverter.iteration_results)
    base_path = inverter._get_iteration_directory(iteration)
    path = base_path / inverter._material_model_file_name
    assert path.exists()

    df = pd.read_parquet(path)
    true_mod = inverter._true_model

    vlims = [3180, 3220]

    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1 = plot_single_gll(ax1, df, "vs", ("x", "z"), 6, vlims=vlims)
    ax2 = plot_single_gll(ax2, true_mod, "vs", ("x", "z"), 6, vlims=vlims)

    return fig, (ax1, ax2)


def plot_misfit(inverter):
    """Make a plot of the misfit functions."""
    it_res = inverter.iteration_results
    misfits = [x.data_misfit for x in it_res]
    iterations = range(1, len(it_res) + 1)
    fig, ax = plt.subplots(1, 1)
    ax.plot(iterations, misfits, ".-", label='data misfit', color='blue')
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Data Misfit")
    ax.set_title("Misfit")
    ax.yaxis.label.set_color('blue')
    # plot model misfit
    model_misfit = [x.model_misfit['vs'] for x in it_res]
    ax2 = ax.twinx()
    ax2.plot(iterations, model_misfit, '.-', label='model misfit', color='red')
    ax2.set_ylabel("Model Misfit")
    ax2.yaxis.label.set_color('red')
    return fig, ax
