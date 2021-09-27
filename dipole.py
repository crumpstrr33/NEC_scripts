"""
Running `python dipole.py` creates a .nec file for a dipole antenna. It uses
the following parameters:

    origin: The (x,y,z) point about which it is centered
    length: Half the total length of the dipole along the axis
"""
from typing import Sequence

from build_nec_file import build_nec_file

length = 0.13
wire_rad = 0.001
origin = (0.0, 0.0, 0.0)

ex_tag = 1

CONSTANTS = {
    "originx": origin[0],
    "originy": origin[1],
    "originz": origin[2],
    "length": length,
    "wire_rad": wire_rad,
}

COMMENTS = [
    "Dipole made with dipole.py",
    f"Origin: ({origin[0]:.3f}, {origin[1]:.3f}, {origin[2]:.3f})",
    f"Dipole half length: {length:.3f} meters",
]

FREQUENCY = ["0", "200", "0", "0", "5", "5"]
RADIATION = ["0", "91", "181", "1000", "0", "0", "2", "2"]
EXCITATIONS = [["0", f"{ex_tag}", "1", "00", "1", "0"]]


def build_dipole(axis: str) -> Sequence[Sequence[str]]:
    if axis not in ["x", "y", "z"]:
        raise f"Please set axis to `x`, `y` or `z`, not {axis}."

    return [
        [
            "1",
            f"originx{' - length' if axis == 'x' else ''}",
            f"originy{' - length' if axis == 'y' else ''}",
            f"originz{' - length' if axis == 'z' else ''}",
            f"originx{' + length' if axis == 'x' else ''}",
            f"originy{' + length' if axis == 'y' else ''}",
            f"originz{' + length' if axis == 'z' else ''}",
            "wire_rad",
        ]
    ]


if __name__ == "__main__":
    WIRES = build_dipole("z")

    build_nec_file(
        comments=COMMENTS,
        wires=WIRES,
        constants=CONSTANTS,
        excitations=EXCITATIONS,
        rad_pattern=RADIATION,
        frequency=FREQUENCY,
        output="dipoletest",
        # lims=lim_lens,
        sig_figs=2,
        verbose=1,
    )
