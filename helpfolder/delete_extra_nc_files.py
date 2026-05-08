#!/usr/bin/env python3

import sys
import os


def delete_duplicate_nc_files(duplicates_file):
    """
    Read duplicates_output.txt and delete duplicate prod_N.nc files.

    The first column of duplicates_output.txt is assumed to be the
    SuMD iteration number N.
    """

    if not os.path.exists(duplicates_file):
        raise FileNotFoundError(f"{duplicates_file} not found")

    with open(duplicates_file, "r") as f:
        for line in f:
            parts = line.strip().split()

            if len(parts) == 0:
                continue

            step = parts[0]

            if not step.isdigit():
                continue

            nc_file = f"prod_{step}.nc"

            if os.path.exists(nc_file):
                print(f"Deleting duplicate trajectory: {nc_file}")
                os.remove(nc_file)


def main():
    if len(sys.argv) != 2:
        print("Usage: python delete_extra_nc_files.py duplicates_output.txt")
        sys.exit(1)

    delete_duplicate_nc_files(sys.argv[1])


if __name__ == "__main__":
    main()
