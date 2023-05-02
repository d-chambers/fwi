"""
Split the windows for the true and initial waveforms
"""

import local
import obspy


def split_wave(st):
    """Split the stream."""
    out = {}
    for name, times in local.windows.items():
        t1, t2 = obspy.UTCDateTime(times[0]), obspy.UTCDateTime(times[1])
        sliced = st.slice(starttime=t1, endtime=t2)
        out[name] = sliced
    return out


if __name__ == "__main__":
    wf_dict = {
        "true": obspy.read(local.true_waveforms_path),
        "initial": obspy.read(local.initial_waveforms_path),
    }
    for name, st in wf_dict.items():
        for phase_name, phase_st in split_wave(st).items():
            path = local.split_wf_directory / phase_name / f"{name}.mseed"
            path.parent.mkdir(exist_ok=True, parents=True)
            phase_st.write(path, "mseed")
    # also save the complete waveforms
