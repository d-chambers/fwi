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

true_workspace = output_path / "a010_base_specfem"
true_output = output_path / "a010_true_output"

initial_workspace = output_path / "a020_initial_specfem"
initial_output = output_path / "a020_initial_output"

waveform_plot = output_path / "a030_waveform_plot.png"
initial_waveforms_path = output_path / "a030_initial.mseed"
true_waveforms_path = output_path / "a030_true.mseed"

split_wf_directory = output_path / "a040_split_waveforms"
split_wf_directory.mkdir(exist_ok=True, parents=True)

wf_adjoint_sources = output_path / "a050_adjoints"

kernel_paths = output_path / "a060_kernel_outputs"

kernel_plot = output_path / "a070_kernel_plots"

# Defines the windows used for distinct phases
windows = {
    "S": (26.5, 36.5),
    "SS": (36.5, 46.5),
    "Whole": (26.5, 46.5),
}


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
