# supervisedmdamber.py

## User Guide and Reference Documentation

### Supervised Molecular Dynamics (SuMD) and Supervised Gaussian Accelerated MD (SuGaMD) for Amber

Amber implementation by Midhun K Madhu

---

# Purpose

This document explains what the `supervisedmdamber.py` workflow does, how to prepare the working directory, how to choose parameters, how to run the script, and how to interpret the outputs. It is written for a new user who may not already know the SuMD workflow.

---

# Basic Run

```bash
supervisedmdamber.py -i input_parameters.txt
```

# Help

```bash
supervisedmdamber.py -h
supervisedmdamber.py --help
```

---

# Contents

1. Overview  
2. What the script does  
3. Required software  
4. Required folder structure  
5. Input parameter file  
6. Detailed parameter reference  
7. How to run  
8. Step-by-step internal workflow  
9. Output files  
10. How to monitor progress  
11. Common problems and checks  
Appendix A. Helper scripts  

---

# 1. Overview

`supervisedmdamber.py` is a Python driver script for running supervised molecular dynamics with Amber. It automates a repeated cycle of:

- Short MD simulations
- Trajectory fitting
- RMSD calculation
- Slope estimation
- Restart selection
- Duplicate branch removal
- Final trajectory creation

The current implementation uses ligand RMSD as the collective variable.

A lower ligand RMSD means that the ligand is closer to the reference bound pose.

The script can later be modified to use other collective variables such as:

- Ligand-pocket distances
- Contacts
- Angles
- Custom reaction coordinates

Reference method:

The SuMD approach was introduced by Sabbadin and Moro in 2014 for studying GPCR-ligand recognition pathways on nanosecond timescales. Their original implementation used ACEMD. This implementation adapts the workflow to Amber.

---

## 1.1 Method citation

Sabbadin, Davide, and Stefano Moro.

*"Supervised molecular dynamics (SuMD) as a helpful tool to depict GPCR-ligand recognition pathway in a nanosecond time scale."*

Journal of Chemical Information and Modeling 54.2 (2014): 372-376.

---

## 1.2 Amber implementation

The Amber implementation script supports:

- cMD supervised workflows
- GaMD supervised workflows
- RMSD-based collective variables
- Slope and CV tracking
- Duplicate branch detection
- Combined supervised trajectory generation

---

# 2. What the script does

Instead of running one very long trajectory, the script runs many short trajectories.

After each short window, the workflow checks whether the ligand has moved in a useful direction toward the reference bound pose.

This is decided from the RMSD trend during the window.

Main workflow logic:

- If ligand RMSD improves, the next window continues from the latest restart
- If ligand RMSD worsens, the script can revert to the previous restart
- If RMSD falls below cutoff and slope is non-positive, the run converges
- Duplicate trajectory branches are automatically removed
- A final combined supervised trajectory is generated

---

## 2.1 Main decision quantities

| Quantity | Meaning | How it is used |
|---|---|---|
| CV value | Final RMSD value from current trajectory window | Compared with `COLVARCUT` |
| Slope | Linear regression slope of RMSD | Indicates productive or unproductive movement |
| COLVARCUT | Convergence cutoff | Stops run when `CV < COLVARCUT and slope <= 0` |

---

# 3. Required software

| Software | Required? | Purpose |
|---|---|---|
| Python 3 | Required | Runs workflow and helper scripts |
| NumPy | Required | Numerical processing |
| SciPy | Required | Linear regression |
| Amber | Required | Provides MD engines and cpptraj |
| cpptraj | Required | Trajectory fitting and RMSD analysis |
| MPI launcher | Only for `pmemd.MPI` | MPI execution |

Example MPI prefix:

```text
MPIPREFIX="mpirun -np 16"
```

---

## GaMD requirement

For:

```text
METHOD=GaMD
```

the file:

```text
gamd-restart.dat
```

must already exist in the working directory.

---

# 4. Required folder structure

```text
SuMD_sample_runfolder/
│
├── supervisedmdamber.py
├── input_parameters.txt
├── check.parm7
├── equil_1.rst7
├── test.pdb
├── gamd-restart.dat
│
└── RunMDSupervised/
    ├── create_traj.py
    ├── create_unique_starting_points.py
    ├── delete_extra_nc_files.py
    ├── extract_and_fit.py
    ├── extract_first_MDOUTline.py
    ├── generate_calcCPPIN.py
    ├── generate_fitCPPIN.py
    ├── log_creater.py
    ├── modify_mdin.py
    ├── suGamd.mdin
    └── sumd.mdin
```

---

## 4.1 Files needed before starting

| File or folder | Required? | Description |
|---|---|---|
| supervisedmdamber.py | Required | Main workflow driver |
| input_parameters.txt | Required | Main parameter file |
| check.parm7 | Required | Amber topology |
| equil_1.rst7 | Required | Initial restart |
| test.pdb | Required | Reference structure |
| gamd-restart.dat | Required for GaMD | GaMD restart statistics |
| RunMDSupervised/ | Required | Helper scripts |

---

## 4.2 Files generated automatically

Generated files include:

```text
fit.cppin
calc_rmsd.cppin
common_prod.mdin
prod_N.nc
prod_N.mdout
prod_N.rst7
prod_ligandRMSD_N.xvg
prod_slope_N.dat
prod_cvval_N.dat
sumd.log
sumdprogress.log
concat.cppin
```

Old generated files are automatically backed up with timestamps.

Example:

```text
additional_data.20260506_143012
sumdprogress.log.20260506_143012
```

---

# 5. Input parameter file

Example:

```text
&parameters
CPPTRAJ="cpptraj.OMP.cuda",
AMBEREXE="pmemd.cuda",
METHOD=GaMD,
TIME_WINDOW_PS=600,
COLVARCUT=2,
TIMESTEP_FS=2,
MDOUTSTEP=100,
TRAJOUTSTEP=500,
MAXSTEP=5000,
INPUT_MDIN_FILE="suGamd.mdin",
AMBER_PARAMETER_FILE="check.parm7",
RESTART_FILE="equil_1.rst7",
TRAJOUTNAME="traj.nc",
PDBALIGN="test.pdb",
FIT_TRAJ_STRING="1-313@CA",
FIT_PDB_STRING="1-313@CA",
CALCRMSD_TRAJ_STRING="314&!@H=",
CALCRMSD_PDB_STRING="314&!@H=:",
/
```

---

## 5.1 MPI example

```text
AMBEREXE="pmemd.MPI",
MPIPREFIX="mpirun -np 16",
```

---

# 6. Detailed parameter reference

| Parameter | Explanation |
|---|---|
| CPPTRAJ | cpptraj executable |
| AMBEREXE | Amber MD executable |
| MPIPREFIX | MPI launcher prefix |
| METHOD | cMD or GaMD |
| TIME_WINDOW_PS | Length of each MD window |
| COLVARCUT | RMSD convergence cutoff |
| TIMESTEP_FS | MD timestep |
| MDOUTSTEP | ntpr frequency |
| TRAJOUTSTEP | ntwx frequency |
| MAXSTEP | Maximum supervised cycles |
| INPUT_MDIN_FILE | mdin template |
| AMBER_PARAMETER_FILE | Amber topology |
| RESTART_FILE | Initial restart |
| TRAJOUTNAME | Final trajectory name |
| PDBALIGN | Reference structure |
| FIT_TRAJ_STRING | Fitting mask |
| FIT_PDB_STRING | Reference fitting mask |
| CALCRMSD_TRAJ_STRING | RMSD trajectory mask |
| CALCRMSD_PDB_STRING | RMSD reference mask |

---

# 7. How to run

## 7.1 Basic command

```bash
chmod +x supervisedmdamber.py
```

```bash
./supervisedmdamber.py -i input_parameters.txt
```

or

```bash
python supervisedmdamber.py -i input_parameters.txt
```

---

## 7.2 Help command

```bash
./supervisedmdamber.py -h
```

```bash
./supervisedmdamber.py --help
```

---

## 7.3 Running on a cluster

Example:

```bash
#!/bin/bash
#SBATCH -A naiss2025-3-21
#SBATCH -p tetralith
#SBATCH -t 24:00:00
#SBATCH -J sumd
#SBATCH --nodes=3
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=1
#SBATCH -o sumd-%j.out
#SBATCH -e sumd-%j.err

module load Amber/24-nsc1-gcccuda-12.2-g11-hpc1

unset PYTHONPATH
source /proj/carlssonlab/users/x_midma/miniforge3/etc/profile.d/conda.sh
conda activate ae-ml

python supervisedmdamber.py -i input_parameters.txt
```

Important:

Do not run the script from inside `RunMDSupervised/`.

Run it from the parent working directory.

---

# 8. Step-by-step internal workflow

1. Read input parameters  
2. Backup old generated files  
3. Initialize logs  
4. Generate cpptraj scripts  
5. Generate `common_prod.mdin`  
6. Run first Amber window  
7. Perform trajectory fitting  
8. Calculate ligand RMSD  
9. Estimate RMSD slope and CV  
10. Detect duplicate branches  
11. Remove duplicate trajectories  
12. Construct supervised trajectory  
13. Select next restart  
14. Repeat until convergence or `MAXSTEP`  

---

## 8.1 Decision logic

```text
If CV < COLVARCUT and slope <= 0:
    stop successfully

Else if step > MAXSTEP:
    stop because maximum cycles were reached

Else if slope <= 0 or (slope > 0 and CV < COLVARCUT):
    continue from restart.rst7

Else:
    continue from prev_restart.rst7
```

---

# 9. Output files

## 9.1 Main outputs

| Output | Meaning |
|---|---|
| traj.nc | Final supervised trajectory |
| sumdprogress.log | Full progress log |
| sumd.log | Compact CV/slope summary |
| additional_data/ | Per-iteration analysis storage |

---

## 9.2 Per-iteration outputs

| Pattern | Meaning |
|---|---|
| prod_N.nc | Trajectory for iteration N |
| prod_N.mdout | Amber output |
| prod_N.rst7 | Restart file |
| prod_ligandRMSD_N.xvg | RMSD trace |
| prod_slope_N.dat | RMSD slope |
| prod_cvval_N.dat | Final CV |
| prod_gamd_N.log | GaMD boost log |

---

## 9.3 Tracking and bookkeeping outputs

| File | Meaning |
|---|---|
| all_starting_points.dat | All starting points |
| unique_starting_points.dat | Unique accepted branches |
| duplicates_output.txt | Duplicate branches |
| concat.cppin | Final trajectory concatenation script |

---

# 10. How to monitor progress

Live monitoring:

```bash
tail -f sumdprogress.log
```

Compact summary:

```bash
cat sumd.log
```

Example:

```text
STEP = 1    SLOPE = -0.0345    CV VALUE = 8.4123
STEP = 2    SLOPE = -0.0181    CV VALUE = 7.9322
```

---

# 11. Common problems and checks

## 11.1 GaMD fails immediately

Likely cause:

```text
gamd-restart.dat
```

is missing or incompatible.

---

## 11.2 cpptraj mask errors

Check:

```text
FIT_TRAJ_STRING
FIT_PDB_STRING
CALCRMSD_TRAJ_STRING
CALCRMSD_PDB_STRING
```

Verify residue numbering carefully.

---

## 11.3 No convergence

Possible solutions:

- Increase `MAXSTEP`
- Increase `TIME_WINDOW_PS`
- Relax `COLVARCUT`
- Verify reference structure
- Consider GaMD instead of cMD

---

## 11.4 Wrong executable

Check:

```bash
which pmemd.cuda
which pmemd.MPI
which cpptraj
```

---

## 11.5 Old files disappearing

Old generated files are automatically backed up with timestamp suffixes.

Example:

```text
sumdprogress.log.20260506_143012
```

---

# Appendix A. Helper scripts

| Script | Purpose |
|---|---|
| generate_fitCPPIN.py | Generate fitting cpptraj script |
| generate_calcCPPIN.py | Generate RMSD cpptraj script |
| modify_mdin.py | Modify mdin template |
| extract_and_fit.py | Calculate slope and CV |
| log_creater.py | Generate compact logs |
| extract_first_MDOUTline.py | Extract mdout starting points |
| create_unique_starting_points.py | Remove duplicate branches |
| delete_extra_nc_files.py | Remove duplicate trajectories |
| create_traj.py | Generate concatenated trajectory |

---

# mdin templates

| File | Purpose |
|---|---|
| suGamd.mdin | GaMD template |
| sumd.mdin | cMD template |
