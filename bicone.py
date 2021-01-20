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
from math import pi

from build_nec_file import build_nec_file

origin = (0.0, 0.0, 0.0)
cone_offset = 0.3
num_rays = 100
num_rings = 25
theta = pi / 4
length = 1
init_rad = 0.1


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
}

COMMENTS = [
    "Bicone made with bicone.py",
    f"Origin: ({origin[0]:.3f}, {origin[1]:.3f}, {origin[2]:.3f})",
    f"Cone offset: {cone_offset:.3f}",
    f"Cone angle: {theta:.3f}",
    f"Cone length: {length:.3f}",
    f"Number of rings: {num_rings}",
    f"Number of rays: {num_rays}",
    f"Cone initial radius: {init_rad:.3f}",
]


def build_cone(axis, parity):
    """
    Creates a cone in a direction along an axis.

    Parameters:
    axis - The axis which the cone is along, either `x`, `y`, `z`
    partiy - Which direction to face, either 0 for negative or 1 for positive
    """
    if parity not in [0, 1]:
        raise f"Please set parity to `1` or `0`, not {parity}."

    wires = []
    neg = 1 if parity else -1
    x = 0 if axis == "x" else 1 if axis == "y" else 2
    y = 2 if axis == "x" else 0 if axis == "y" else 1
    z = 1 if axis == "x" else 2 if axis == "y" else 0

    # Rays start at (x, y) = (cone_offset, init_rad)
    # End at (x, y) = (cone_offset + length, init_rad + length*tan(theta))
    # Rotate ray about x axis
    dtheta = 2 * pi / num_rays
    for ind in range(num_rays):
        prim_axis = (
            f"{neg}*cone_offset",
            f"{neg}*(cone_offset + length)",
        )
        sec1_axis = (
            f"init_rad*cos({ind*dtheta})",
            f"(init_rad + length*tan(theta))*cos({ind*dtheta})",
        )
        sec2_axis = (
            f"init_rad*sin({ind*dtheta})",
            f"(init_rad + length*tan(theta))*sin({ind*dtheta})",
        )
        axes = (prim_axis, sec1_axis, sec2_axis)

        wires.append(
            [
                "1",
                "1",
                "originx +" + axes[x][0],
                "originy +" + axes[y][0],
                "originz +" + axes[z][0],
                "originx +" + axes[x][1],
                "originy +" + axes[y][1],
                "originz +" + axes[z][1],
                "0.01",
            ]
        )

    # Connects rays
    # The {offset}*tan(theta) is location on ray it connects, the cosine/sine
    # afterwards rotates just like above. The y, z endpoints are just the proceeding
    # ray to connect to
    dlength = length / (num_rings - 1)
    for ind in range(num_rings):
        offset = f"{ind * dlength}"
        for ind in range(num_rays):
            prim_axis = (
                f"{neg}*(cone_offset + {offset})",
                f"{neg}*(cone_offset + {offset})",
            )
            sec1_axis = (
                f"({offset}*tan(theta) + init_rad)*cos({ind*dtheta})",
                f"({offset}*tan(theta) + init_rad)*cos({((ind + 1) % num_rays)*dtheta})",
            )
            sec2_axis = (
                f"({offset}*tan(theta) + init_rad)*sin({ind*dtheta})",
                f"({offset}*tan(theta) + init_rad)*sin({((ind + 1) % num_rays)*dtheta})",
            )
            axes = (prim_axis, sec1_axis, sec2_axis)

            wires.append(
                [
                    "1",
                    "1",
                    "originx +" + axes[x][0],
                    "originy +" + axes[y][0],
                    "originz +" + axes[z][0],
                    "originx +" + axes[x][1],
                    "originy +" + axes[y][1],
                    "originz +" + axes[z][1],
                    "0.01",
                ]
            )

    return wires


if __name__ == "__main__":
    wires_neg_x = build_cone("x", 0)
    wires_pos_x = build_cone("x", 1)
    wires_neg_y = build_cone("y", 0)
    wires_pos_y = build_cone("y", 1)
    wires_neg_z = build_cone("z", 0)
    wires_pos_z = build_cone("z", 1)

    tripole_bicone = (
        wires_neg_x
        + wires_pos_x
        + wires_neg_y
        + wires_pos_y
        + wires_neg_z
        + wires_pos_z
    )
    build_nec_file(COMMENTS, tripole_bicone, CONSTANTS)
