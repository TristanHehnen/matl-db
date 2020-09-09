import pandas as pd
import re


# Pattern to match numbers in strings with regular expressions.
# From: John Machin; https://stackoverflow.com/questions/4703390/how-to-extract-a-floating-number-from-a-string
numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
rx = re.compile(numeric_const_pattern, re.VERBOSE)
# rx.findall("Some example: Jr. it. was .23 between 2.3 and 42.31 seconds")


def read_experiment_lines(readme_lines, start_marker_a="TGA",
                          start_marker_b="###", end_marker="###"):
    """
    This function iterates over a list of strings and searches for information
    about a desired experiment. The information is found by looking for
    sub-strings (markers) that encapsulate the desired information. A
    shortened list is returned containing the experiment information.

    :param readme_lines: List of string containing text file content
    :param start_marker_a: Marker to find the desired experiment
    :param start_marker_b: Additional marker to make sure the correct
           line is chosen
    :param end_marker: Marker to indicate when to stop collecting lines.

    :return: list, containing lines of string related to a desired experiment
    """

    # Initialise collection of experiment description.
    experiment_lines = list()

    # Flag to control what lines to collect.
    collect_entry = False

    # Iterate over all the lines of the file content.
    for line in readme_lines:

        # Skip empty lines.
        if line == '':
            continue

        if end_marker in line:
            if "####" not in line:
                # Stop collecting lines after the TGA experiment
                # description concluded and a new section starts.
                collect_entry = False

        if start_marker_a in line and start_marker_b in line:
            # Allow collection of lines.
            collect_entry = True

        if collect_entry is True:
            # Collect lines.
            experiment_lines.append(line)

    return experiment_lines


def read_test_condition_table(experiment_lines):
    """
    Takes a list of strings of information on an experiment that also
    includes a markdown table with a summary of the experiment. It finds
    the table lines and translates them into a Pandas DataFrame.

    :param experiment_lines: list of strings containing information on an
           experiment including a markdown table

    :return: Pandas DataFrame of said table
    """

    # Initialise data collection.
    preprocess_content = list()
    table_content = dict()

    # Find and read table.
    for line in experiment_lines:
        if "|:-" in line:
            # Skip lines containing visual markers (horizontal lines).
            continue

        elif "|" in line:
            # Read table lines and seperate by columns.
            # Ignore first and last character per line, they are empty.
            preprocess_content.append(line.split("|")[1:-1])
            # print(line.split("|")[1:-1])

    # Process content by column.
    for col_id, col_label in enumerate(preprocess_content[0]):
        # Initialise column.
        col_content = list()

        # Get all cells per column.
        for line_id, line in enumerate(preprocess_content[1:]):

            if "Test Label" not in col_label and "File Name" not in col_label:
                # Transform string to float.
                cell_content = line[col_id].replace("\\", "")
                col_content.append(float(cell_content))
            else:
                # Remove "\\" from file names and experiment labels.
                cell_content = line[col_id].replace("\\", "")
                # Remove surrounding " " of test label.
                cell_content = cell_content.replace(" ", "")
                col_content.append(cell_content)

        # Collect columns.
        table_content[col_label[1:-1]] = col_content

    # Return table as Pandas DataFrame.
    return pd.DataFrame.from_dict(table_content)


def get_institute(readme_lines):
    """
    Takes a list of strings of the README-file content and extract the first
    line, which contains the institute label and name. Label and name are both
    returned as a list of string.

    :param readme_lines: list of strings of the README-file content

    :return: list of string with institute label and name
    """

    # Read the institute line (skip markdown marker for heading).
    institute_line = readme_lines[0][2:]

    # Split the institute line into individual elements.
    institute_line_parts = institute_line.split(" ")

    # Get the institute label and its length (amount of characters).
    institute_label_raw = institute_line_parts[-1]
    label_raw_len = len(institute_label_raw)
    institute_label = institute_label_raw[1:-1]

    # From the institute line remove the institute label
    # to get the institute name.
    institute_name = institute_line[:-(label_raw_len + 1)]

    # Return institute label and name as a list.
    return [institute_label, institute_name]


def readme_items(md_lines, items):
    """
    Takes a list of markdown lines (string) of a desired experiment,
    e.g. TGA, and a dictionary of the expected bullet points. It parses the
    lines and extracts the information of the bullet points and stores them
    in the dictionary. Bullet points are distinguished between major, medium
    and minor. Major points are understood as some kind of heading that ties
    multiple minor points together, e.g. description of crucibles. Medium
    points stand on their own and only provide a single piece of
    information, e.g. sample mass.

    :param md_lines: list of strings (markdown file lines)
    :param items: dictionary with expected bullet points as keys.

    :return: Nothing; the existing dictionary is simply filled with the
             appropriate values for the keys.
    """

    # Read bullet points of markdown list and transform them
    # to dictionary keys.
    for line in md_lines:
        # Get medium items.
        if "* " in line and ": " in line:
            new_key = line[2:].split(':')[0].replace(' ', '_').lower()
            new_info = line[4:].split(':')[1]
        #             print(line)

        # Get major items.
        elif "* " in line and not ": " in line:
            new_key = line[2:].replace(' ', '_').lower()
            recent_main_key = new_key
        #             print(line)

        # Get minor items.
        elif "  - " in line and ": " in line:
            new_key = line[4:].split(':')[0].replace(' ', '_').lower()
            new_info = line[4:].split(':')[1]
        #             print(new_info)

        else:
            # Catch cases that aren't expected keywords, e.g. empty lines.
            new_key = None

        if new_key is not None:
            if "heating_rate" in new_key:
                # Determine how many heating rates were used,
                # create a new dictionary for each. #TODO

                # Get all heating rates as list.
                heating_rates = rx.findall(line)

                # Get unit.
                heating_rate_unit = line[4:].split(' ')[-1]
        #                 print('hr unit', heating_rate_unit)

        #                 for heating_rate in rx.findall(line):
        #                     print(heating_rate)
        #                 print(rx.findall(line))
        #                 print(new_info)

        if new_key is not None:

            #             # Set the heating rate.
            #             new_val = 10
            #             new_unit = "K/min"
            #             items["heating_rate"] = {'value': new_val,
            #                                      'unit': new_unit}

            if "initial_temperature" in new_key:
                if not None:
                    new_val = new_info.split(" ")[-2]
                    new_unit = new_info.split(" ")[-1]
                else:
                    new_val = None
                    new_unit = None

                items[recent_main_key][new_key] = {'value': new_val,
                                                   'unit': new_unit}
            #                 print(new_info.split(" "), recent_main_key)

            elif "initial_isotherm" in new_key:
                if "None" not in new_info:
                    new_val = new_info.split(" ")[-2]
                    new_unit = new_info.split(" ")[-1]
                else:
                    new_val = None
                    new_unit = None

                items[recent_main_key][new_key] = {'value': new_val,
                                                   'unit': new_unit}
            #                 print(new_info.split(" "), recent_main_key)

            elif "maximum_temperature" in new_key:
                if "None" not in new_info:
                    new_val = new_info.split(" ")[-2]
                    new_unit = new_info.split(" ")[-1]
                else:
                    new_val = None
                    new_unit = None

                items[recent_main_key][new_key] = {'value': new_val,
                                                   'unit': new_unit}
            #                 print(new_info.split(" "), recent_main_key)

            elif "final_isotherm" in new_key:
                if "None" not in new_info:
                    new_val = new_info.split(" ")[-2]
                    new_unit = new_info.split(" ")[-1]
                else:
                    new_val = None
                    new_unit = None

                items[recent_main_key][new_key] = {'value': new_val,
                                                   'unit': new_unit}
            #                 print(new_info.split(" "), recent_main_key)

            elif "sample_mass" in new_key:
                if "None" not in new_info:
                    new_val = new_info.split(" ")[-2]
                    new_unit = new_info.split(" ")[-1]
                else:
                    new_val = None
                    new_unit = None

                items[new_key] = {'value': new_val,
                                  'unit': new_unit}
            #                 print(new_info.split(" "), recent_main_key)

            elif "sample_geometry" in new_key:
                if "None" not in new_info:
                    new_val = new_info[1:]
                else:
                    new_val = None

                items[new_key] = new_val
            #                 print(new_info.split(" "), recent_main_key)

            elif "calibration_type" in new_key:
                if "None" not in new_info:
                    new_val = new_info[1:]
                else:
                    new_val = None

                items[new_key] = new_val
            #                 print(new_info.split(" "), recent_main_key)

            elif "type" in new_key and "crucible" in recent_main_key:
                if "None" not in new_info:
                    new_val = new_info[1:]
                else:
                    new_val = None

                items[recent_main_key][new_key] = new_val
            #                 print(new_info.split(" "), recent_main_key)

            elif "volume" in new_key and "crucible" in recent_main_key:
                if "None" not in new_info:
                    new_val = new_info.split(" ")[-2]
                    new_unit = new_info.split(" ")[-1]
                else:
                    new_val = None
                    new_unit = None

                items[recent_main_key][new_key] = {'value': new_val,
                                                   'unit': new_unit}
            #                 print(new_info.split(" "), recent_main_key)

            elif "diameter" in new_key and "crucible" in recent_main_key:
                if "None" not in new_info:
                    new_val = new_info.split(" ")[-2]
                    new_unit = new_info.split(" ")[-1]
                else:
                    new_val = None
                    new_unit = None

                items[recent_main_key][new_key] = {'value': new_val,
                                                   'unit': new_unit}
            #                 print(new_info.split(" "), recent_main_key)

            elif "mass" in new_key and "crucible" in recent_main_key:
                if "None" not in new_info:
                    new_val = new_info.split(" ")[-2]
                    new_unit = new_info.split(" ")[-1]
                else:
                    new_val = None
                    new_unit = None

                items[recent_main_key][new_key] = {'value': new_val,
                                                   'unit': new_unit}
            #                 print(new_info.split(" "), recent_main_key)

            elif "lid" in new_key and "crucible" in recent_main_key:
                if "None" not in new_info:
                    new_val = new_info.split(" ")[-2]
                    new_unit = new_info.split(" ")[-1]
                else:
                    new_val = None
                    new_unit = None

                items[recent_main_key][new_key] = {'value': new_val,
                                                   'unit': new_unit}
            #                 print(new_info.split(" "), recent_main_key)

            elif "note" in new_key and "crucible" in recent_main_key:
                if "None" not in new_info:
                    new_val = new_info[1:]
                else:
                    new_val = None

                items[recent_main_key][new_key] = new_val
            #                 print(new_info.split(" "), recent_main_key)

            elif "type" in new_key and "carrier_gas" in recent_main_key:
                if "None" not in new_info:
                    new_val = new_info[1:]
                else:
                    new_val = None

                items[recent_main_key][new_key] = new_val
            #                 print(new_info.split(" "), recent_main_key)

            elif "flow_rate" in new_key and "carrier_gas" in recent_main_key:
                if "None" not in new_info:
                    new_val = new_info.split(" ")[-2]
                    new_unit = new_info.split(" ")[-1]
                else:
                    new_val = None
                    new_unit = None

                items[recent_main_key][new_key] = {'value': new_val,
                                                   'unit': new_unit}
            #                 print(new_info.split(" "), recent_main_key)

            elif "note" in new_key and "carrier_gas" in recent_main_key:
                if "None" not in new_info:
                    new_val = new_info[1:]
                else:
                    new_val = None

                items[recent_main_key][new_key] = new_val
            #                 print(new_info.split(" "), recent_main_key)

            elif "type" in new_key and "instrument" in recent_main_key:
                if "None" not in new_info:
                    new_val = new_info[1:]
                else:
                    new_val = None

                items[recent_main_key][new_key] = new_val
            #                 print(new_info.split(" "), recent_main_key)

            elif "note" in new_key and "instrument" in recent_main_key:
                if "None" not in new_info:
                    new_val = new_info[1:]
                else:
                    new_val = None

                items[recent_main_key][new_key] = new_val


# Collection of experiment description templates.
experiment_template = {
    "TGA_base": {
        'laboratory': {},
        'heating_rate': {},
        'temperature_program': {
            'initial_temperature': {},
            'initial_isotherm': {},
            'maximum_temperature': {},
            'final_isotherm': {}},
        'sample_mass': {},
        'sample_geometry': {},
        'calibration_type': {},
        'crucible': {
            'type': {},
            'volume': {},
            'diameter': {},
            'mass': {},
            'lid': {},
            'note': {}},
        'carrier_gas': {
            'type': {},
            'flow_rate': {},
            'note': {}},
        'instrument': {
            'type': {},
            'note': {}},
        'path': {}}}
