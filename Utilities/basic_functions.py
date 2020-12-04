import re
import os
import copy

import pandas as pd
from pandas.core.common import flatten as pd_flatten


# Pattern to match numbers in strings with regular expressions.
# From: John Machin; https://stackoverflow.com/questions/4703390/how-to-extract-a-floating-number-from-a-string
numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
rx = re.compile(numeric_const_pattern, re.VERBOSE)
# rx.findall("Some example: Jr. it. was .23 between 2.3 and 42.31 seconds")


def get_exp_readme_files(institutes, base_path, experiment_key="TGA"):
    """
    This function needs a list of institute labels, e.g. abbreviations of the
    institute names, that doubles as the directory names containing the
    contributed data by said institute. The base path to where these
    directories are located needs to be provided as well. An experiment
    keyword needs to be specified that is used in the title of the
    section of the README file that describes the desired experiment,
    e.g. TGA.
    This function iterates over all the institutes and checks if the README
    file contains the experiment keyword. If that is the case, the whole
    README content is extracted as a list of string and stored in a
    dictionary, where the institute labels are the keys to access the
    respective lists.

    :param institutes: list of institute labels that doubles as directory names
    :param base_path: path to the institute directories
    :param experiment_key: string, experiment keyword to look for in the
                           README files

    :return: dictionary populated with the content of the README markdown
             bullet points of a desired experiment (experiment_key)
    """

    print("* Institutes that contributed {} data:".format(experiment_key))
    # Initialise collection of README files with desired experiments.
    exp_readme_contents = dict()

    # Iterate over all contributions by institute.
    for institute in institutes:
        # Build path to each individual README file.
        readme_path = os.path.join(base_path,
                                   institute,
                                   "README.md")
        print("  " + institute)

        # Open the README file and check if it contains
        # the experiment keyword in a markdown title line.
        with open(readme_path, encoding='utf8') as f:
            for line in f:
                if experiment_key in line and "###" in line:
                    # Read the complete file content.
                    with open(readme_path, encoding='utf8') as f:
                        # Create list of string, line by line.
                        readme_lines = [line.rstrip() for line in f]

                    print("  " + "+ True")

                    # Collect README file content.
                    exp_readme_contents[institute] = readme_lines
                    continue  # Skip to next file.

        print()

    return exp_readme_contents


def read_experiment_lines(readme_lines, start_marker_a="TGA",
                          start_marker_b="### ", end_marker="### "):
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
    Transforms markdown table into pandas DataFrame.

    Takes a list of strings of information on an experiment that also
    includes a markdown table with a summary of the experiment. It finds
    the table lines and translates them into a Pandas DataFrame.

    :param experiment_lines: list of strings containing information on an
           experiment including a markdown table

    :return: Pandas DataFrame of said table
    """

    # Initialise data collection.
    pre_process_content = list()
    table_content = dict()

    # Find and read table.
    for line in experiment_lines:
        if "|:-" in line:
            # Skip lines containing visual markers (horizontal lines).
            continue

        elif "|" in line:
            # Read table lines and separate by columns.
            # Ignore first and last character per line, they are empty.
            pre_process_content.append(line.split("|")[1:-1])
            # print(line.split("|")[1:-1])

    # Process content by column.
    for col_id, col_label in enumerate(pre_process_content[0]):
        # Initialise column.
        col_content = list()

        # Get all cells per column.
        for line_id, line in enumerate(pre_process_content[1:]):

            if "Test Label" not in col_label:
                # Transform string to float.
                # Split the string at a space to deal with
                # possible question marks or notes that should be
                # after the number, thus the number is the first
                # element in the returned list.
                cell_content = line[col_id].split()[0]
                # Check if the cell can be transformed to a float
                # otherwise set it to None.
                try:
                    cell_content = float(cell_content)
                except:
                    print(
                        "* An exception occurred: '{}' will be set to 'None'.\n".format(
                            cell_content))
                    cell_content = None

                col_content.append(cell_content)
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


def get_value_unit(exp_info, missing_info="[?]"):
    """
    Splits string into pieces to separate value and unit.

    :param exp_info: string containing the value and unit
    :param missing_info: marker denoting missing information

    :return: value and unit
    """
    if "None" not in exp_info:
        # Split the entry to separate value, unit and missing_info marker,
        # store them in an list.
        entry = exp_info.split(" ")
        # Remove missing_info marker.
        if missing_info in entry:
            print("* Missing info: ", entry)
            del entry[-1]
        # From the list get the value and the unit, respectively.
        exp_value = entry[-2]
        exp_unit = entry[-1]
    else:
        # Set both to 'None' if no info is available.
        exp_value = None
        exp_unit = None

    return exp_value, exp_unit


def get_value(exp_info, missing_info="[?]"):
    """
    Get the value of an experiment item.

    :param exp_info: string containing the value
    :param missing_info: marker denoting missing information

    :return: value
    """
    if "None" not in exp_info:
        # Remove missing_info marker and the leading space.
        if missing_info in exp_info:
            print("* Missing info: ", exp_info)
            exp_value = exp_info[:-3]
        else:
            # Take the value and remove the leading space.
            exp_value = exp_info[:]
    else:
        # Set to 'None' if no info is available.
        exp_value = None

    return exp_value


def get_institute(readme_lines):
    """
    Collects the institute name and label from the README content.

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


def fill_tga_dict(experiment_lines, institute_name_info,
                  exp_table_df, tga_base_dict, material_path):
    """
    Populates dictionary with information from the TGA README content.

    This function creates a deep copy from a base dictionary of a given
    experiment and populates it with the respective values from markdown
    bullet points of the README file content.

    :param experiment_lines: list of string of the TGA README
    :param institute_name_info: list containing the institute label and the
                                institute name
    :param exp_table_df: Pandas DataFrame of the test condition summary table
    :param tga_base_dict: dictionary containing the keys for the TGA
                          experiment, will be (deep) copied and populated
    :param material_path: path to the material information in the MaCFP repo,
                          e.g. "Non-charring\PMMA"

    :return: populated (deep) copy of the tga_base_dict
    """

    #
    experiment_type = "TGA"
    experiment_info = dict()
    repetition_info = dict()
    institute_label = institute_name_info[0]
    institute_name = institute_name_info[1]

    for test_label in exp_table_df["Test Label"][:]:

        # Remove unnecessary spaces.
        test_label = test_label.replace(" ", "")

        # Get line number of test.
        test_idx = exp_table_df[exp_table_df['Test Label'] == test_label].index[0]

        # Initialise experiment dictionary and fill in a copy of
        # the experiment description template.
        test_info = copy.deepcopy(tga_base_dict)

        # Set institute name and label.
        test_info['laboratory']['label'] = institute_label
        test_info['laboratory']['name'] = institute_name

        # Get test label to build file name.
        data_file_name = exp_table_df['Test Label'][test_idx] + ".csv"
        if "_STA_" in data_file_name:
            # For simultaneous DSC/TGA tests the '_STA_' part in the test label
            # needs to be changed to either '_DSC_' oder '_TGA_'.
            data_file_name = data_file_name.replace("_STA_",
                                                    "_" + experiment_type + "_")
        print(data_file_name)

        # Build data file path.
        data_file_path = os.path.join(material_path.split("\\")[-2],
                                      material_path.split("\\")[-1],
                                      institute_label,
                                      data_file_name)
        # Store relative data file path.
        test_info['path'] = data_file_path

        # Set experiment description items from README.
        get_tga_items(md_lines=experiment_lines,
                      items=test_info)

        # Set heating rate.
        new_val = exp_table_df['Heating Rate [K/min]'][test_idx]
        new_unit = "K/min"
        test_info["heating_rate"] = {'value': new_val,
                                     'unit': new_unit}

        # Set initial sample mass.
        new_val = exp_table_df['Initial Sample Mass [mg]'][test_idx]
        new_unit = "mg"
        test_info["sample_mass"] = {'value': new_val,
                                    'unit': new_unit}

        repetition_info[test_label] = test_info

    experiment_info[institute_label] = repetition_info

    return repetition_info


def fill_dsc_dict(experiment_lines, institute_name_info,
                  exp_table_df, dsc_base_dict, material_path):
    """
    Populates dictionary with information from the DSC README content.

    This function creates a deep copy from a base dictionary of a given
    experiment and populates it with the respective values from markdown
    bullet points of the README file content.

    :param experiment_lines: list of string of the TGA README
    :param institute_name_info: list containing the institute label and the
                                institute name
    :param exp_table_df: Pandas DataFrame of the test condition summary table
    :param dsc_base_dict: dictionary containing the keys for the DSC
                          experiment, will be (deep) copied and populated
    :param material_path: path to the material information in the MaCFP repo,
                          e.g. "Non-charring\PMMA"

    :return: populated (deep) copy of the tga_base_dict
    """

    #
    experiment_type = "DSC"
    experiment_info = dict()
    repetition_info = dict()
    institute_label = institute_name_info[0]
    institute_name = institute_name_info[1]

    for test_label in exp_table_df["Test Label"][:]:

        # Remove unnecessary spaces.
        test_label = test_label.replace(" ", "")

        # Get line number of test.
        test_idx = exp_table_df[exp_table_df['Test Label'] == test_label].index[0]

        # Initialise experiment dictionary and fill in a copy of
        # the experiment description template.
        test_info = copy.deepcopy(dsc_base_dict)

        # Set institute name and label.
        test_info['laboratory']['label'] = institute_label
        test_info['laboratory']['name'] = institute_name

        # Get test label to build file name.
        data_file_name = exp_table_df['Test Label'][test_idx] + ".csv"
        if "_STA_" in data_file_name:
            # For simultaneous DSC/TGA tests the '_STA_' part in the test label
            # needs to be changed to either '_DSC_' oder '_TGA_'.
            data_file_name = data_file_name.replace("_STA_",
                                                    "_" + experiment_type + "_")
        print(data_file_name)

        # Build data file path.
        data_file_path = os.path.join(material_path.split("\\")[-2],
                                      material_path.split("\\")[-1],
                                      institute_label,
                                      data_file_name)
        # Store relative data file path.
        test_info['path'] = data_file_path

        # Set experiment description items from README.
        get_dsc_items(md_lines=experiment_lines,
                      items=test_info)

        # Set heating rate.
        new_val = exp_table_df['Heating Rate [K/min]'][test_idx]
        new_unit = "K/min"
        test_info["heating_rate"] = {'value': new_val,
                                     'unit': new_unit}

        # Set initial sample mass.
        new_val = exp_table_df['Initial Sample Mass [mg]'][test_idx]
        new_unit = "mg"
        test_info["sample_mass"] = {'value': new_val,
                                    'unit': new_unit}

        repetition_info[test_label] = test_info

    experiment_info[institute_label] = repetition_info

    return repetition_info


def get_cone_items(md_lines, items,
                   multi_set=["backing", "thermocouple"]):
    """

    :param md_lines: list of strings (markdown file lines)
    :param items: dictionary with expected bullet points as keys.
    :param multi_set: list of keywords that spawn multiple parameter sets.

    """

    # The parent is used to sort the individual items
    # into the dictionary.
    parent = None

    # List of items that are not of the value-unit type (e.g. 5 kg).
    text_items = ["note", "material", "shape", "retainer_frame",
                  "retaining_grid", "top_opening", "doors_windshield",
                  "bottom_opening", "carrier_gas", "type", "frequency",
                  "manufacturer", "apparatus_and_model_number", "surface"]

    # Read bullet points of markdown list and transform them
    # to dictionary keys.
    for line in md_lines:
        # Get medium items.
        if "* " in line and ": " in line:
            new_key = line[2:].split(': ')[0].replace(' ', '_').lower()
            new_info = line[4:].split(': ')[1]
            # Reset parent.
            parent = None

        # Get major items.
        elif "* " in line and ": " not in line:
            # Set parent.
            parent = line[2:].replace(' ', '_').lower()

        # Get minor items.
        elif "  - " in line and ": " in line:
            new_key = line[4:].split(': ')[0].replace(' ', '_').lower()
            new_key = new_key.replace("/", "_")
            new_info = line[4:].split(': ')[1]

        else:
            # Catch cases that aren't expected keywords, e.g. empty lines.
            new_key = None

        if parent is not None:
            if parent in multi_set and new_key is not None:
                # Process special cases with multiple parameter sets
                # of the same kind, like thermocouple locations.

                # Find integer before ':' to determine to which
                # set the parameter belongs.
                keyword_number_res = re.findall(r'[0-9]+$',
                                                new_key)

                # Determine if only a single number is in the string.
                if len(keyword_number_res) == 1:
                    # Build new parent key word for the new parameter set.
                    parent_keyword = '{}_{}'.format(parent,
                                                    keyword_number_res[0])

                    # Create new dictionary, if the parent key word doesn't
                    # exist.
                    if parent_keyword not in items[parent]:
                        items[parent][parent_keyword] = dict()

                # Remove trailing number from key and check against
                # the text items.
                if "location" in new_key:
                    # Get the coordinate information for the thermocouples.
                    coordinates_raw = new_info.split(',')

                    # Initialise dictionary to store the coordinate information.
                    coordinates = dict()

                    # Iterate over the coordinate and split the letter from
                    # the value.
                    for coordinate_raw in coordinates_raw:
                        c_letter = coordinate_raw.split('=')[0]
                        c_value = coordinate_raw.split('=')[1]

                        # Get value and unit from the coordinate value.
                        new_val, new_unit = get_value_unit(c_value,
                                                           missing_info="[?]")

                        # Remove spaces.
                        c_letter = c_letter.replace(' ', '')

                        # Store the individual coordinates in their dictionary.
                        coordinates[c_letter] = {"value": new_val,
                                                 "unit": new_unit}

                    # Store the combined coordinates.
                    items[parent][parent_keyword][new_key[:-2]] = coordinates

                elif new_key.split('_')[0] not in text_items:
                    # Process items that are of the value-unit type.
                    new_val, new_unit = get_value_unit(new_info,
                                                       missing_info="[?]")

                    # Store value-unit pair in the appropriate dictionary.
                    items[parent][parent_keyword][new_key[:-2]] = {
                        "value": new_val,
                        "unit": new_unit}

                else:
                    # Process items that are basically text, like notes.
                    new_val = get_value(new_info,
                                        missing_info="[?]")

                    # Store information in the appropriate dictionary.
                    items[parent][parent_keyword][new_key[:-2]] = new_val

            elif new_key is not None:
                # Process regular items.

                if new_key not in text_items:
                    # Process items that are of the value-unit type.
                    new_val, new_unit = get_value_unit(new_info,
                                                       missing_info="[?]")

                    # Store value-unit pair in the appropriate dictionary.
                    items[parent][new_key] = {"value": new_val,
                                              "unit": new_unit}
                else:
                    # Process items that are basically text, like notes.
                    new_val = get_value(new_info,
                                        missing_info="[?]")

                    # Store information in the appropriate dictionary.
                    items[parent][new_key] = new_val

        # Reset new_key.
        new_key = None


def fill_cone_dict(experiment_lines, institute_name_info,
                   exp_table_df, base_dict, material_path):
    """


    :param experiment_lines:
    :param institute_name_info:
    :param exp_table_df:
    :param base_dict:
    :param material_path:

    :return:
    """

    #
    experiment_type = "Cone Calorimeter"
    experiment_info = dict()
    repetition_info = dict()
    institute_label = institute_name_info[0]
    institute_name = institute_name_info[1]

    for test_label in exp_table_df["Test Label"][:]:
        # Remove unnecessary spaces.
        test_label = test_label.replace(" ", "")

        # Get line number of test.
        test_idx = exp_table_df[exp_table_df['Test Label'] == test_label].index[
            0]

        # Initialise experiment dictionary and fill in a copy of
        # the experiment description template.
        test_info = copy.deepcopy(base_dict)

        # Set institute name and label.
        test_info['laboratory']['label'] = institute_label
        test_info['laboratory']['name'] = institute_name

        # Get test label to build file name.
        data_file_name = exp_table_df['Test Label'][test_idx] + ".csv"
        print(data_file_name)

        # Build data file path.
        data_file_path = os.path.join(material_path.split("\\")[-2],
                                      material_path.split("\\")[-1],
                                      institute_label,
                                      data_file_name)
        # Store relative data file path.
        test_info['path'] = data_file_path

        # Set experiment description items from README.
        get_cone_items(md_lines=experiment_lines,
                       items=test_info,
                       multi_set=["backing", "thermocouple"])

        # Set heating rate.
        new_val = exp_table_df['Heat Flux (kW/m²)'][test_idx]
        new_unit = "kW/m²"
        test_info["heat_flux"] = {'value': new_val,
                                  'unit': new_unit}

        # Set initial sample mass.
        new_val = exp_table_df['Initial Sample Mass (g)'][test_idx]
        new_unit = "g"
        test_info["sample_mass"] = {'value': new_val,
                                    'unit': new_unit}

        repetition_info[test_label] = test_info

    experiment_info[institute_label] = repetition_info

    return repetition_info


def utility_build_base_dict(md_lines, exp_data_info=dict()):
    """
    Utility function to build a dictionary from points found in the README
    lines. This is intended to process the descriptions of the same
    experiment provided by the various contributors to easily find the
    different items used in the description. This helps to unify the README
    for a specific experiment across all contributors. It is not meant to be
    used  on a regular basis, but rather during the definition of the
    dictionaries for the different experiments during the early stages of the
    repository. After the definition of said dictionaries is settled, README
    templates are to be created and new contributions should follow that
    guidance.
    This functions is merely collected for completeness and might be useful
    if new types of experiments are included into the repo.

    :param md_lines: list of strings of the README-file content for a desired
                     experiment
    :param exp_data_info: dictionary that is to be populated with the
                          different items, makes it possible to provide the
                          dictionary externally for when multiple files are
                          to be processed

    :return: dictionary with the different markdown items
    """

    # # Initialise dictionary to collect the different README items.
    # exp_data_info = dict()

    recent_main_key = None

    # Read bullet points of markdown list and transform them
    # to dictionary keys.
    for line in md_lines:
        # Get medium items.
        if "* " in line and ": " in line:
            new_key = line[2:].split(':')[0].replace(' ', '_').lower()
            new_info = line[4:].split(':')[1]
            exp_data_info[new_key] = dict()

        # Get major items.
        elif "* " in line and ": " not in line:
            new_key = line[2:].replace(' ', '_').lower()
            recent_main_key = new_key
            # Check if a key-value pair of this type already exists,
            # to avoid overwriting it.
            if new_key in list(exp_data_info.keys()):
                continue
            else:
                exp_data_info[new_key] = dict()

        # Get minor items.
        elif "  - " in line and ": " in line:
            new_key = line[4:].split(':')[0].replace(' ', '_').lower()
            new_info = line[4:].split(':')[1]
            #             print(new_info)

            # Add a dictionary to store the item info.
            exp_data_info[recent_main_key][new_key] = dict()

        elif "  - " in line and ": " not in line:
            print(' * ERROR - check README layout! * ')
            print(line)
            print()

        else:
            # Catch cases that aren't expected keywords, e.g. empty lines.
            new_key = None

        # Select for expected keywords.
        if new_key is not None:
            if "heating_rate" in new_key:
                rx.findall(line)
                print(rx.findall(line))
                print(new_info)

    return exp_data_info


# def readme_items(md_lines, items):
#     """
#     Takes a list of markdown lines (string) of a desired experiment,
#     e.g. TGA, and a dictionary of the expected bullet points. It parses the
#     lines and extracts the information of the bullet points and stores them
#     in the dictionary. Bullet points are distinguished between major, medium
#     and minor. Major points are understood as some kind of heading that ties
#     multiple minor points together, e.g. description of crucibles. Medium
#     points stand on their own and only provide a single piece of
#     information, e.g. sample mass.
#
#     :param md_lines: list of strings (markdown file lines)
#     :param items: dictionary with expected bullet points as keys.
#
#     :return: Nothing; the existing dictionary is simply filled with the
#              appropriate values for the keys.
#     """
#
#     # Read bullet points of markdown list and transform them
#     # to dictionary keys.
#     for line in md_lines:
#         # Get medium items.
#         if "* " in line and ": " in line:
#             new_key = line[2:].split(':')[0].replace(' ', '_').lower()
#             new_info = line[4:].split(':')[1]
#         #             print(line)
#
#         # Get major items.
#         elif "* " in line and not ": " in line:
#             new_key = line[2:].replace(' ', '_').lower()
#             recent_main_key = new_key
#         #             print(line)
#
#         # Get minor items.
#         elif "  - " in line and ": " in line:
#             new_key = line[4:].split(':')[0].replace(' ', '_').lower()
#             new_info = line[4:].split(':')[1]
#         #             print(new_info)
#
#         else:
#             # Catch cases that aren't expected keywords, e.g. empty lines.
#             new_key = None
#
#         if new_key is not None:
#             if "heating_rate" in new_key:
#                 # Determine how many heating rates were used,
#                 # create a new dictionary for each. #TODO
#
#                 # Get all heating rates as list.
#                 heating_rates = rx.findall(line)
#
#                 # Get unit.
#                 heating_rate_unit = line[4:].split(' ')[-1]
#         #                 print('hr unit', heating_rate_unit)
#
#         #                 for heating_rate in rx.findall(line):
#         #                     print(heating_rate)
#         #                 print(rx.findall(line))
#         #                 print(new_info)
#
#         if new_key is not None:
#
#             #             # Set the heating rate.
#             #             new_val = 10
#             #             new_unit = "K/min"
#             #             items["heating_rate"] = {'value': new_val,
#             #                                      'unit': new_unit}
#
#             if "initial_temperature" in new_key:
#                 if not None:
#                     new_val = new_info.split(" ")[-2]
#                     new_unit = new_info.split(" ")[-1]
#                 else:
#                     new_val = None
#                     new_unit = None
#
#                 items[recent_main_key][new_key] = {'value': new_val,
#                                                    'unit': new_unit}
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "initial_isotherm" in new_key:
#                 if "None" not in new_info:
#                     new_val = new_info.split(" ")[-2]
#                     new_unit = new_info.split(" ")[-1]
#                 else:
#                     new_val = None
#                     new_unit = None
#
#                 items[recent_main_key][new_key] = {'value': new_val,
#                                                    'unit': new_unit}
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "maximum_temperature" in new_key:
#                 if "None" not in new_info:
#                     new_val = new_info.split(" ")[-2]
#                     new_unit = new_info.split(" ")[-1]
#                 else:
#                     new_val = None
#                     new_unit = None
#
#                 items[recent_main_key][new_key] = {'value': new_val,
#                                                    'unit': new_unit}
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "final_isotherm" in new_key:
#                 if "None" not in new_info:
#                     new_val = new_info.split(" ")[-2]
#                     new_unit = new_info.split(" ")[-1]
#                 else:
#                     new_val = None
#                     new_unit = None
#
#                 items[recent_main_key][new_key] = {'value': new_val,
#                                                    'unit': new_unit}
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "sample_mass" in new_key:
#                 if "None" not in new_info:
#                     new_val = new_info.split(" ")[-2]
#                     new_unit = new_info.split(" ")[-1]
#                 else:
#                     new_val = None
#                     new_unit = None
#
#                 items[new_key] = {'value': new_val,
#                                   'unit': new_unit}
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "sample_geometry" in new_key:
#                 if "None" not in new_info:
#                     new_val = new_info[1:]
#                 else:
#                     new_val = None
#
#                 items[new_key] = new_val
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "calibration_type" in new_key:
#                 if "None" not in new_info:
#                     new_val = new_info[1:]
#                 else:
#                     new_val = None
#
#                 items[new_key] = new_val
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "type" in new_key and "crucible" in recent_main_key:
#                 if "None" not in new_info:
#                     new_val = new_info[1:]
#                 else:
#                     new_val = None
#
#                 items[recent_main_key][new_key] = new_val
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "volume" in new_key and "crucible" in recent_main_key:
#                 if "None" not in new_info:
#                     new_val = new_info.split(" ")[-2]
#                     new_unit = new_info.split(" ")[-1]
#                 else:
#                     new_val = None
#                     new_unit = None
#
#                 items[recent_main_key][new_key] = {'value': new_val,
#                                                    'unit': new_unit}
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "diameter" in new_key and "crucible" in recent_main_key:
#                 if "None" not in new_info:
#                     new_val = new_info.split(" ")[-2]
#                     new_unit = new_info.split(" ")[-1]
#                 else:
#                     new_val = None
#                     new_unit = None
#
#                 items[recent_main_key][new_key] = {'value': new_val,
#                                                    'unit': new_unit}
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "mass" in new_key and "crucible" in recent_main_key:
#                 if "None" not in new_info:
#                     new_val = new_info.split(" ")[-2]
#                     new_unit = new_info.split(" ")[-1]
#                 else:
#                     new_val = None
#                     new_unit = None
#
#                 items[recent_main_key][new_key] = {'value': new_val,
#                                                    'unit': new_unit}
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "lid" in new_key and "crucible" in recent_main_key:
#                 if "None" not in new_info:
#                     new_val = new_info.split(" ")[-2]
#                     new_unit = new_info.split(" ")[-1]
#                 else:
#                     new_val = None
#                     new_unit = None
#
#                 items[recent_main_key][new_key] = {'value': new_val,
#                                                    'unit': new_unit}
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "note" in new_key and "crucible" in recent_main_key:
#                 if "None" not in new_info:
#                     new_val = new_info[1:]
#                 else:
#                     new_val = None
#
#                 items[recent_main_key][new_key] = new_val
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "type" in new_key and "carrier_gas" in recent_main_key:
#                 if "None" not in new_info:
#                     new_val = new_info[1:]
#                 else:
#                     new_val = None
#
#                 items[recent_main_key][new_key] = new_val
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "flow_rate" in new_key and "carrier_gas" in recent_main_key:
#                 if "None" not in new_info:
#                     new_val = new_info.split(" ")[-2]
#                     new_unit = new_info.split(" ")[-1]
#                 else:
#                     new_val = None
#                     new_unit = None
#
#                 items[recent_main_key][new_key] = {'value': new_val,
#                                                    'unit': new_unit}
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "note" in new_key and "carrier_gas" in recent_main_key:
#                 if "None" not in new_info:
#                     new_val = new_info[1:]
#                 else:
#                     new_val = None
#
#                 items[recent_main_key][new_key] = new_val
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "type" in new_key and "instrument" in recent_main_key:
#                 if "None" not in new_info:
#                     new_val = new_info[1:]
#                 else:
#                     new_val = None
#
#                 items[recent_main_key][new_key] = new_val
#             #                 print(new_info.split(" "), recent_main_key)
#
#             elif "note" in new_key and "instrument" in recent_main_key:
#                 if "None" not in new_info:
#                     new_val = new_info[1:]
#                 else:
#                     new_val = None
#
#                 items[recent_main_key][new_key] = new_val


def get_tga_items(md_lines, items):
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
        elif "* " in line and ": " not in line:
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


def get_dsc_items(md_lines, items):
    """
    Takes a list of markdown lines (string) of a desired experiment,
    e.g. DSC, and a dictionary of the expected bullet points. It parses the
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
        elif "* " in line and ": " not in line:
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


def build_major_bullet_point(exp_dict, bullet_point):
    """
    This function takes a desired major bullet point and its minor bullet
    points from an experiment description dictionary and translates it into
    a string. This string is a series of markdown items and can be written to a
    text file to be human-readable.

    :param exp_dict: dictionary containing the experiment description
    :param bullet_point: key (string) for the desired major bullet point

    :return: list of string
    """

    # Define string nuclei to build README lines.
    major_nucleus = "* {}"
    minor_nucleus = "  - {}: {}"

    # Initialise collection of README lines as list of string.
    new_lines = list()

    # Define major bullet point (heading).
    major_bullet = bullet_point.replace('_', ' ').title()
    major_bullet = major_nucleus.format(major_bullet)
    new_lines.append(major_bullet)

    # Define minor bullet points.
    for key in exp_dict[bullet_point].keys():
        if type(exp_dict[bullet_point][key]) is str:
            # Get bullet points that only hold a string, e.g. a note.
            value = exp_dict[bullet_point][key]

        elif type(exp_dict[bullet_point][key]) is None:
            # Get bullet points that contain no information, i.e. None.
            value = "None"

        else:
            if key is 'note':
                # Get the text of the note.
                value = exp_dict[bullet_point][key]

            elif exp_dict[bullet_point][key]['value'] is not None:
                # Concatenate value and measurement unit.
                value = "{} {}".format(exp_dict[bullet_point][key]['value'],
                                       exp_dict[bullet_point][key]['unit'])

            else:
                # Write only a single "None", instead one for the value
                # and one for the measurement unit.
                value = "None"

        # Construct and collect bullet point.
        new_bullet_point = key.replace('_', ' ').title()
        new_line = minor_nucleus.format(new_bullet_point, value)
        new_lines.append(new_line)

    return new_lines


def build_medium_bullet_point(exp_dict, bullet_point):
    """
    This function takes a desired medium bullet point from an
    experiment description dictionary and translates it into a string. This
    string is a markdown item and can be written to a text file to be
    human-readable.

    :param exp_dict: dictionary containing the experiment description
    :param bullet_point: key (string) for the desired medium bullet point

    :return: list of string
    """

    # Define string nucleus to build README lines.
    medium_nucleus = "* {}: {}"
    value_unit_nucleus = "{} {}"

    # Read the content of the bullet point.
    exp_content = exp_dict[bullet_point]

    # Initialise collection of README lines as list of string.
    new_lines = list()

    # Check if the content is a value with a unit or a description.
    if type(exp_content) is dict:
        value = exp_content["value"]
        unit = exp_content["unit"]
        new_bullet_content = value_unit_nucleus.format(value, unit)
    else:
        new_bullet_content = exp_dict[bullet_point]

    # Define medium bullet point (heading).
    new_bullet_point = bullet_point.replace('_', ' ').title()
    new_line = medium_nucleus.format(new_bullet_point, new_bullet_content)
    new_lines.append(new_line)

    return new_lines


def build_test_condition_table(test_condition_table_df):
    """
    Function to create a markdown table from a Pandas DataFrame.

    :param test_condition_table_df: DataFrame to be translated

    :return: list of string
    """

    # Initialise collection of README lines as list of string.
    new_lines = list()

    # Define string nucleus to build markdown table lines.
    table_line_nucleus = "|"
    table_entry_nucleus = "{}|"

    # Get column headers.
    column_headers = list(test_condition_table_df)
    n_columns = len(column_headers)

    # Build table header.
    table_line = "" + table_line_nucleus
    for column_header in column_headers:
        table_line += table_entry_nucleus.format(" " + column_header + " ")
    new_lines.append(table_line)

    # Build table divider.
    table_line = "" + table_line_nucleus
    for n_column in range(n_columns):
        table_line += table_entry_nucleus.format(":---:")
    new_lines.append(table_line)

    # Build table body.
    n_rows = len(test_condition_table_df[column_headers[0]])
    # Iterate over lines.
    for line in range(n_rows):
        table_line = "" + table_line_nucleus
        # Iterate over columns.
        for column_header in column_headers:
            entry = str(test_condition_table_df.iloc[line][column_header])
            #             entry = entry.replace("_", "\\_")
            table_line += table_entry_nucleus.format(" " + entry + " ")
        new_lines.append(table_line)

    return new_lines


def build_tga(tga_exp, exp_table_df=None):
    """
    This functions builds the README lines for the TGA experiments. Heating
    rate and sample masses are summarised.

    :param tga_exp: dictionary, containing the description of the different
                    repetitions of the TGA experiments
    :param exp_table_df: Pandas DataFrame containing the
                         test condition summary table

    :return: list of string for a new README file
    """

    # Initialise collection of README lines as list of string.
    tga_readme_lines = list()

    # Define string nuclei to build README lines.
    exp_header = "### Experimental Conditions, TGA"
    tga_readme_lines.append(exp_header)

    # Get keys of the different experiments.
    exp_keys = list(tga_exp.keys())

    # Heating Rates.
    heating_rates = list()
    # Get all heating rates.
    for exp_key in exp_keys:
        heating_rates.append(tga_exp[exp_key]["heating_rate"]["value"])
    # Remove duplicates.
    heating_rates = list(dict.fromkeys(heating_rates))
    # Build the summary of different heating rates.
    part_one = "{}".format(heating_rates[0])
    for heating_rate in heating_rates[1:-1]:
        part_one += ", {}".format(heating_rate)
    part_two = heating_rates[-1]
    unit = tga_exp[exp_key]["heating_rate"]["unit"]
    readme_lines = "* Heating Rates: {} and {} {}".format(part_one,
                                                          part_two,
                                                          unit)
    tga_readme_lines.append(readme_lines)

    # Temperature program.
    readme_lines = build_major_bullet_point(tga_exp[exp_keys[0]],
                                            "temperature_program")
    tga_readme_lines.append(readme_lines)

    # Sample mass.
    sample_masses = list()
    # Get all sample masses.
    for exp_key in exp_keys:
        sample_masses.append(tga_exp[exp_key]["sample_mass"]["value"])
    # Remove duplicates.
    sample_masses = list(dict.fromkeys(sample_masses))
    # Build the summary of different sample masses.
    unit = tga_exp[exp_key]["sample_mass"]["unit"]
    readme_lines = "* Sample Mass: {} - {} {}".format(min(sample_masses),
                                                      max(sample_masses),
                                                      unit)
    tga_readme_lines.append(readme_lines)

    # Sample geometry.
    readme_lines = build_medium_bullet_point(tga_exp[exp_keys[0]],
                                             "sample_geometry")
    tga_readme_lines.append(readme_lines)

    # Calibration type
    readme_lines = build_medium_bullet_point(tga_exp[exp_keys[0]],
                                             "calibration_type")
    tga_readme_lines.append(readme_lines)

    # Crucible
    readme_lines = build_major_bullet_point(tga_exp[exp_keys[0]],
                                            "crucible")
    tga_readme_lines.append(readme_lines)

    # Carrier Gas
    readme_lines = build_major_bullet_point(tga_exp[exp_keys[0]],
                                            "carrier_gas")
    tga_readme_lines.append(readme_lines)

    # Instrument
    readme_lines = build_major_bullet_point(tga_exp[exp_keys[0]],
                                            "instrument")
    tga_readme_lines.append(readme_lines)

    # Test condition summary table
    if exp_table_df is not None:
        table_header = "###### Test Condition Summary"
        tga_readme_lines.append(table_header)
        table_lines = build_test_condition_table(exp_table_df)
        tga_readme_lines.append(table_lines)

    # Flatten list of new README lines.
    tga_readme_lines = list(pd_flatten(tga_readme_lines))
    return tga_readme_lines


def build_dsc(dsc_exp, exp_table_df=None):
    """
    This functions builds the README lines for the DSC experiments. Heating
    rate and sample masses are summarised.

    :param dsc_exp: dictionary, containing the description of the different
                    repetitions of the DSC experiments
    :param exp_table_df: Pandas DataFrame containing the
                         test condition summary table

    :return: list of string for a new README file
    """

    # Initialise collection of README lines as list of string.
    dsc_readme_lines = list()

    # Define string nuclei to build README lines.
    exp_header = "### Experimental Conditions, DSC"
    dsc_readme_lines.append(exp_header)

    # Get keys of the different experiments.
    exp_keys = list(dsc_exp.keys())

    # Heating Rates.
    heating_rates = list()
    # Get all heating rates.
    for exp_key in exp_keys:
        heating_rates.append(dsc_exp[exp_key]["heating_rate"]["value"])
    # Remove duplicates.
    heating_rates = list(dict.fromkeys(heating_rates))
    # Build the summary of different heating rates.
    part_one = "{}".format(heating_rates[0])
    for heating_rate in heating_rates[1:-1]:
        part_one += ", {}".format(heating_rate)
    part_two = heating_rates[-1]
    unit = dsc_exp[exp_key]["heating_rate"]["unit"]
    readme_lines = "* Heating Rates: {} and {} {}".format(part_one,
                                                          part_two,
                                                          unit)
    dsc_readme_lines.append(readme_lines)

    # Temperature program.
    readme_lines = build_major_bullet_point(dsc_exp[exp_keys[0]],
                                            "temperature_program")
    dsc_readme_lines.append(readme_lines)

    # Sample mass.
    sample_masses = list()
    # Get all sample masses.
    for exp_key in exp_keys:
        sample_masses.append(dsc_exp[exp_key]["sample_mass"]["value"])
    # Remove duplicates.
    sample_masses = list(dict.fromkeys(sample_masses))
    # Build the summary of different sample masses.
    unit = dsc_exp[exp_key]["sample_mass"]["unit"]
    readme_lines = "* Sample Mass: {} - {} {}".format(min(sample_masses),
                                                      max(sample_masses),
                                                      unit)
    dsc_readme_lines.append(readme_lines)

    # Sample geometry.
    readme_lines = build_medium_bullet_point(dsc_exp[exp_keys[0]],
                                             "sample_geometry")
    dsc_readme_lines.append(readme_lines)

    # Calibration type
    readme_lines = build_medium_bullet_point(dsc_exp[exp_keys[0]],
                                             "calibration_type")
    dsc_readme_lines.append(readme_lines)

    # Crucible
    readme_lines = build_major_bullet_point(dsc_exp[exp_keys[0]],
                                            "crucible")
    dsc_readme_lines.append(readme_lines)

    # Carrier Gas
    readme_lines = build_major_bullet_point(dsc_exp[exp_keys[0]],
                                            "carrier_gas")
    dsc_readme_lines.append(readme_lines)

    # Instrument
    readme_lines = build_major_bullet_point(dsc_exp[exp_keys[0]],
                                            "instrument")
    dsc_readme_lines.append(readme_lines)

    # Test condition summary table
    if exp_table_df is not None:
        table_header = "###### Test Condition Summary"
        dsc_readme_lines.append(table_header)
        table_lines = build_test_condition_table(exp_table_df)
        dsc_readme_lines.append(table_lines)

    # Flatten list of new README lines.
    dsc_readme_lines = list(pd_flatten(dsc_readme_lines))
    return dsc_readme_lines


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
        'path': {}},
    "DSC_base": {
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
        'path': {}},
    "Cone_base": {
        'laboratory': {},
        'heat_flux': {},
        'sample': {
            'material': {},
            'mass': {},
            'shape': {},
            'diameter_or_edge_length': {},
            'exposed_surface_area_(nominal)': {},
            'thickness': {},
            'note': {}},
        'sample_holder': {
            'shape': {},
            'retainer_frame': {},
            'retaining_grid': {},
            'note': {}},
        'sample_chamber': {
            'top_opening': {},
            'doors_windshield': {},
            'bottom_opening': {},
            'note': {}},
        'backing': {
            # 'material_1': {},
            # 'thickness_1': {},
            # 'density_1': {},
            # 'conductivity_1': {},
            # 'specific_heat_capacity_1': {},
            # 'note_1': {}
        },
        'thermocouple': {
            # 'type_1': {},
            # 'location_1': {},
            # 'surface_1': {},
            # 'note_1': {}
        },
        'carrier_gas': {
            'type': {},
            'flow_rate': {},
            'note': {}},
        'calibration': {
            'type': {},
            'frequency': {},
            'note': {}},
        'instrument': {
            'manufacturer': {},
            'apparatus_and_model_number': {},
            'note': {}},
        'path': {}}
}
