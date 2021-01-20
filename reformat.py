"""
This script will correctly format a `.nec` file based on the proper
columns limits according to https://www.nec2.org/part_3/cards/ in
the list `LIMS`. I'm not assuming all cards follow this format
although I would guess hence the existence of the `FORMATTED_CARDS`
list; these are cards I know follow this pattern.

It seems that constants can be defined with an SY card. This script
will replace the constants in the file with the value and evaluate it
via Python's `eval` method.

To run this, you can either import the `reformat` method or, via CLI,
run `python reformat.py <old_nec> <new_nec>`.
"""
import os
import re
import sys

LIMS = [0, 2, 5, 10, 20, 30, 40, 50, 60, 70, 80]
FORMATTED_CARDS = ["GW", "GE", "RP", "EX"]


def reformat(necf, new_necf):
    """
    Reformats a `.nec` file to follow the correct column limits for
    each parameter.

    Parameters:
    necf - The `.nec` file to format
    new_necf - The name of the `.nec` file to place this new formatted
                file. If the file name already exists, nothing will be done.
    """
    if os.path.isfile(new_necf):
        print(f"File {new_necf} already exists. Aborting...")
        return

    with open(necf, "r") as lines:
        with open(new_necf, "w") as new_lines:
            # Dict for variables signified by SY card type
            sy_vars = {}

            for line in lines:
                editted_line = False
                # Grab all variables
                if line.startswith("SY"):
                    editted_line = True
                    gw_str = ""
                    # Assumes form SY <var> = <val>
                    sy_vars[line.split(" ")[1]] = line.split(" ")[3].strip("\n")

                # Format wire cards correctly as per https://www.nec2.org/part_3/cards/gw.html
                if line[:2] in FORMATTED_CARDS:
                    editted_line = True
                    # Remove all whitespace to create list of parameters
                    params = re.sub(r"[ ]+", " ", line.strip("\n")).split(" ")

                    gw_str = ""
                    for ind, param in enumerate(params):
                        # Replaces variables with the values
                        for sy_key, sy_val in sy_vars.items():
                            param = param.replace(sy_key, sy_val)

                        try:
                            rlim = LIMS[ind + 1] - LIMS[ind]
                        except IndexError:
                            break

                        # Evaluates arithmetic added from the variables
                        # Doesn't evaluate 0th index param cause that's card type
                        if ind:
                            param = str(eval(param))
                        gw_str += f"{param.rjust(rlim):<{rlim}}"
                    # print(s)
                    gw_str += "\n"

                if editted_line:
                    new_lines.write(gw_str)
                else:
                    new_lines.write(line)


if __name__ == "__main__":
    reformat(sys.argv[1], sys.argv[2])
