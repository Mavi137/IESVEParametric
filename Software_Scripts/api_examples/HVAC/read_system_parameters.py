""""
This sample shows how to get system parameters data
"""

import iesve   # the VE api
import pprint
pp = pprint.PrettyPrinter(indent=4)

from ies_file_picker import IesFilePicker

# Open APS file:
file_name = IesFilePicker.pick_aps_file()

# Load the HVAC network
with iesve.ResultsReader.open(file_name) as results_file_reader:
    hvac = iesve.HVACNetwork
    network = hvac.load_network(results_file_reader.hvac_file)
    
    # Print the system parameters for each system
    for system_id, system in network.systems_dict.items():
        print("----------------------------------")
        print(system_id)
        sys_params = system.get_system_parameters()
        num_layers = system.number_of_layers
        
        print("\nSchedules:")
        pp.pprint(sys_params.get_schedules())
        
        layer = 0
        while layer < num_layers:
            print ("\nLayer:", layer)
            print ("\nSystem Parameters:")
            pp.pprint(sys_params.get_system_parameters(layer))
            print ("\nZone Temperature, Humidity & Equipment:")
            pp.pprint(sys_params.get_zone_temperature_humidity_equipment(layer))
            print ("\nZone Ventilation & Exhaust:")
            pp.pprint(sys_params.get_zone_ventilation_exhaust(layer))
            print ("\nZone Loads & Supply Airflows:")
            pp.pprint(sys_params.get_zone_loads_airflows(layer))
            print ("\nZone Airflows, Turndown & Engineering:")
            pp.pprint(sys_params.get_zone_airflows_turndown_engineering(layer))
            layer = layer + 1
