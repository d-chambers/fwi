# fwi

CSM spring 2023 FWI course work.

The homework directory contains subdirectories for each assignment.

The src file contains a python package for working with specfem2d and other
utilities. To install this, do the following:


# Specfem

Compile [specfem2d](https://github.com/SPECFEM/specfem2d) and copy the bin
in this directory.

# Setup an environment

```bash
conda env create -f environment.yml
conda activate fwi
```

# Install pre-commit

```bash
pre-commit install
```
