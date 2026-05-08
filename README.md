# supervisedmdamber

## Supervised Molecular Dynamics (SuMD) and Supervised Gaussian Accelerated Molecular Dynamics (SuGaMD) for Amber

Implementation using Amber MD suite by Midhun K Madhu

---

# Overview

`supervisedmdamber` is a Python-based workflow driver for performing:

- Supervised Molecular Dynamics (SuMD)
- Supervised Gaussian Accelerated Molecular Dynamics (SuGaMD)

using the Amber MD suite.

The workflow automates repeated short molecular dynamics windows and evaluates ligand progress toward a reference bound pose using RMSD-based supervision.

The implementation uses:

- Classical MD supervised workflows
- Gaussian accelerated MD supervised workflows
- Automatic RMSD evaluation
- Linear regression slope estimation
- Restart-state decision making
- Duplicate trajectory branch removal
- Automatic construction of combined supervised trajectories

The workflow was inspired by the original SuMD methodology introduced by:

Sabbadin, Davide, and Stefano Moro.

*"Supervised molecular dynamics (SuMD) as a helpful tool to depict GPCR-ligand recognition pathway in a nanosecond time scale."*

Journal of Chemical Information and Modeling 54.2 (2014): 372-376.

---

# Important Requirements Before Starting

This workflow is not intended to start from an unequilibrated system.

The system must already be properly equilibrated before starting supervised simulations.

The ligand should initially be positioned sufficiently far away from any non-hydrogen atom of the receptor, typically:

```text
25 to 30 Å
```

The workflow assumes that:

- The receptor structure is equilibrated
- The membrane and solvent are equilibrated
- The production-ready restart file already exists
- The reference bound pose structure is already known as a reference PDB file

---

# Additional Requirements for GaMD

For:

```text
METHOD=GaMD
```

additional preparation steps are required before supervised simulations can begin.

The following steps must already be completed:

1. Standard equilibration
2. GaMD equilibration
3. GaMD statistics collection phase
4. Creation of `gamd-restart.dat`
5. A short GaMD production run, typically around:

```text
1 ns
```

to ensure the system is fully prepared to continue GaMD production. The restart file for SuGaMD should come from this short GaMD production run.

The file:

```text
gamd-restart.dat
```

must already exist before starting the supervised GaMD workflow.

Do not rename this file.

If classical MD supervision is used:

```text
METHOD=cMD
```

then `gamd-restart.dat` is not required.

---

# Software Requirements

The following software must already be installed and available in the environment.

| Software | Purpose |
|---|---|
| Python 3.11+ | Main workflow |
| NumPy | Numerical processing |
| SciPy | Linear regression |
| Amber / AmberTools | MD execution and trajectory processing |
| cpptraj | RMSD calculations and trajectory fitting |
| awk | Internal bookkeeping |
| sort | Sorting operations |

Amber executables can be selected in the input parameter file using:

```text
AMBEREXE
```

Examples include:

```text
sander
pmemd
pmemd.cuda
pmemd.MPI
```

---

# Cloning the Repository

Clone the repository:

```bash
git clone https://github.com/MidhunkMadhu/supervisedmdamber.git
```

Enter the directory:

```bash
cd supervisedmdamber
```

---

# Installation

Create a conda environment:

```bash
conda create -n sumd python=3.11 numpy scipy pip -y
```

Activate the environment:

```bash
conda activate sumd
```

Install the package:

```bash
python -m pip install -e .
```

Check installation:

```bash
which supervisedmdamber
```

Check help:

```bash
supervisedmdamber -h
```

Expected output:

```text
usage: supervisedmdamber -i input_parameters.in
```

---

# Repository Structure

```text
supervisedmdamber/
│
├── supervisedmdamber.py
├── README.md
├── pyproject.toml
├── setup.py
│
├── helpfolder/
│   ├── create_traj.py
│   ├── create_unique_starting_points.py
│   ├── delete_extra_nc_files.py
│   ├── extract_and_fit.py
│   ├── extract_first_MDOUTline.py
│   ├── generate_calcCPPIN.py
│   ├── generate_fitCPPIN.py
│   ├── log_creater.py
│   └── modify_mdin.py
│
└── testfolder/
    ├── example.parm7
    ├── example.rst7
    ├── ref_example.pdb
    ├── input_parameters.in
    ├── gamd-restart.dat
    ├── sumd.in
    ├── suGamd.in
    └── run_sumd.sh
```

---

# Description of Main Components

## supervisedmdamber.py

Main workflow driver.

This executable controls:

- MD execution
- RMSD calculations
- Restart decisions
- Trajectory processing
- Supervised trajectory construction

This is the only executable users normally need to run directly.

---

## helpfolder/

Contains all helper scripts used internally by the workflow.

Users normally do not need to execute these scripts manually.

| Script | Purpose |
|---|---|
| `generate_fitCPPIN.py` | Generates the cpptraj input file used for fitting the trajectory to the reference structure |
| `generate_calcCPPIN.py` | Generates the cpptraj input file used for ligand RMSD calculation |
| `modify_mdin.py` | Creates `common_prod.mdin` from the selected Amber mdin template by inserting the requested time window, timestep, output frequency, and trajectory frequency |
| `extract_and_fit.py` | Reads the ligand RMSD profile, performs linear regression, writes the RMSD slope to `slope.dat`, and writes the final collective variable value to `cvval.dat` |
| `log_creater.py` | Creates or updates the compact supervision summary log from the per-step slope files |
| `extract_first_MDOUTline.py` | Extracts the first relevant `NSTEP` line from each Amber mdout file for identifying starting points |
| `create_unique_starting_points.py` | Reads all detected starting points and identifies unique trajectory branches |
| `delete_extra_nc_files.py` | Removes duplicate trajectory files based on the duplicate-branch list |
| `create_traj.py` | Creates the cpptraj concatenation script and generates the final combined supervised trajectory |

---

## testfolder/

Contains a prepared example workflow.

This folder includes:

| File | Purpose |
|---|---|
| `example.parm7` | Amber topology |
| `example.rst7` | Initial restart |
| `ref_example.pdb` | Reference bound structure |
| `input_parameters.in` | Main workflow parameter file |
| `gamd-restart.dat` | Required only for GaMD |
| `sumd.in` | Example cMD mdin template |
| `suGamd.in` | Example GaMD mdin template |
| `run_sumd.sh` | Example execution script |

---

# Tutorial

After installation, move into the example workflow folder:

```bash
cd testfolder
```

The example folder should contain:

- `example.parm7`
- `example.rst7`
- `ref_example.pdb`
- `input_parameters.in`
- `sumd.in`
- `suGamd.in`

and additionally:

```text
gamd-restart.dat
```

for GaMD workflows.

If GaMD is not required, this file can be ignored.

Do not rename:

```text
gamd-restart.dat
```

---

# Running the Workflow

## Direct Execution

```bash
supervisedmdamber -i input_parameters.in
```

---

# Recommended Execution Using a Script

It is generally recommended to run the workflow using a shell script.

Example:

```bash
bash run_sumd.sh
```

Even on local machines, long simulations are better launched using:

```bash
nohup bash run_sumd.sh &
```

This allows the workflow to continue running after terminal disconnection.

---

# Example Local Execution Script

Example `run_sumd.sh`:

```bash
#!/bin/bash

source ~/miniconda3/etc/profile.d/conda.sh

conda activate sumd

supervisedmdamber -i input_parameters.in
```

Make executable:

```bash
chmod +x run_sumd.sh
```

Run:

```bash
bash run_sumd.sh
```

---

# Example SLURM Submission Script

Example `run_sumd.sh` for SLURM systems:

```bash
#!/bin/bash
#SBATCH -J sumd
#SBATCH -p gpu
#SBATCH -t 24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH -o sumd-%j.out
#SBATCH -e sumd-%j.err

module load Amber

unset PYTHONPATH

source ~/miniconda3/etc/profile.d/conda.sh

conda activate sumd

supervisedmdamber -i input_parameters.in
```

Submit using:

```bash
sbatch run_sumd.sh
```

Edit the SLURM resource headers appropriately depending on the target cluster configuration.

---

# Example PBS Submission Script

Example `run_sumd.sh` for PBS systems:

```bash
#!/bin/bash
#PBS -N sumd
#PBS -l walltime=24:00:00
#PBS -l select=1:ncpus=1:ngpus=1
#PBS -j oe

cd $PBS_O_WORKDIR

module load Amber

unset PYTHONPATH

source ~/miniconda3/etc/profile.d/conda.sh

conda activate sumd

supervisedmdamber -i input_parameters.in
```

Submit using:

```bash
qsub run_sumd.sh
```

Edit the PBS resource headers appropriately depending on the target cluster configuration.

---

# Input Parameter File

Example:

```text
&parameters
CPPTRAJ="cpptraj",
AMBEREXE="pmemd.cuda",
METHOD=GaMD,
TIME_WINDOW_PS=600,
COLVARCUT=2,
TIMESTEP_FS=2,
MDOUTSTEP=100,
TRAJOUTSTEP=500,
MAXSTEP=5000,
INPUT_MDIN_FILE="suGamd.in",
AMBER_PARAMETER_FILE="example.parm7",
RESTART_FILE="example.rst7",
TRAJOUTNAME="traj.nc",
PDBALIGN="ref_example.pdb",
FIT_TRAJ_STRING="1-313@CA",
FIT_PDB_STRING="1-313@CA",
CALCRMSD_TRAJ_STRING="314&!@H=",
CALCRMSD_PDB_STRING="314&!@H=",
/
```

---

# Description of Input Parameters

| Parameter | Required? | Type | Description |
|---|---|---|---|
| `CPPTRAJ` | Yes | string | cpptraj executable name or path. Example: `cpptraj` |
| `AMBEREXE` | Yes | string | Amber MD executable name or path. Example: `sander`, `pmemd`, `pmemd.cuda`, or `pmemd.MPI` |
| `MPIPREFIX` | Required only for `pmemd.MPI` | string | MPI launch command. Example: `mpirun -np 16` |
| `METHOD` | Yes | string | Simulation method. Must be `cMD` or `GaMD` |
| `TIME_WINDOW_PS` | Yes | integer | Length of each supervised MD window in picoseconds |
| `COLVARCUT` | Yes | float | RMSD cutoff for convergence |
| `TIMESTEP_FS` | Yes | integer | MD timestep in femtoseconds |
| `MDOUTSTEP` | Yes | integer | Amber mdout print frequency in MD steps |
| `TRAJOUTSTEP` | Yes | integer | Trajectory write frequency in MD steps |
| `MAXSTEP` | Yes | integer | Maximum number of supervised cycles |
| `INPUT_MDIN_FILE` | Yes | string | Amber mdin template used to generate `common_prod.mdin` |
| `AMBER_PARAMETER_FILE` | Yes | string | Amber topology file |
| `RESTART_FILE` | Yes | string | Initial restart file |
| `TRAJOUTNAME` | Yes | string | Name of the final combined supervised trajectory |
| `PDBALIGN` | Yes | string | Reference PDB structure used by cpptraj |
| `FIT_TRAJ_STRING` | Yes | string | cpptraj mask used to fit each trajectory window |
| `FIT_PDB_STRING` | Yes | string | cpptraj mask used to fit the reference PDB |
| `CALCRMSD_TRAJ_STRING` | Yes | string | cpptraj mask used to calculate RMSD from the trajectory |
| `CALCRMSD_PDB_STRING` | Yes | string | cpptraj mask used to calculate RMSD from the reference PDB |

---

# Meaning of Key Parameters

## `TIME_WINDOW_PS`

This controls the length of each supervised MD segment.

For example:

```text
TIME_WINDOW_PS=600
```

means each supervised window is 600 ps long.

---

## `COLVARCUT`

This is the convergence cutoff for the collective variable.

In the current implementation, the collective variable is ligand RMSD.

The workflow stops when:

```text
CV < COLVARCUT and slope <= 0
```

---

## `MAXSTEP`

This is the maximum number of supervised cycles.

For example:

```text
MAXSTEP=5000
```

means the workflow can run up to 5000 supervised windows unless convergence is reached earlier.

---

## `INPUT_MDIN_FILE`

This is the Amber mdin template used for the production window.

For cMD:

```text
INPUT_MDIN_FILE="sumd.in"
```

For GaMD:

```text
INPUT_MDIN_FILE="suGamd.in"
```

The helper script `modify_mdin.py` reads this file and creates:

```text
common_prod.mdin
```

---

## `FIT_TRAJ_STRING` and `FIT_PDB_STRING`

These masks define which atoms are used for structural alignment.

Commonly, protein C-alpha atoms are used:

```text
FIT_TRAJ_STRING="1-313@CA"
FIT_PDB_STRING="1-313@CA"
```

---

## `CALCRMSD_TRAJ_STRING` and `CALCRMSD_PDB_STRING`

These masks define the atoms used for RMSD supervision.

For ligand heavy atoms, an example is:

```text
CALCRMSD_TRAJ_STRING="314&!@H="
CALCRMSD_PDB_STRING="314&!@H="
```

This means residue 314 excluding hydrogens.

---

# Workflow Logic

The workflow repeatedly:

1. Runs a short MD window
2. Fits the trajectory to the reference structure
3. Calculates ligand RMSD
4. Estimates RMSD slope using linear regression
5. Evaluates whether progress is productive
6. Selects the next restart file
7. Identifies duplicate trajectory branches
8. Removes duplicate trajectory files
9. Updates the combined supervised trajectory

The workflow stops when:

```text
CV < COLVARCUT and slope <= 0
```

or when:

```text
MAXSTEP reached
```

---

# Restart Decision Logic

After each supervised MD window, the script evaluates the final CV value and RMSD slope.

If:

```text
CV < COLVARCUT and slope <= 0
```

the workflow stops.

If:

```text
slope <= 0
```

the next cycle continues from the latest accepted restart.

If:

```text
slope > 0 and CV >= COLVARCUT
```

the next cycle restarts from the previous restart.

This prevents obviously non-productive RMSD-increasing branches from being extended.

---

# Output Files

| File or folder | Meaning |
|---|---|
| `traj.nc` | Combined supervised trajectory |
| `sumdprogress.log` | Detailed workflow log |
| `sumd.log` | Compact slope/CV summary |
| `additional_data/` | Per-step outputs and analysis files |
| `prod_N.nc` | Trajectory from supervised window N |
| `prod_N.mdout` | Amber output from supervised window N |
| `prod_N.rst7` | Restart from supervised window N |
| `prod_ligandRMSD_N.xvg` | Ligand RMSD profile from window N |
| `prod_slope_N.dat` | RMSD slope from window N |
| `prod_cvval_N.dat` | Final CV value from window N |
| `prod_gamd_N.log` | GaMD log from window N, only for GaMD |
| `all_starting_points.dat` | All detected trajectory starting points |
| `unique_starting_points.dat` | Unique trajectory branches |
| `duplicates_output.txt` | Duplicate trajectory branch list |
| `concat.cppin` | cpptraj input used to generate the combined trajectory |

Most per-step files are moved into:

```text
additional_data/
```

at the end of the workflow.

---

# Monitoring the Run

Follow the detailed log:

```bash
tail -f sumdprogress.log
```

Check the compact summary:

```bash
cat sumd.log
```

Check generated files:

```bash
ls additional_data
```

---

# Important Notes

- The workflow currently supports RMSD-based supervision only
- The choice of RMSD masks strongly affects performance
- The workflow assumes Amber-compatible topology and trajectory formats
- Existing generated files are automatically removed before a new run
- Previous runs are not automatically backed up
- Duplicate branch analysis is handled using helper scripts
- `gamd-restart.dat` must not be renamed for GaMD workflows
- The ligand should be initially placed 25 to 30 Å away from any non-hydrogen atom of the receptor
- The workflow should only be started from a properly equilibrated system

---

# Citation

If this workflow contributes to published work, please cite:

Sabbadin, Davide, and Stefano Moro.

*"Supervised molecular dynamics (SuMD) as a helpful tool to depict GPCR-ligand recognition pathway in a nanosecond time scale."*

Journal of Chemical Information and Modeling 54.2 (2014): 372-376.
