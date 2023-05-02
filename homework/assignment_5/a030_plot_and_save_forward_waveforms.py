"""
Calculate the True model seismograms.
"""
import local
import matplotlib.pyplot as plt
import specster as sp


def plot_true_and_initial(st_true, st_init):
    """Plot True and initial streams."""
    assert len(st_true) == len(st_init) == 1
    tr_true, tr_init = st_true[0], st_init[0]

    fig, ax = plt.subplots(1, 1, figsize=(5, 3))
    time = tr_init.times() + tr_init.stats.starttime.timestamp
    ax.plot(time, tr_true.data, label="True")
    ax.plot(time, tr_init.data, label="Initial")
    ax.legend(loc="upper left")
    # add phases
    ax.axvline(local.windows["S"][0], color="0.5", ls="--")
    ax.axvline(local.windows["S"][1], color="0.5", ls="--")
    ax.axvline(local.windows["SS"][1], color="0.5", ls="--")
    # set axis
    ax.set_xlabel("time (s)")
    ax.set_ylabel("displacement (m)")
    # zoom in around phases
    ax.set_xlim(20, 50)
    return fig, ax


def assert_not_same(st1, st2):
    """Ensure the streams are not identical"""
    st1.sort()
    st2.sort()
    for tr1, tr2 in zip(st1, st2):
        assert not tr1 == tr2


if __name__ == "__main__":
    cont_true = sp.Control2d(local.true_workspace)
    out_true = cont_true.output
    st_true = out_true.get_waveforms()

    cont_initial = sp.Control2d(local.initial_workspace)
    out_initial = cont_initial.output
    st_initial = out_initial.get_waveforms()

    # Ensure true and initial are not identical.

    assert_not_same(st_true, st_initial)

    st_initial.write(local.initial_waveforms_path, "mseed")
    st_true.write(local.true_waveforms_path, "mseed")
