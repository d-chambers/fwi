"""
Plot the kernels.
"""

import specster as sp
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr  # has classes for tick-locating and -formatting

import local


def numfmt(x, pos):  # your custom formatter function: divide by 100.0
    s = '{}'.format(x / 1000.0)
    return s


if __name__ == "__main__":

    for misfit_path in local.kernel_paths.glob('*'):
        assert misfit_path.is_dir()
        misfit_name = misfit_path.name
        control = sp.Control2d(misfit_path)
        out = control.output
        kernel = out.load_kernel()
        fig, ax = out.plot_kernels(columns=['beta'], kernel_df=kernel)
        # polish the figure and save.
        fig.set_size_inches(7.5, 3)
        ax.invert_yaxis()
        ax.set_title(f"SH Beta Kernel: {misfit_name}")
        # set x/Z labels to km to be less confusing.
        ax.set_xlabel('X (km)')
        ax.set_ylabel("Z (km)")
        yfmt = tkr.FuncFormatter(numfmt)
        ax.yaxis.set_major_formatter(yfmt)
        ax.xaxis.set_major_formatter(yfmt)
        # tighten and save
        plt.tight_layout()
        out_path = local.kernel_plot / f"{misfit_name}.png"
        out_path.parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(out_path)
