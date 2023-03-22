"""
Get adjoint source for a variety of misfits.
"""

import specster as sp
from specster.fwi.misfit import WaveformMisFit, TravelTimeMisFit

import local

misfits = {
    "waveform": WaveformMisFit,
    "travel_time": TravelTimeMisFit,
}

if __name__ == "__main__":
    control = sp.Control2d(local.initial_workspace)
    pre_proc = local.get_preprocessing_func(control.output)

    for phase, st_dict in local.load_phases(
            local.split_wf_directory, pre_proc=pre_proc
    ):
        synth = st_dict['initial']
        observed = st_dict['true']
        for misfit_name, Misfit in misfits.items():
            wf = Misfit(observed, synth)
            adjoints = pre_proc(wf.get_adjoint_sources())
            base_path = local.wf_adjoint_sources / f"{misfit_name}" / f"{phase}.mseed"
            base_path.parent.mkdir(exist_ok=True, parents=True)
            adjoints.write(base_path, 'mseed')
