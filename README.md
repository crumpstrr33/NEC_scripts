# NEC_scripts
Various python scripts for working with and creating .nec files

Run `python bicone.py` to create a directory of bicones at different frequency. Used specifically for 4nec2 to create many .out files for radiation data for different frequencies.

Otherwise, passing `build_nec_file` method in `build_nec_file.py` a list where each element is a .nec card (formatted as list with each element being a column for that card).

The method `reformat` will take a .nec file and properly format it by adding in the proper whitespace between columns and substituting in and then evaluating any variables in the files under the SY card.
