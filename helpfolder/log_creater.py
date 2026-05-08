#!/usr/bin/env python3

import sys
import numpy as np


def get_step_number(filename):
    """
    Extract step number from prod_slope_N.dat.
    """

    stem = filename.split(".")[0]
    return int(stem.split("_")[-1])


def create_log(filenames):
    """
    Create sumd.log with step, slope, and CV value.
    """

    step_numbers = sorted(get_step_number(f) for f in filenames)

    with open("sumd.log", "w") as out:
        for i, step in enumerate(step_numbers, start=1):
            slope_file = f"prod_slope_{step}.dat"
            cv_file = f"prod_cvval_{step}.dat"

            slope = np.loadtxt(slope_file)
            cv = np.loadtxt(cv_file)

            print(
                "STEP = %d\tSLOPE = %.4f\tCV VALUE = %.4f" % (i, slope, cv),
                file=out,
            )


def main():
    filenames = sys.argv[1:]

    if not filenames:
        print("Usage: python log_creater.py prod_slope_*.dat")
        sys.exit(1)

    create_log(filenames)


if __name__ == "__main__":
    main()
