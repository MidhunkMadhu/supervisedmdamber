#!/usr/bin/env python3

import sys
import numpy as np
from scipy.stats import linregress


def extract_slope_and_cv(input_file, slope_file, cv_file):
    """
    Read ligandRMSD.xvg.

    The second column is the RMSD collective variable.
    Five points are selected across the time window.
    A linear fit is performed through those points.
    The slope and final CV value are written to output files.
    """

    data = np.loadtxt(input_file)
    n = len(data)

    x_indices = [
        0,
        int(n / 4) - 1,
        2 * int(n / 4) - 1,
        3 * int(n / 4) - 1,
        4 * int(n / 4) - 1,
    ]

    x = []
    y = []

    for i in range(n):
        cv = data[i][1]

        if i in x_indices:
            x.append(i)
            y.append(cv)

    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    final_cv = data[-1][1]

    with open(slope_file, "w") as f:
        print(f"{slope:.4f}", file=f)

    with open(cv_file, "w") as f:
        print(f"{final_cv:.4f}", file=f)


def main():
    if len(sys.argv) != 4:
        print("Usage: python extract_and_fit.py ligandRMSD.xvg slope.dat cvval.dat")
        sys.exit(1)

    extract_slope_and_cv(sys.argv[1], sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    main()
