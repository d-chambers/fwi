"""
Run the true model.
"""
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import specster as sp

import local
import matplotlib.pyplot as plt

import local


if __name__ == "__main__":
    import specster as sp

    path = Path("outputs/run_example")

    control = sp.Control2d(path)
    output = control.output

    st = output.get_waveforms()
    st_fig = st.select(component='Z')[:3].plot(show=False)
    st_fig.savefig(local.stream_plot_path)
    plt.tight_layout()
    plt.cla()

    # plot
    fig, _ = output.plot_gll_per_wavelength_histogram()
    fig.savefig(local.gll_hist_plot)
    breakpoint()
