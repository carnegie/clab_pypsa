import os, csv
import pandas as pd


def check_directory(directory):
    """
    Check if directory exists, if not create it
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def strip_quotes(string):
    """
    Strip string of leading and trailing single and double quotes, if present
    """
    if string is None:
        return None
    if string.startswith('"') and string.endswith('"'):
        return string[1:-1]
    if string.startswith("'") and string.endswith("'"):
        return string[1:-1]
    return string


def remove_empty_rows(list_of_lists):
    """
    Eliminate all lists in a list of lists that are empty or contain only empty strings
    """
    return [row for row in list_of_lists if not all(x is None for x in row)]


def find_first_row_with_keyword(list_of_lists, keyword):
    """
    Return as integer the index of first list in list of lists that only has a keyword in the first element, 
    checking in a case insensitive manner
    """
    for i in range(len(list_of_lists)):
        if not ( keyword is None or list_of_lists[i][0] is None):
            if keyword.lower() == list_of_lists[i][0].lower():
                return i
    return -1


def check_attributes(element_list, dict_of_lists):
    """
    Return true if all elements of a list are in any of the lists in a dictionary of lists or are empty strings or all spaces, else return the elements that are not in any of the lists in the dictionary
    """
    for element in element_list:
        if element != None:
            if not any(element in dict_of_lists[key].index for key in dict_of_lists):
                return False, element
    return True, None


def concatenate_list_of_strings(list_of_strings):
    """
    Concatenate list of strings into a single string separated by spaces
    """
    if type(list_of_strings) is list:
        return ' '.join(list_of_strings)
    else:
        return list_of_strings


def is_number(s):
    """
    Check if a string is a number
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_nyears(start, end):
    """
    Return the number of years in the time series
    """
    time = pd.date_range(start, end, freq='h')
    # Drop Feb 29 when leap year
    if time.is_leap_year.any():
        time = time[~((time.month == 2) & (time.day == 29))]
    nyears = len(time) / 8760
    return nyears


def skip_until_keyword(ts_file, keyword):
    """
    Number of rows to skip until beginning of data in time series csv file.
    Returns the line index of the keyword, or 0 if the keyword is not found.
    """
    with open(ts_file, encoding='utf-8-sig') as fin:
        # Read to keyword and then one more line (header line)
        data_reader = csv.reader(fin)
        line_index = 1
        try:
            while True:
                line = next(data_reader)
                if line[0] == keyword:
                    return line_index
                line_index += 1
        except StopIteration:
            return 0  # Return 0 if the keyword is not found


def get_output_filename(case_input_dict):
    """
    return generated output file pathname
    """
    check_directory(case_input_dict["output_path"])
    check_directory(os.path.join(case_input_dict["output_path"], case_input_dict["case_name"]))
    outfile = os.path.join(case_input_dict["output_path"], case_input_dict["case_name"], case_input_dict["filename_prefix"])
    return outfile

def stats_add_units(n_stats, case_input_dict):
    """
    return statistics dataframe with units added to column names
    """
    stats = n_stats(groupby=False).copy()
    for col in stats.columns:
        if "Capital Expenditure" in col or "Revenue" in col:
            unit = " [{}]".format(case_input_dict["currency"])
        elif "Operational Expenditure" in col:
            unit = " [{}]".format(case_input_dict["currency"])
        elif "Curtailment" in col or "Dispatch" in col:
            unit = " [{0}{1}]".format(case_input_dict["power_unit"], case_input_dict["time_unit"])
        elif "Market Value" in col:
            unit = " [{0}/{1}{2}]".format(case_input_dict["currency"], case_input_dict["power_unit"], case_input_dict["time_unit"])
        elif not "Factor" in col :
            unit = " [{}]".format(case_input_dict["power_unit"])  
        else:
            unit = ""
        stats.rename(columns={col: col+unit}, inplace=True)
    return stats

def add_carrier_info(network, stats_df):
    """
    Add carrier information to statistics DataFrame
    """
    # Initialize a list to hold the carrier information
    carriers = []
    sorted_components = sorted(network.iterate_components(), key=lambda x: x.name)
    # Iterate over components
    for component_class in sorted_components:
        if component_class.name == "Bus":
            continue
        # Collect carriers
        components = getattr(network, component_class.list_name)
        # Sort components by index
        if hasattr(components, "carrier"):
            sorted_carriers = components.sort_index().carrier.tolist()
            carriers.extend(sorted_carriers)
    # Add the carrier info to your statistics DataFrame
    stats_df.insert(0, "carrier", carriers)

    return stats_df
