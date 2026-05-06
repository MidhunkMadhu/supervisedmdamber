#!/usr/bin/env python3

import sys


def generate_traj_commands(input_file, amber_param_file, traj_file):
    """
    Create concat.cppin for cpptraj.

    It reads unique_starting_points.dat and writes trajin commands only
    for accepted unique prod_N.nc trajectory files.
    """

    trajin_lines = []

    with open(input_file, "r") as f:
        for line in f:
            cols = line.strip().split()

            if len(cols) == 2 and cols[0].isdigit():
                trajin_lines.append(f"trajin prod_{cols[0]}.nc")

    with open("concat.cppin", "w") as f:
        f.write(f"parm {amber_param_file}\n")

        for line in trajin_lines:
            f.write(line + "\n")

        f.write(f"trajout {traj_file}\n")
        f.write("run\n")


def main():
    if len(sys.argv) != 4:
        print("Usage: python create_traj.py unique_starting_points.dat amber.parm7 traj.nc")
        sys.exit(1)

    input_file = sys.argv[1]
    amber_param_file = sys.argv[2]
    traj_file = sys.argv[3]

    generate_traj_commands(input_file, amber_param_file, traj_file)


if __name__ == "__main__":
    main()
