""""
Sample to query a simulation result file (APS file) and display results
in both IP and Metric units

A results file can be read at building level, room level and system level
as well as weather variables.

The variable level is represented by a single character, as follows, with the
corresponding API for reading the data:
    w = weather                 get_weather_results
    z = room level (zone)       get_room_results
    v = apache systems misc     get_apache_system_results
    j = apache systems energy   get_apache_system_results
    r = apache systems carbon   get_apache_system_results
    l = building load           get_results
    e = building energy         get_results
    c = building carbon         get_results
    n = HVAC node level         get_hvac_node_results
    h = HVAC component level    get_hvac_component_results
    
APS files are queried by an internal variable name.  This sample shows how
to convert a Vista / VistaPro display variable + variable level combination
to an APS file results name.

A list of known variables is supplied by the API, as well as a corresponding
units dictionary.  The units dictionary contains the information to convert
numbers to both IP and Metric display variables.
"""

import iesve        # the VE api
import numpy as np  # numeric data series returned as numpy arrays
import sys
from ies_file_picker import IesFilePicker


#helper function, finds variable by name and category (level)
def find_variable(vista_display_name, var_level):
    """
    This searches the list of variables for one that matches the Vista/VistaPro 
    display name (and variable level).  
    The variable details are then returned, or None if the variable wasn't found
    """
    for variable in aps_variables:
        if variable['display_name'] == vista_display_name and variable['model_level'] == var_level:
            return variable
            
    return None

# helper function, convert units from internal APS units to display units
def convert_units(value, units):
    return (value / units['divisor']) + units['offset']
    
# helper function, makes a string out of the various numbers + unit display name
def make_display_string(sum, min, max, mean, units):
    return "{:,.2f} / {:,.4f} / {:,.4f} / {:,.4f} {}".format(
        convert_units(sum, units),
        convert_units(min, units),
        convert_units(max, units), 
        convert_units(mean, units),
        units['display_name']
        )

# This function reads an APS variable for a particular variable
# It then does some basic calcs on the results (min/max/mean/annual sum)
# and prints out the result
def read_variable(result_reader, result_variable):
    """
    This reads an energy or loads building-level variable from the results file.
    The value is then converted to Wh to accomodate result files that don't
    operate at an hourly value
    A result set is displayed including both annual sum, min, and max
    """
    assert result_variable is not None, "Error: missing variable data"
    
    # Get the units data for this variable
    units_for_this_variable = aps_units[result_variable['units_type']]
    units_metric = units_for_this_variable['units_metric']
    units_ip = units_for_this_variable['units_IP']

    # Step one: query the results file for the variable
    aps_data = result_reader.get_results(result_variable['aps_varname'], result_variable['display_name'], result_variable['model_level'])
        
    # Check if the read was successful
    if aps_data is None:
        print("Error reading variable: " + result_variable['display_name'], file=sys.stderr)
        return 0

    # Calculate some peak values - note that for energy / loads variables, these will be in W units
    val_min = np.min(aps_data)
    val_max = np.max(aps_data)
    mean_val = np.average(aps_data)

    # now calculate annual total: this will be in Wh
    # because results data is not hourly, we need adjust W to Wh by
    # adjusting for results per hour
    # Convert W -> Wh, then calculate annual total
    aps_data *= (24 / result_reader.results_per_day)
    annual_total = np.sum(aps_data)
    
    # print the results
    print("Variable: {}".format(result_variable['display_name']))
    print("  Metric  Sum/Min/Max/Mean: {}".format(make_display_string(
        annual_total, val_min, val_max, mean_val, units_metric)))
    print("  IP      Sum/Min/Max/Mean: {}".format(make_display_string(
        annual_total, val_min, val_max, mean_val, units_ip)))

    # clean up memory for the results array
    del aps_data

# Main function, open the APS file and decide which variables to query
if __name__ == "__main__":
    # Open APS file:
    file_name = IesFilePicker.pick_aps_file()
    with iesve.ResultsReader.open(file_name) as results_file_reader:
        assert results_file_reader is not None, "Error opening results file"
        
        # get the variables and units for this file
        aps_variables = results_file_reader.get_variables()
        aps_units = results_file_reader.get_units()
        
        # Read variables and display some results
        read_variable(results_file_reader, find_variable('Boilers load', 'l'))
        read_variable(results_file_reader, find_variable('Chillers load', 'l'))
        read_variable(results_file_reader, find_variable('Total electricity', 'e'))
        read_variable(results_file_reader, find_variable('Total energy', 'e'))
