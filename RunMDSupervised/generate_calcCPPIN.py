#!/usr/bin/env python3

import sys


def generate_calc_rmsd_cppin(amber_parameter_file, pdb_reference, traj_atoms, pdb_atoms):
    """
    Generate calc_rmsd.cppin.

    This cpptraj script calculates RMSD of the selected CV atoms after
    the fitted trajectory temp2.nc has already been generated.
    """

    return f"""\
parm {amber_parameter_file}
trajin temp2.nc

parm {pdb_reference}
reference {pdb_reference} parm {pdb_reference} [SYS_PDB]
rms To_SYS_PDB ref [SYS_PDB] :{traj_atoms} :{pdb_atoms} out ligandRMSD.xvg time 0.01 nofit

run
"""


def main():
    if len(sys.argv) != 5:
        print("Usage: python generate_calcCPPIN.py amber.parm7 reference.pdb traj_atoms pdb_atoms")
        sys.exit(1)

    amber_parameter_file = sys.argv[1]
    pdb_reference = sys.argv[2]
    traj_atoms = sys.argv[3]
    pdb_atoms = sys.argv[4]

    script = generate_calc_rmsd_cppin(
        amber_parameter_file,
        pdb_reference,
        traj_atoms,
        pdb_atoms,
    )

    with open("calc_rmsd.cppin", "w") as f:
        f.write(script)


if __name__ == "__main__":
    main()
