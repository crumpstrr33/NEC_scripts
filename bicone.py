"""
Running `python bicone.py` creates a .nec file for a bicone antenna. It uses
the following parameters:

    origin: The (x,y,z) point about which it is centered
    cone_offset: How far from the center the cone starts
    num_rays: How fine of a circle the cone is, `n` rays would mean a n-gon
                representation of the circle
    num_rings: How dense the cone is with wire, since NEC can't model planes,
                this representes how many rings along the axis make up the cone
    theta: The angle of the cone, at >pi/4, the cone could intersect with other
            cones (if there are multiple bicones present)
    length: The length of the cone along the axis
    init_rad: The inital radius of the cone (since it doesn't start at an exact point
                like a cone mathematically would do)
"""
import os
from math import pi

from build_nec_file import build_nec_file

cone_offset = 0.004
num_rays = 20
num_rings = 20
theta = 40 * (pi / 180)  # In degrees to be converted
length = 0.13
init_rad = 0.007
wire_rad = 0.001
origin = (0.0, 0.0, 0.0)

ex_tag = 9999

CONSTANTS = {
    "originx": origin[0],
    "originy": origin[1],
    "originz": origin[2],
    "cone_offset": cone_offset,
    "num_rays": num_rays,
    "num_rings": num_rings,
    "theta": theta,
    "length": length,
    "init_rad": init_rad,
    "wire_rad": wire_rad,
}

COMMENTS = [
    "Bicone made with bicone.py",
    f"Origin: ({origin[0]:.3f}, {origin[1]:.3f}, {origin[2]:.3f})",
    f"Cone offset: {cone_offset:.3f} meters",
    f"Cone angle: {theta:.3f} radians",
    f"Cone length: {length:.3f} meters",
    f"Number of rings: {num_rings}",
    f"Number of rays: {num_rays}",
    f"Cone initial radius: {init_rad:.3f} meters",
]

INIT_WIRE = [
    [
        f"{ex_tag}",
        "1",
        "0",
        "init_rad",
        "originz + cone_offset",
        "0",
        "init_rad",
        "originz - cone_offset",
        "wire_rad",
    ],
]

FREQUENCY = ["0", "200", "0", "0", "5", "5"]
RADIATION = ["0", "91", "181", "1000", "0", "0", "2", "2"]
EXCITATIONS = [["0", f"{ex_tag}", "1", "00", "1", "0"]]


def build_cone(axis, parity, wires=[]):
    """
    Creates a cone in a direction along an axis.

    Parameters:
    axis - The axis which the cone is along, either `x`, `y`, `z`
    partiy - Which direction to face, either 0 for negative or 1 for positive
    wires (default []) - The list of wires to add to
    """
    # Do not edit in-place! Instead return the list of wires!
    _wires = wires.copy()
    if parity not in [0, 1]:
        raise f"Please set parity to `1` or `0`, not {parity}."
    if axis not in ["x", "y", "z"]:
        raise f"Please set axis to `x`, `y` or `z`, not {axis}."

    neg = 1 if parity else -1
    # Determine which of the x, y and z axes are the primary axis/secondary axes
    # Primary axes is that which the cone is symmetric about
    x = 0 if axis == "x" else 1 if axis == "y" else 2
    y = 2 if axis == "x" else 0 if axis == "y" else 1
    z = 1 if axis == "x" else 2 if axis == "y" else 0

    # Change in angle between rays
    dtheta = 2 * pi / num_rays
    # Change in length between rings
    dlength = length / (num_rings - 1)

    # Add the rays, create num_rings-1 wires for each ray, so each interaction
    # point is of 4 wires. The offset*tan(theta) term compensates for the increase
    # in height along the ray, the cosine and sine terms then appropriately rotate them
    for ring_ind in range(num_rings - 1):
        offsets = (f"{ring_ind * dlength}", f"{(ring_ind + 1) * dlength}")
        for ray_ind in range(num_rays):
            prim_axis = (
                f"{neg}*(cone_offset + {offsets[0]})",
                f"{neg}*(cone_offset + {offsets[1]})",
            )
            sec1_axis = (
                f"({offsets[0]}*tan(theta) + init_rad)*cos({ray_ind*dtheta})",
                f"({offsets[1]}*tan(theta) + init_rad)*cos({ray_ind*dtheta})",
            )
            sec2_axis = (
                f"({offsets[0]}*tan(theta) + init_rad)*sin({ray_ind*dtheta})",
                f"({offsets[1]}*tan(theta) + init_rad)*sin({ray_ind*dtheta})",
            )
            axes = (prim_axis, sec1_axis, sec2_axis)

            _wires.append(
                [
                    str(len(_wires)),  # Tag
                    "1",  # Number of segments
                    "originx +" + axes[x][0],  # x init
                    "originy +" + axes[y][0],  # y init
                    "originz +" + axes[z][0],  # z init
                    "originx +" + axes[x][1],  # x final
                    "originy +" + axes[y][1],  # y final
                    "originz +" + axes[z][1],  # z final
                    "wire_rad",  # Wire radius
                ]
            )

    # Connects rays
    for ring_ind in range(num_rings):
        offset = f"{ring_ind * dlength}"
        for ray_ind in range(num_rays):
            # Primary axis and 1st and 2nd secondary axes
            prim_axis = (
                f"{neg}*(cone_offset + {offset})",
                f"{neg}*(cone_offset + {offset})",
            )
            sec1_axis = (
                f"({offset}*tan(theta) + init_rad)*cos({ray_ind*dtheta})",
                f"({offset}*tan(theta) + init_rad)*cos({((ray_ind + 1) % num_rays)*dtheta})",
            )
            sec2_axis = (
                f"({offset}*tan(theta) + init_rad)*sin({ray_ind*dtheta})",
                f"({offset}*tan(theta) + init_rad)*sin({((ray_ind + 1) % num_rays)*dtheta})",
            )
            axes = (prim_axis, sec1_axis, sec2_axis)

            _wires.append(
                [
                    str(len(_wires)),  # Tag
                    "1",  # Number of segments
                    "originx +" + axes[x][0],  # x init
                    "originy +" + axes[y][0],  # y init
                    "originz +" + axes[z][0],  # z init
                    "originx +" + axes[x][1],  # x final
                    "originy +" + axes[y][1],  # y final
                    "originz +" + axes[z][1],  # z final
                    "wire_rad",  # Wire radius
                ]
            )

    return _wires


if __name__ == "__main__":
    # Length in number of chars for each column
    lim_lens = [2, 4, 5, 10, 10, 10, 10, 10, 10, 10]
    # How NEC2 wants it, i.e. as the char index of the start of each column
    lim_lens = [sum(lim_lens[: ind + 1]) for ind in range(len(lim_lens))]

    WIRES = build_cone("z", 0, INIT_WIRE)
    WIRES = build_cone("z", 1, WIRES)

    build_nec_file(
        comments=COMMENTS,
        wires=WIRES,
        constants=CONSTANTS,
        excitations=EXCITATIONS,
        rad_pattern=RADIATION,
        frequency=FREQUENCY,
        output="custom_bicone",
        lims=lim_lens,
        sig_figs=2,
        verbose=1,
    )
