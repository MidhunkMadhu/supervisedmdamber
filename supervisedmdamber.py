#!/usr/bin/env python3

import os
import sys
import glob
import shlex
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
RUN_DIR = SCRIPT_DIR / "helpfolder"
LOG_FILE = "sumdprogress.log"

INT_KEYS = ["TIME_WINDOW_PS", "TIMESTEP_FS", "MDOUTSTEP", "TRAJOUTSTEP", "MAXSTEP"]
FLOAT_KEYS = ["COLVARCUT"]

REQUIRED_KEYS = [
    "CPPTRAJ", "AMBEREXE", "METHOD", "INPUT_MDIN_FILE",
    "AMBER_PARAMETER_FILE", "RESTART_FILE", "TRAJOUTNAME", "PDBALIGN",
    "FIT_TRAJ_STRING", "FIT_PDB_STRING",
    "CALCRMSD_TRAJ_STRING", "CALCRMSD_PDB_STRING",
] + INT_KEYS + FLOAT_KEYS


def now_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def write_log(msg, mode="a"):
    with open(LOG_FILE, mode) as f:
        f.write(msg + "\n")


def print_and_log(msg):
    print(msg)
    write_log(msg)


def print_banner():
    banner = r"""
================================================================================
                     supervisedmdamber.py
================================================================================

Supervised Molecular Dynamics (SuMD) and Supervised Gaussian
Accelerated Molecular Dynamics (SuGaMD) driver for Amber.

SuMD methodology originally developed by:

Sabbadin, Davide, and Stefano Moro.
"Supervised molecular dynamics (SuMD) as a helpful tool to depict
GPCR-ligand recognition pathway in a nanosecond time scale."
Journal of Chemical Information and Modeling 54.2 (2014): 372-376.

Original implementation developed using ACEMD.

Amber implementation developed by:

Midhun K Madhu

Current implementation:
  - Supports cMD and GaMD workflows
  - Uses RMSD as collective variable
  - Tracks slope and collective variable values
  - Generates unique starting points
  - Removes duplicate trajectory branches
  - Creates combined supervised trajectories

Usage:
    supervisedmdamber -i input_parameters.txt

Help:
    supervisedmdamber -h
    supervisedmdamber --help
================================================================================
"""
    print(banner)
    write_log(banner)


def clean_value(val):
    return val.strip().rstrip(",").strip('"').strip("'")


def remove_path(path):
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)


def cleanup_old_generated_files(params):
    patterns = [
        LOG_FILE,
        "additional_data",
        "fit.cppin",
        "calc_rmsd.cppin",
        "concat.cppin",
        "common_prod.mdin",
        "restart.rst7",
        "prev_restart.rst7",
        "prod*",
        "temp1.nc",
        "temp2.nc",
        "ligandRMSD.xvg",
        "proteinFitRMSD.xvg",
        "slope.dat",
        "cvval.dat",
        "sumd.log",
        "first_MDOUTlines.dat",
        "all_starting_points_temp.dat",
        "all_starting_points.dat",
        "unique_starting_points.dat",
        "duplicates_output.txt",
        params["TRAJOUTNAME"],
    ]

    for pattern in patterns:
        for path in glob.glob(pattern):
            remove_path(path)

    write_log("=" * 80, mode="w")
    write_log(f"Run started at: {now_time()}")
    write_log("=" * 80)
    print_banner()

    Path("additional_data").mkdir(exist_ok=True)
    print_and_log("Created fresh additional_data directory")


def run_cmd(cmd, shell=False):
    cmd_string = cmd if isinstance(cmd, str) else " ".join(cmd)
    print_and_log("")
    print_and_log(f"[{now_time()}] Running command:")
    print_and_log(cmd_string)
    subprocess.run(cmd, shell=shell, check=True)


def read_input_parameters(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} not found")

    params = {}

    with open(filename) as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#") or line.startswith("&") or line == "/":
                continue

            if "=" not in line:
                continue

            key, val = line.split("=", 1)
            params[key.strip()] = clean_value(val)

    missing = [k for k in REQUIRED_KEYS if k not in params]

    if missing:
        raise ValueError("Missing parameters:\n" + "\n".join(missing))

    if params["AMBEREXE"] == "pmemd.MPI" and "MPIPREFIX" not in params:
        raise ValueError(
            "AMBEREXE is pmemd.MPI, so MPIPREFIX is required.\n"
            "Example: MPIPREFIX=\"mpirun -np 16\""
        )

    return params


def log_parameters(params):
    print_and_log("")
    print_and_log("INPUT PARAMETERS")
    print_and_log("-" * 80)

    for key in sorted(params.keys()):
        print_and_log(f"{key} = {params[key]}")


def to_int(params, key):
    val = params[key]

    if "." in val:
        raise ValueError(f"{key} must be integer, got {val}")

    return int(val)


def to_float(params, key):
    return float(params[key])


def check_file(path, label):
    if not os.path.exists(path):
        raise FileNotFoundError(f"{label} missing: {path}")


def check_helper_folder():
    if not RUN_DIR.exists():
        raise FileNotFoundError(f"helpfolder missing: {RUN_DIR}")

    required_helpers = [
        "generate_fitCPPIN.py",
        "generate_calcCPPIN.py",
        "modify_mdin.py",
        "extract_and_fit.py",
        "log_creater.py",
        "extract_first_MDOUTline.py",
        "create_unique_starting_points.py",
        "delete_extra_nc_files.py",
        "create_traj.py",
    ]

    missing = [str(RUN_DIR / f) for f in required_helpers if not (RUN_DIR / f).exists()]

    if missing:
        raise FileNotFoundError(
            "Missing helper scripts:\n" + "\n".join(missing)
        )


def safe_copy(src, dst):
    check_file(src, "copy source")
    shutil.copy(src, dst)


def safe_move(src, dst):
    check_file(src, "move source")
    shutil.move(src, dst)


def safe_remove(*files):
    for f in files:
        if os.path.exists(f):
            remove_path(f)


def read_float_file(path):
    check_file(path, "numeric file")
    return float(open(path).read().strip())


def make_amber_command(exe, mpiprefix):
    if exe == "pmemd.MPI":
        return shlex.split(mpiprefix) + [exe]

    return [exe]


def run_amber(exe, mpiprefix, method, parm, rst, step):
    check_file(parm, "parm7")
    check_file(rst, "restart")
    check_file("common_prod.mdin", "mdin")

    base = make_amber_command(exe, mpiprefix) + [
        "-O",
        "-i", "common_prod.mdin",
        "-o", "prod.mdout",
        "-p", parm,
        "-c", rst,
        "-r", "prod.rst7",
        "-x", "prod.nc",
        "-inf", "prod.mdinfo",
    ]

    print_and_log("")
    print_and_log("=" * 80)
    print_and_log(f"ITERATION {step}")
    print_and_log("=" * 80)
    print_and_log(f"Amber executable = {exe}")
    print_and_log(f"MPI prefix = {mpiprefix}")
    print_and_log(f"Method = {method}")
    print_and_log(f"Restart file used = {rst}")
    print_and_log(f"Full Amber command = {' '.join(base)}")

    if method == "GaMD":
        run_cmd(base + ["-gamd", "prod_gamd.log"])
        safe_move("prod_gamd.log", f"prod_gamd_{step}.log")

    elif method == "cMD":
        run_cmd(base)

    else:
        raise ValueError("METHOD must be GaMD or cMD")


def process_outputs(step, cpptraj):
    safe_copy("prod.nc", "temp1.nc")

    safe_move("prod.mdout", f"prod_{step}.mdout")
    safe_move("prod.rst7", f"prod_{step}.rst7")
    safe_move("prod.nc", f"prod_{step}.nc")

    safe_copy(f"prod_{step}.mdout", "./additional_data")

    run_cmd([cpptraj, "-i", "fit.cppin"])
    run_cmd([cpptraj, "-i", "calc_rmsd.cppin"])

    run_cmd([
        sys.executable,
        str(RUN_DIR / "extract_and_fit.py"),
        "ligandRMSD.xvg",
        "slope.dat",
        "cvval.dat",
    ])

    slope = read_float_file("slope.dat")
    cv = read_float_file("cvval.dat")

    safe_move("ligandRMSD.xvg", f"prod_ligandRMSD_{step}.xvg")
    safe_move("slope.dat", f"prod_slope_{step}.dat")
    safe_move("cvval.dat", f"prod_cvval_{step}.dat")

    print_and_log("")
    print_and_log(f"Iteration {step} analysis completed")
    print_and_log(f"Collective variable value = {cv}")
    print_and_log(f"Slope = {slope}")

    return slope, cv


def update_starting_points_and_trajectory(parm, trajoutname, first_step):
    print_and_log("")
    print_and_log("Updating starting points and combined trajectory")

    slope_files = sorted(glob.glob("prod_slope_*.dat"))

    if slope_files:
        run_cmd([sys.executable, str(RUN_DIR / "log_creater.py")] + slope_files)

    run_cmd(
        f"{shlex.quote(sys.executable)} {shlex.quote(str(RUN_DIR / 'extract_first_MDOUTline.py'))} "
        f"{first_step} > first_MDOUTlines.dat",
        shell=True,
    )

    run_cmd(
        "awk -F'.mdout' '{print $1\" \"$2}' first_MDOUTlines.dat | "
        "awk -F'_' '{print $2\" \"$3}' | "
        "awk '{print $1\" \"$7}' | "
        "sort -n -k1 > all_starting_points_temp.dat",
        shell=True,
    )

    run_cmd(
        "awk 'NF > 0' all_starting_points_temp.dat > all_starting_points.dat",
        shell=True,
    )

    run_cmd([
        sys.executable,
        str(RUN_DIR / "create_unique_starting_points.py"),
        "all_starting_points.dat",
        "unique_starting_points.dat",
        "duplicates_output.txt",
    ])

    safe_remove("first_MDOUTlines.dat", "all_starting_points_temp.dat")

    run_cmd([
        sys.executable,
        str(RUN_DIR / "delete_extra_nc_files.py"),
        "duplicates_output.txt",
    ])

    safe_remove(trajoutname)

    run_cmd([
        sys.executable,
        str(RUN_DIR / "create_traj.py"),
        "unique_starting_points.dat",
        parm,
        trajoutname,
    ])

    print_and_log("Updated all_starting_points.dat")
    print_and_log("Updated unique_starting_points.dat")
    print_and_log("Updated duplicates_output.txt")
    print_and_log(f"Updated combined trajectory = {trajoutname}")


def move_final_outputs_to_additional_data():
    print_and_log("")
    print_and_log("Moving final analysis/output files to additional_data")

    patterns = [
        "common_prod.mdin",
        "prod_*.mdout",
        "prod_*.rst7",
        "prod_ligandRMSD_*.xvg",
        "prod_slope_*.dat",
        "prod_cvval_*.dat",
        "prod_gamd_*.log",
        "duplicates_output.txt",
        "unique_starting_points.dat",
        "all_starting_points.dat",
        "concat.cppin",
        "sumd.log",
    ]

    for pattern in patterns:
        for f in glob.glob(pattern):
            if os.path.exists(f):
                dst = Path("additional_data") / Path(f).name

                if dst.exists():
                    remove_path(dst)

                shutil.move(f, dst)
                print_and_log(f"Moved {f} -> {dst}")


def main():
    parser = argparse.ArgumentParser(
        prog="supervisedmdamber",
        description="Supervised Molecular Dynamics driver for Amber",
        usage="supervisedmdamber -i input_parameters.txt",
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input parameter file",
    )

    args = parser.parse_args()

    check_helper_folder()

    params = read_input_parameters(args.input)

    cleanup_old_generated_files(params)
    log_parameters(params)

    numeric_int = {k: to_int(params, k) for k in INT_KEYS}
    numeric_float = {k: to_float(params, k) for k in FLOAT_KEYS}

    timestep_fs = numeric_int["TIMESTEP_FS"]
    mdoutstep = numeric_int["MDOUTSTEP"]
    trajoutstep = numeric_int["TRAJOUTSTEP"]
    max_step = numeric_int["MAXSTEP"]
    time_window_ps = numeric_int["TIME_WINDOW_PS"]
    first_step = mdoutstep * timestep_fs
    cut = numeric_float["COLVARCUT"]

    cpptraj = params["CPPTRAJ"]
    amberexe = params["AMBEREXE"]
    mpiprefix = params.get("MPIPREFIX", "")
    method = params["METHOD"]
    input_mdin = params["INPUT_MDIN_FILE"]
    parm = params["AMBER_PARAMETER_FILE"]
    restart = params["RESTART_FILE"]
    pdbalign = params["PDBALIGN"]
    trajoutname = params["TRAJOUTNAME"]

    print_and_log("")
    print_and_log("Parameters loaded successfully")
    print_and_log(f"AMBEREXE = {amberexe}")
    print_and_log(f"MPIPREFIX = {mpiprefix}")
    print_and_log(f"METHOD = {method}")
    print_and_log(f"TIME_WINDOW_PS = {time_window_ps}")
    print_and_log(f"COLVARCUT = {cut}")
    print_and_log(f"TIMESTEP_FS = {timestep_fs}")
    print_and_log(f"MDOUTSTEP = {mdoutstep}")
    print_and_log(f"TRAJOUTSTEP = {trajoutstep}")
    print_and_log(f"MAXSTEP = {max_step}")
    print_and_log(f"FIRST_STEP = {first_step}")
    print_and_log(f"Final trajectory = {trajoutname}")
    print_and_log(f"Helper folder = {RUN_DIR}")
    print_and_log(f"Python executable = {sys.executable}")

    run_cmd([
        sys.executable,
        str(RUN_DIR / "generate_fitCPPIN.py"),
        parm,
        pdbalign,
        params["FIT_TRAJ_STRING"],
        params["FIT_PDB_STRING"],
    ])

    run_cmd([
        sys.executable,
        str(RUN_DIR / "generate_calcCPPIN.py"),
        parm,
        pdbalign,
        params["CALCRMSD_TRAJ_STRING"],
        params["CALCRMSD_PDB_STRING"],
    ])

    run_cmd([
        sys.executable,
        str(RUN_DIR / "modify_mdin.py"),
        str(timestep_fs),
        str(time_window_ps),
        str(mdoutstep),
        str(trajoutstep),
        input_mdin,
    ])

    step = 1

    run_amber(amberexe, mpiprefix, method, parm, restart, step)

    safe_copy("prod.rst7", "restart.rst7")
    safe_copy(restart, "prev_restart.rst7")

    slope, cv = process_outputs(step, cpptraj)

    update_starting_points_and_trajectory(parm, trajoutname, first_step)

    while True:
        safe_remove("temp1.nc", "temp2.nc")

        step += 1

        print_and_log("")
        print_and_log("-" * 80)
        print_and_log(f"Preparing decision for iteration {step}")
        print_and_log(f"Previous CV = {cv}")
        print_and_log(f"Previous slope = {slope}")
        print_and_log(f"CV cutoff = {cut}")

        if cv < cut and slope <= 0:
            print_and_log("Stopping condition met")
            print_and_log(f"Reason: CV {cv} < cutoff {cut} and slope {slope} <= 0")
            break

        if step > max_step:
            print_and_log("Reached MAXSTEP")
            print_and_log(f"Maximum allowed iteration was {max_step}")
            break

        if slope <= 0 or (slope > 0 and cv < cut):
            print_and_log("Next restart decision: using restart.rst7")
            run_amber(amberexe, mpiprefix, method, parm, "restart.rst7", step)
            safe_copy("restart.rst7", "prev_restart.rst7")
            safe_copy("prod.rst7", "restart.rst7")

        else:
            print_and_log("Next restart decision: using prev_restart.rst7")
            run_amber(amberexe, mpiprefix, method, parm, "prev_restart.rst7", step)
            safe_copy("prod.rst7", "restart.rst7")

        slope, cv = process_outputs(step, cpptraj)

        update_starting_points_and_trajectory(parm, trajoutname, first_step)

    safe_remove("temp1.nc", "temp2.nc", "prev_restart.rst7", "restart.rst7")

    slope_files = sorted(glob.glob("prod_slope_*.dat"))

    if slope_files:
        run_cmd([sys.executable, str(RUN_DIR / "log_creater.py")] + slope_files)

    if os.path.exists("concat.cppin"):
        run_cmd([cpptraj, "-i", "concat.cppin"])

    move_final_outputs_to_additional_data()

    print_and_log("")
    print_and_log("=" * 80)
    print_and_log(f"Run finished at: {now_time()}")
    print_and_log("Run finished successfully")
    print_and_log("=" * 80)


if __name__ == "__main__":
    main()
