"""
This script uses python to build a `.nec` file. This allows
for the use of variables and other arithmetic which is much
easier in python. For information on the cards specified by the
arguments, e.g. EX or RP, check out https://www.nec2.org/part_3/cards/
"""
from datetime import datetime as dt
from math import *


def build_nec_file(
    comments,
    wires,
    constants,
    frequency=[],
    excitations=[],
    rad_pattern=[],
    output="output",
    lims=[2, 5, 10, 20, 30, 40, 50, 60, 70, 80],
    sig_figs=2,
    verbose=0,
):
    """
    Creates a `.nec` file. The values can contain arithmetic in it. Anything
    that Python's `eval` can handle and any function in the `math` package,
    so trig functions, exponentials, etc.

    Parameters:
    comments - The comments that are found on CM cards, added as a list
    wires - The wire data found on GW cards, a list of lists where the
        elements of the sublist are each parameter for the wire. Can use
        constants defined in the `constants` argument and baisc arithmatic
        (or any function defined in Python's `math` package).
    constants - A dictionary of constants to be substituted into the nec
        file. Constant names may not be such that one is found in another.
        For example, you cannot have 'offset' and 'origin_offset' because
        'offset' can be found (via Python's `replace` method in 'origin_offset').
    frequency (default []) - Defines the FR card, the frequency range and step
        for calculations.
    excitations (default []) - List for EX cards, cards that define excitations,
        e.g. voltage sources.
    rad_pattern (default []) - The RP card which defines how to calculate the
        the radiation pattern.
    output (default 'output') - The name of the output `.nec` file, the
        extension is automatically added.
    lims (default [2, 5, 10, 20, 30, 40, 50, 60, 70, 80]) - The character
        number that each column ends on. For example, for the default,
        we allocate 2 characters for the first argument (the card name),
        3 for the next column, 5 for the third, and 10 for the rest.
    sig_figs (default 2) - The number of significant figures used for the
        numbers written in scientific notation (i.e. how many digits after
        the decimal point).
    verbose (default 2) - If 0, will not print out anything. If 1, will print out
        just info on the number of wires, file location and time taken to create
        file. If 2, will print out the comments in the .nec file, and info on the
        number of wires, file location and time taken to create file.
    """

    # scinot_ind tells this function at which column of a row to
    # start using scientific notation
    def _format_rows(rows, card, scinot_ind):
        for row in rows:
            row_str = card
            for ind, param in enumerate(row):
                # Replace constants with values
                for const_key, const_val in constants.items():
                    param = param.replace(const_key, str(const_val))

                # Add to line correctly formatted
                rlim = lims[ind + 1] - lims[ind]
                if ind > (scinot_ind - 1):
                    # Change to 3-digit rounded scientific notation
                    val = f"{eval(param):.{sig_figs}e}"
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
    nec_file.append(f"GE{(lims[1] - lims[0] - 1)*' '}0")
    # Frequency
    if frequency:
        _format_rows(rows=[frequency], card="FR", scinot_ind=4)
    # Excitations
    if excitations:
        _format_rows(rows=excitations, card="EX", scinot_ind=4)
    # Radation pattern,
    if rad_pattern:
        _format_rows(rows=[rad_pattern], card="RP", scinot_ind=8)
    # File end
    nec_file.append("EN\n")

    # Write to new file
    with open(f"{output}.nec", "w") as f:
        f.write("\n".join(nec_file))
    dt_end = dt.now()

    if verbose:
        if verbose == 2:
            print("\nComments:")
            for comment in comments:
                print(" " * 8 + f"{comment}")
        print(
            f"Wrote {len(wires)} wires to {output}.nec in "
            + f"{(dt_end - dt_start).total_seconds() * 1000:.3f}ms."
        )
