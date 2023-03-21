"""
Calculate kernels for each misfit/phase.
"""

import obspy

import specster as sp

import local

if __name__ == "__main__":
    initial_control = sp.Control2d(local.initial_workspace)
    initial_st = initial_control.output.get_waveforms()
    tr = initial_st[0]
    start, stop = tr.stats.starttime, tr.stats.endtime

    for misfit_path in local.wf_adjoint_sources.glob('*'):
        assert misfit_path.is_dir()
        misfit_name = misfit_path.name
        for mseed_path in misfit_path.glob('*.mseed'):
            phase_name = mseed_path.name.split(".")[0]
            st = obspy.read(mseed_path).trim(
                starttime=start,
                endtime=stop,
                fill_value=0,
                pad=True,
            )
            assert st[0].data.shape == tr.data.shape
            # init control 2D
            new_control_path = local.kernel_paths / f"{misfit_name}" / f"{phase_name}"
            control = (
                initial_control
                .copy(new_control_path)
                .prepare_fwi_adjoint()
                .write_adjoint_sources(st)
            )
            control.run()
