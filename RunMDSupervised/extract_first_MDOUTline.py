#!/usr/bin/env python3

import sys
import glob
import os


def extract_first_mdout_line(first_step):
    """
    Search all prod_*.mdout files for the first NSTEP line
    corresponding to FIRST_STEP.

    This version is spacing-independent, so it works even if Amber
    changes the number of spaces around NSTEP or TIME(PS).
    """

    first_step = int(first_step)

    mdout_files = sorted(glob.glob("prod_*.mdout"))

    for mdout_file in mdout_files:
        if not os.path.isfile(mdout_file):
            continue

        with open(mdout_file, "r", errors="ignore") as f:
            for line in f:
                if "NSTEP" not in line or "TIME(PS)" not in line:
                    continue

                parts = line.replace("=", " ").split()

                if "NSTEP" not in parts:
                    continue

                idx = parts.index("NSTEP")

                if idx + 1 >= len(parts):
                    continue

                try:
                    nstep = int(parts[idx + 1])
                except ValueError:
                    continue

                if nstep == first_step:
                    print(f"{os.path.basename(mdout_file)} {line.strip()}")
                    break


def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_first_MDOUTline.py FIRST_STEP")
        sys.exit(1)

    extract_first_mdout_line(sys.argv[1])


if __name__ == "__main__":
    main()
