"""
Core functions for full wave.
"""
import contextlib
import os
import re
from pathlib import Path
from subprocess import run

import numpy as np
import obspy

BASE_PATH = Path(__file__).parent.parent.parent
BIN_PATH = BASE_PATH / "bin"


# Some utility functions (written by Ridvan Orsvuran)
def read_trace(filename):
    """Reads an ASCII file and returns a obspy Traces"""
    data = np.loadtxt(filename)
    # first column is time, second column is the data
    times = data[:, 0]
    disp = data[:, 1]
    # get station name from the filename
    net, sta, comp, *_ = filename.split("/")[-1].split(".")
    delta = times[1] - times[0]
    headers = {
        "station": sta,
        "network": net,
        "channel": comp,
        "delta": delta,
        "b": times[0],
    }
    return obspy.Trace(disp, headers)


def save_trace(tr, filename):
    """Writes out the traces as an ASCII file. Uses b value as the beginning."""
    data = np.zeros((len(tr.data), 2))
    data[:, 0] = tr.times() + tr.stats.b
    data[:, 1] = tr.data
    np.savetxt(filename, data)


def specfem_write_parameters(filename, parameters, output_file=None):
    """Write parameters to a specfem config file"""

    with open(filename) as f:
        pars = f.read()

    for varname, value in parameters.items():
        pat = re.compile(
            r"(^{varname}\s*=\s*)([^#$\s]+)".format(varname=varname), re.MULTILINE
        )
        pars = pat.sub(r"\g<1>{value}".format(value=value), pars)

    if output_file is None:
        output_file = filename

    with open(output_file, "w") as f:
        f.write(pars)


def specfem2D_prep_save_forward(filename=None):
    if filename is None:
        filename = "./DATA/Par_file"
    params = {"SIMULATION_TYPE": 1, "SAVE_FORWARD": ".true."}
    specfem_write_parameters(filename, params)


def specfem2D_prep_adjoint(filename=None):
    if filename is None:
        filename = "./DATA/Par_file"
    params = {"SIMULATION_TYPE": 3, "SAVE_FORWARD": ".false."}
    specfem_write_parameters(filename, params)


def grid(x, y, z, resX=100, resY=100):
    """
    Converts 3 column data to matplotlib grid
    """
    # Can be found in ./utils/Visualization/plot_kernel.py
    from scipy.interpolate import griddata

    xi = np.linspace(min(x), max(x), resX)
    yi = np.linspace(min(y), max(y), resY)

    # mlab version
    # Z = griddata(x, y, z, xi, yi, interp='linear')
    # scipy version
    Z = griddata((x, y), z, (xi[None, :], yi[:, None]), method="cubic")

    X, Y = np.meshgrid(xi, yi)
    return X, Y, Z


@contextlib.contextmanager
def change_dir(new):
    """Change directory to new, then back to current."""
    target = Path(new)
    current = Path.cwd()
    os.chdir(target)
    yield
    os.chdir(current)


def _create_outputs(cwd):
    """Ensure the ouputs folder exists."""
    path = Path(cwd) / "OUTPUT_FILES"
    if not path.exists():
        path.mkdir(exist_ok=True, parents=True)


def _call_bin(cwd, name):
    cwd = Path(cwd or Path().cwd()).absolute()
    _create_outputs(cwd)
    with change_dir(cwd):
        bin_path = BIN_PATH / name
        assert bin_path.exists()
        output = run(str(bin_path), shell=True, capture_output=True)
        print(output.stdout.decode("utf-8"))
        print(output.stderr.decode("utf-8"))
    return output


def mesh(cwd=None):
    """Run the mesher."""
    return _call_bin(cwd, "xmeshfem2D")


def specfem(cwd=None):
    """Run specfem."""
    return _call_bin(cwd, "xspecfem2D")


if __name__ == "__main__":
    mesh()
