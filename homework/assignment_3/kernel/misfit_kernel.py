"""
2D Kernel with SPECFEM2D
Based on a notebook by Andrea R.  
Utility functions written by Ridvan Orsvuran.  
Following file structure as in the Seisflows example (By Bryant Chow)
"""
import os
import shutil
from pathlib import Path
from subprocess import run

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from pydantic import Field
from pydantic.dataclasses import dataclass
from scipy.integrate import simps

import FunctionsPlotBin
from UtilityFunctions import (
    read_trace,
    specfem2D_prep_save_forward,
    replace_line,
    save_trace,
    specfem2D_prep_adjoint,
    grid,
)


@dataclass
class Workspace:
    """
    A workspace for keeping track of various parameters.
    """

    work_path: Path = Field(default_factory=os.getcwd)
    bin_path: Path
    template_path: Path


def refresh_directory(dir_path: Path):
    """Make a fresh directory, delete old contents."""
    dir_path = Path(dir_path)
    if dir_path.exists():
        shutil.rmtree(dir_path)
    dir_path.mkdir(exist_ok=True, parents=True)
    return dir_path


if __name__ == "__main__":
    cwd_path = Path(os.getcwd())
    specfem_bin_path = Path("/media/data/Gits/specfem2d/bin")
    example_path = cwd_path / "Examples" / "DATA_Example01"
    work_path = refresh_directory(cwd_path / "work")

    # The SPECFEM2D working directory that we will create separate from the downloaded repo
    bin_path = work_path / "bin"
    data_path = work_path / "DATA"
    output_path = work_path / "OUTPUT_FILES"

    # Pre-defined locations of velocity models we will generate using the solver
    model_init_path = work_path / "OUTPUT_FILES_INIT"
    model_true_path = work_path / "OUTPUT_FILES_TRUE"

    # Copy the binary files incase we update the source code. These can also be symlinked.
    shutil.copytree(specfem_bin_path, bin_path)

    # Copy the DATA/ directory
    shutil.copytree(example_path, data_path)

# ### Generate true model


os.chdir(data_path)
specfem2D_prep_save_forward("Par_file")
# Modify the Par_file to increase Initial Vs by ~1%
replace_line(
    "Par_file", 262, "1 1 2700.d0 3000.d0 1820.d0 0 0 9999 9999 0 0 0 0 0 0 \n"
)

# create the OUTPUT_FILES directory before running
os.chdir(work_path)
if os.path.exists(output_path):
    shutil.rmtree(output_path)
os.mkdir(output_path)

# In[7]:


os.chdir(work_path)
run("bin/xmeshfem2D > OUTPUT_FILES/mesher_log.txt")
run("bin/xspecfem2D > OUTPUT_FILES/solver_log.txt")

# Move the model files (*.bin) into the OUTPUT_FILES directory
run("mv DATA/*bin OUTPUT_FILES")

# Make sure we don't overwrite this target model when creating our initial model in the next step
run("mv OUTPUT_FILES OUTPUT_FILES_TRUE")

run("head OUTPUT_FILES_TRUE/solver_log.txt")
run("tail OUTPUT_FILES_TRUE/solver_log.txt")

# In[8]:


x_coords_file = "OUTPUT_FILES_TRUE/proc000000_x.bin"
z_coords_file = "OUTPUT_FILES_TRUE/proc000000_z.bin"
Vs_true = "OUTPUT_FILES_TRUE/proc000000_vs.bin"

# Plot
FunctionsPlotBin.plotbin(
    x_coords_file, z_coords_file, Vs_true, work_path + "/Vs_true", "Vs_true=m/s"
)

# ### Generate initial model

# In[9]:


os.chdir(data_path)
replace_line(
    "Par_file", 262, "1 1 2700.d0 3000.d0 1800.d0 0 0 9999 9999 0 0 0 0 0 0 \n"
)

# In[10]:


# create the OUTPUT_FILES directory before running
os.chdir(work_path)
if os.path.exists(output_path):
    shutil.rmtree(output_path)
os.mkdir(output_path)
run("ls")

# In[11]:


os.chdir(work_path)
run("bin/xmeshfem2D > OUTPUT_FILES/mesher_log.txt")
run("bin/xspecfem2D > OUTPUT_FILES/solver_log.txt")

# Move the model files (*.bin) into the OUTPUT_FILES directory
# The binary files of the velocity models are stored in DATA after running xspecfem2D
run("mv DATA/*bin OUTPUT_FILES")

# Store output files of initial model
run("mv OUTPUT_FILES OUTPUT_FILES_INIT")

run("head OUTPUT_FILES_INIT/solver_log.txt")
run("tail OUTPUT_FILES_INIT/solver_log.txt")

# In[12]:


x_coords_file = "OUTPUT_FILES_INIT/proc000000_x.bin"
z_coords_file = "OUTPUT_FILES_INIT/proc000000_z.bin"
Vs_true = "OUTPUT_FILES_INIT/proc000000_vs.bin"

# Plot
FunctionsPlotBin.plotbin(
    x_coords_file, z_coords_file, Vs_true, work_path + "/Vs_init", "Vs_init=m/s"
)

# ### 3. Plot synthetic seismogram

# In[13]:


os.chdir(work_path)
# Read synthetic seismogram
obsd = read_trace(os.path.join("OUTPUT_FILES_TRUE", "AA.S0001.BXZ.semd"))
synt = read_trace(os.path.join("OUTPUT_FILES_INIT", "AA.S0001.BXZ.semd"))

# Process data
obsd.detrend("simple")
obsd.taper(0.05)
obsd.filter("bandpass", freqmin=0.01, freqmax=20)

synt.detrend("simple")
synt.taper(0.05)
synt.filter("bandpass", freqmin=0.01, freqmax=20)

matplotlib.rcParams.update({"font.size": 14})
fig, ax = plt.subplots(figsize=(20, 4))
# Use the beginning time value from the file: tr.times()+tr.stats.b
ax.plot(obsd.times() + obsd.stats.b, obsd.data, "b", label="Obsd")
ax.plot(synt.times() + synt.stats.b, synt.data, "r", label="Synt")
ax.set_xlim(synt.stats.b, synt.times()[-1] + synt.stats.b)
ax.legend(frameon=False)
ax.set_xlabel("Time (s)")
ax.set_ylabel("Displacement (m)")
ax.tick_params(axis="both", which="major", labelsize=14)

# In[23]:


synt

# ### Misfit Calculation and Adjoint Source
# For one seismogram, waveform misfit is
#
# $$ \chi = \frac{1}{2} \int [d(t)-s(t)]^2 dt~, $$
#
#
# and waveform adjoint source is
#
# $$  f^\dagger (t) = s(t) - d(t)~,$$
#
# where $s(t)$ is the synthetic, $d(t)$ is the observed seismograms.

# In[14]:


# Misfit
misfit = simps((obsd.data - synt.data) ** 2, dx=obsd.stats.delta)
print(f"Misfit: {misfit:.6f}")

# Adjoint Source
adj = synt.copy()
adj.data = synt.data - obsd.data

# Process
adj.detrend("simple")
adj.taper(0.05)
adj.filter("bandpass", freqmin=0.01, freqmax=20)

# In[15]:


fig, axes = plt.subplots(nrows=2, sharex=True, figsize=(20, 8))
axes[0].plot(obsd.times() + obsd.stats.b, obsd.data, "b", label="obsd")
axes[0].plot(synt.times() + synt.stats.b, synt.data, "r", label="synt")
axes[0].set_xlim(obsd.stats.b, obsd.times()[-1] + obsd.stats.b)
axes[0].legend()
axes[0].legend(frameon=False)
axes[0].set_ylabel("Displacement (m)")

axes[1].plot(adj.times() + adj.stats.b, adj.data, "g", label="Adjoint Source")
axes[1].legend()
axes[1].legend(frameon=False)
axes[1].set_xlabel("Time (s)")
ax.tick_params(axis="both", which="major", labelsize=14)
matplotlib.rcParams.update({"font.size": 14})

# ### Adjoint simulation

# In[16]:


os.chdir(work_path)
# Save adjoint source to SEM directory
os.makedirs("SEM", exist_ok=True)
save_trace(adj, "SEM/AA.S0001.BXY.adj")

# For adjoint simulation, following `DATA/Par_file` needs be set
#
# ```toml
# SIMULATION_TYPE                 = 3
# # save the last frame, needed for adjoint simulation
# SAVE_FORWARD                    = .false.
# ```
#
# `specfem2D_prep_adjoint` function can be used for this purpose.

# In[20]:


# Prepare Par_file
os.chdir(data_path)
specfem2D_prep_adjoint("Par_file")

# In[21]:


# create the OUTPUT_FILES directory before running and copy
# results of OUTPUT_FILES_INIT to the new created OUTPUT_FILES, this is needed
# for the adjoint simulation because we saved the last frame in the
# forward simulation of the initial model

os.chdir(work_path)
if os.path.exists(output_path):
    shutil.rmtree(output_path)
os.mkdir(output_path)
run("cp OUTPUT_FILES_INIT/* OUTPUT_FILES")
run("ls")

# In[22]:


os.chdir(work_path)
run("bin/xmeshfem2D > OUTPUT_FILES/mesher_log.txt")
run("bin/xspecfem2D > OUTPUT_FILES/solver_log.txt")

# Move the model files (*.bin) into the OUTPUT_FILES directory
# The binary files of the velocity models are stored in DATA after running xspecfem2D
run("mv DATA/*bin OUTPUT_FILES")

# Make sure we don't overwrite output files
run("mv OUTPUT_FILES OUTPUT_FILES_ADJ")

run("head OUTPUT_FILES_ADJ/solver_log.txt")
run("tail OUTPUT_FILES_ADJ/solver_log.txt")

# ### Plotting the Kernels
#
# `./OUTPUT_FILES/proc000000_rhop_alpha_beta_kernel.dat` file holds the kernel data.
#
# It is a text file contains 5 columns: `x`, `z`, `rhop`, `alpha`, `beta`.

# In[ ]:


data = np.loadtxt("./OUTPUT_FILES_ADJ/proc000000_rhop_alpha_beta_kernel.dat")

# first column: x
x = data[:, 0]
# second column: z
z = data[:, 1]
# fifth column: beta_kernel
beta = data[:, 4]

# For plotting, you can check: specfem2D/utils/Visualization/plot_kernel.py
vmax = 2.5e-9
X, Z, BETA = grid(x, z, beta)

fig, ax = plt.subplots(figsize=(8, 8))
im = ax.imshow(
    BETA,
    vmax=vmax,
    vmin=-vmax,
    extent=[x.min(), x.max(), z.min(), z.max()],
    cmap="seismic_r",
)
ax.set_xlabel("X (m)")
ax.set_ylabel("Z (m)")
ax.set_title("Beta Kernel")

# Plot source and station
ax.scatter(1000, 2000, 1000, marker="*", color="black", edgecolor="white")
ax.scatter(3000, 2000, 450, marker="v", color="black", edgecolor="white")

plt.colorbar(im, ax=ax)
ax.tick_params(axis="both", which="major", labelsize=14)
matplotlib.rcParams.update({"font.size": 14})

# In[ ]:
