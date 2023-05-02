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

true_workspace = output_path / "a010_base_specfem"
true_output = output_path / "a010_true_output"

initial_workspace = output_path / "a020_initial_specfem"
initial_output = output_path / "a020_initial_output"


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
