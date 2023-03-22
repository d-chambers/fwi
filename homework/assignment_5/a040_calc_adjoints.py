"""
Get adjoint source for a variety of misfits.
"""

import obspy

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

    synth = pre_proc(obspy.read(local.initial_waveforms_path))
    observed = pre_proc(obspy.read(local.true_waveforms_path))

    for misfit_name, Misfit in misfits.items():
        wf = Misfit(observed, synth)
        adjoint_raw = wf.get_adjoint_sources()
        adjoints = pre_proc(adjoint_raw)
        base_path = local.wf_adjoint_sources / f"{misfit_name}.mseed"
        base_path.parent.mkdir(exist_ok=True, parents=True)
        adjoints.write(base_path, 'mseed')
