#!/usr/bin/env python3

import sys


def extract_unique_last_value(input_file, output_file, duplicates_file):
    """
    Read all_starting_points.dat.

    Column 1: iteration number
    Column 2: collective variable value

    If the same CV value appears more than once, keep only the latest line.
    Older duplicate lines are written to duplicates_output.txt.
    """

    unique_values = {}
    duplicate_lines = []

    with open(input_file, "r") as f:
        for line in f:
            parts = line.strip().split()

            if len(parts) != 2:
                continue

            step = int(parts[0])
            cv_value = float(parts[1])

            if cv_value in unique_values:
                duplicate_lines.append(unique_values[cv_value])

            unique_values[cv_value] = line

    with open(output_file, "w") as out:
        for line in unique_values.values():
            out.write(line)

    with open(duplicates_file, "w") as dup:
        for line in duplicate_lines:
            dup.write(line)


def check_duplicate_lines(file1, file2):
    """
    Sanity check that the unique file and duplicate file do not share lines.
    """

    with open(file1, "r") as f1:
        lines1 = set(f1.readlines())

    with open(file2, "r") as f2:
        lines2 = set(f2.readlines())

    common = lines1.intersection(lines2)

    if common:
        print("Warning: duplicate lines found between unique and duplicate files:")
        for line in common:
            print(line.strip())
    else:
        print("No duplicate lines found between unique and duplicate files.")


def main():
    if len(sys.argv) != 4:
        print("Usage: python create_unique_starting_points.py all_starting_points.dat unique_starting_points.dat duplicates_output.txt")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    duplicates_file = sys.argv[3]

    extract_unique_last_value(input_file, output_file, duplicates_file)
    check_duplicate_lines(output_file, duplicates_file)

    print("Starting-point files processed successfully.")


if __name__ == "__main__":
    main()
