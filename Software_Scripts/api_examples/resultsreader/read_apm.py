""""
Shows how to read an APM file's rooms, variables and results.

"""

import iesve        # the VE api
import numpy as np  # numeric data series returned as numpy arrays

from ies_file_picker import IesFilePicker

file_name = IesFilePicker.pick_apm_file()
file1 = iesve.ResultsReader.open(file_name)
apm_rooms = file1.get_room_list()
apm_variables = file1.get_variables()
apm_units = file1.get_units()

assert len(apm_variables) > 0, "Error: no APM variables loaded.  Missing project vistaset.ies file?"

# for demo purposes, we try and read all variables that are defined here
for var in apm_variables:
    
    # an APM can contain a mix of standard (system) variables and project (APM-specific)
    # variables.  For the sake of this sample, we'll only process APM-specific 
    # (variable source = project) variables
    if var['source'] is not iesve.VariableSource.project:
        continue

    # a variable has the name of its units in the dictionary key units_type
    # find the corresponding units details in the units dictionary
    units_for_this_variable = apm_units[var['units_type']]
    units_metric = units_for_this_variable['units_metric']
    units_ip = units_for_this_variable['units_IP']
    
    # different levels of variables (model level, room level, etc) require different APIs
    # so we check which model level this variable has, then call the appropriate API
    
    # first variable type: room level data ('z')
    if var['model_level'] == 'z':
        # room-level variable, so we try and read it for all rooms
        # if a get_room_results call fails, it will return None and we skip it
        num_rooms = rooms_total = 0
        for room in apm_rooms:
            # room[1] is the room ID, and we query by variable name and variable level
            res = file1.get_room_results(room[1], var['aps_varname'], var['display_name'], var['model_level'])
            if res is not None:
                if len(res) > 0:
                    # for demo purposes, just sum the results together
                    # note that APM variables can have NaN values where no data was recorded
                    rooms_total += np.nansum(res)
                    num_rooms += 1
        # now that all rooms were processed, output a wee message
        msg = 'Room variable: {}, found in {} rooms. Total Metric value: {} {}, IP value: {} {}'
        print(msg.format(var['display_name'], num_rooms, 
            (rooms_total / units_metric['divisor']) + units_metric['offset'], units_metric['display_name'],
            (rooms_total / units_ip['divisor']) + units_ip['offset'], units_ip['display_name']
            ))
    elif var['model_level'] in ['h', 'n']:
        # don't know how to process HVAC variables yet
        msg = "Variable: {} of type {}, network-level variables coming soon..."
        print(msg.format(var['display_name'], var['model_level']))
    else:
        res = file1.get_results(var['aps_varname'], var['display_name'], var['model_level'])
        if res is None:
            msg = "Model level variable: {}, returned no results"
            print(msg.format(var['display_name']))
        else:
            msg = "Model level variable: {}, num results: {}"
            print(msg.format(var['display_name'], len(res)))

file1.close()
del apm_rooms
del apm_variables
del apm_units
