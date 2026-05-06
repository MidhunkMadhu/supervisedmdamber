#!/usr/bin/env python3

import sys
import glob
import os


def extract_first_mdout_line(first_step):
    """
    Search all prod_*.mdout files for the first NSTEP line
    corresponding to FIRST_STEP.

    Output format matches the old bash script:

    prod_1.mdout NSTEP =      200 TIME(PS) = ...
    """

    search_string = f"NSTEP =      {first_step}"

    mdout_files = sorted(glob.glob("prod_*.mdout"))

    for mdout_file in mdout_files:
        if not os.path.isfile(mdout_file):
            continue

        with open(mdout_file, "r", errors="ignore") as f:
            for line in f:
                if search_string in line:
                    print(f"{os.path.basename(mdout_file)} {line.strip()}")
                    break


def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_first_MDOUTline.py FIRST_STEP")
        sys.exit(1)

    first_step = sys.argv[1]
    extract_first_mdout_line(first_step)


if __name__ == "__main__":
    main()
