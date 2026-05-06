#!/usr/bin/env python3

import sys


def generate_fit_cppin(amber_parameter_file, pdb_reference, traj_atoms, pdb_atoms):
    """
    Generate fit.cppin.

    This cpptraj script:
    1. Reads temp1.nc.
    2. Autoimages the trajectory.
    3. Fits the trajectory to the reference PDB using protein atoms.
    4. Writes the fitted trajectory as temp2.nc.
    """

    return f"""\
parm {amber_parameter_file}
trajin temp1.nc

autoimage

parm {pdb_reference}
reference {pdb_reference} parm {pdb_reference} [SYS_PDB]
rms To_SYS_PDB ref [SYS_PDB] :{traj_atoms} :{pdb_atoms} out proteinFitRMSD.xvg time 0.01
trajout temp2.nc

run
"""


def main():
    if len(sys.argv) != 5:
        print("Usage: python generate_fitCPPIN.py amber.parm7 reference.pdb traj_atoms pdb_atoms")
        sys.exit(1)

    amber_parameter_file = sys.argv[1]
    pdb_reference = sys.argv[2]
    traj_atoms = sys.argv[3]
    pdb_atoms = sys.argv[4]

    script = generate_fit_cppin(
        amber_parameter_file,
        pdb_reference,
        traj_atoms,
        pdb_atoms,
    )

    with open("fit.cppin", "w") as f:
        f.write(script)


if __name__ == "__main__":
    main()
