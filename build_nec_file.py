"""
This script uses python to build a `.nec` file. This allows
for the use of variables and other arithmetic which is much
easier in python. For information on the cards specified by the
arguments, e.g. EX or RP, check out https://www.nec2.org/part_3/cards/
"""
from datetime import datetime as dt
from math import *

LIMS = [2, 5, 10, 20, 30, 40, 50, 60, 70, 80]


def build_nec_file(
    comments,
    wires,
    constants,
    frequency=[],
    excitations=[],
    rad_pattern=[],
    output="output",
):
    """
    Creates a `.nec` file. The values can contain arithmetic in it. Anything
    that Python's `eval` can handle and any function in the `math` package,
    so trig functions, exponentials, etc.

    Parameters:
    comments - The comments that are found on CM cards, added as a list
    wires - The wire data found on GW cards, a list of lists where the
            elements of the sublist are each parameter for the wire.
    constants - A dictionary of constants to be substituted into the nec
                file. Constant names may not be such that one is found
                in another. For example, you cannot have 'offset' and
                'origin_offset' because 'offset' can be found (via Python's
                `replace` method in 'origin_offset')
    frequency (default []) -
    excitations (default []) - List for EX cards, cards that define excitations,
                                e.g. voltage sources
    rad_pattern (default []) - The RP card which defines how to calculate the
                                the radiation pattern
    output (default `output`) - The name of the output `.nec` file, the
                                extension is automatically added
    """

    def _format_rows(rows, card, scinot_ind):
        for row in rows:
            row_str = card
            for ind, param in enumerate(row):
                # Replace constants with values
                for const_key, const_val in constants.items():
                    param = param.replace(const_key, str(const_val))

                # Add to line correctly formatted
                rlim = LIMS[ind + 1] - LIMS[ind]
                if ind > (scinot_ind - 1):
                    # Change to 3-digit rounded scientific notation
                    val = f"{eval(param):.2e}"
                else:
                    # Otherwise just evaluate, e.g. tag number
                    val = str(eval(param))
                # Add to string and push the rightmost it can go
                row_str += f"{val.rjust(rlim):<{rlim}}"
            nec_file.append(row_str)

    dt_start = dt.now()
    nec_file = []
    # Add comments
    for comment in comments:
        nec_file.append(f"CM {comment}")
    # Comment end
    nec_file.append("CE")

    # Add wires
    _format_rows(rows=wires, card="GW", scinot_ind=2)
    # Wire end
    nec_file.append("GE  0")
    # Frequency
    _format_rows(rows=[frequency], card="FR", scinot_ind=4)
    # Excitations
    _format_rows(rows=excitations, card="EX", scinot_ind=4)
    # Radation pattern,
    _format_rows(rows=[rad_pattern], card="RP", scinot_ind=8)
    # File end
    nec_file.append("EN\n")

    # Write to new file
    with open(f"{output}.nec", "w") as f:
        f.write("\n".join(nec_file))
    dt_end = dt.now()

    print("Comments:")
    for comment in comments:
        print(" " * 8 + f"{comment}")
    print(
        f"\nWrote {len(wires)} wires to {output}.nec in "
        + f"{(dt_end - dt_start).total_seconds() * 1000:.3f}ms."
    )
