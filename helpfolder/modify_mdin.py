#!/usr/bin/env python3

import sys
import re


def modify_mdin(timestep_fs, time_window_ps, ntpr, ntwx, input_file):
    """
    Create common_prod.mdin from the chosen mdin template.

    Replaced Amber parameters:
    nstlim: number of MD steps in one SuMD window
    dt: timestep in ps
    ntpr: mdout print frequency in steps
    ntwx: trajectory writing frequency in steps
    """

    nstlim = int(time_window_ps * 1000 / timestep_fs)
    dt = round(timestep_fs / 1000, 3)

    with open(input_file, "r") as f:
        content = f.read()

    content = re.sub(r"nstlim\s*=\s*\d+", f"nstlim={nstlim}", content)
    content = re.sub(r"dt\s*=\s*\d+\.\d+", f"dt={dt}", content)
    content = re.sub(r"ntpr\s*=\s*\d+", f"ntpr={ntpr}", content)
    content = re.sub(r"ntwx\s*=\s*\d+", f"ntwx={ntwx}", content)

    with open("common_prod.mdin", "w") as f:
        f.write(content)

    print("Created common_prod.mdin")
    print(f"nstlim = {nstlim}")
    print(f"dt     = {dt}")
    print(f"ntpr   = {ntpr}")
    print(f"ntwx   = {ntwx}")


def main():
    if len(sys.argv) != 6:
        print("Usage: python modify_mdin.py TIMESTEP_FS TIME_WINDOW_PS MDOUTSTEP TRAJOUTSTEP INPUT_MDIN_FILE")
        sys.exit(1)

    timestep_fs = int(sys.argv[1])
    time_window_ps = int(sys.argv[2])
    ntpr = int(sys.argv[3])
    ntwx = int(sys.argv[4])
    input_file = sys.argv[5]

    modify_mdin(timestep_fs, time_window_ps, ntpr, ntwx, input_file)


if __name__ == "__main__":
    main()
