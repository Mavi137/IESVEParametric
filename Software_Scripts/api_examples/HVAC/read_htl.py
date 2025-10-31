""""
This sample shows how to get Heat Transfer Loop data
"""

import iesve # the VE api
from ies_file_picker import IesFilePicker
import pprint
pp = pprint.PrettyPrinter()

# Open APS file:
file_name = IesFilePicker.pick_aps_file()

# Load the HVAC network
with iesve.ResultsReader.open(file_name) as results_file_reader:
    hvac = iesve.HVACNetwork
    network = hvac.load_network(results_file_reader.hvac_file)

    # Print HVAC data
    print("\nNetwork Name: " + network.name)
    print("Network Path: " + network.path)
    
    print("-----------------")
    
    for component in network.components:
        if isinstance(component, iesve.HVACHeatingCoil):
            htl = component.htl
            print('----')
            if htl:
                output = {}
                output['name'] = htl.reference
                output['oversizing_factor'] = htl.oversizing_factor
                output['heating_capacity'] = htl.heating_capacity
                output['cooling_capacity'] = htl.cooling_capacity
                output['flow_rate'] = htl.flow_rate
                output['primary_pump_power'] = htl.primary_pump_power
                output['secondary_pump_power'] = htl.secondary_pump_power
                output['heat_acquisition_chr_capacity'] = htl.heat_acquisition_chr_capacity
                output['heat_acquisition_chr_wwhp_capacity'] = htl.heat_acquisition_chr_wwhp_capacity
                output['heat_acquisition_awhp_capacity'] = htl.heat_acquisition_awhp_capacity
                output['water_source_heat_exchanger_heating_capacity'] = htl.water_source_heat_exchanger_heating_capacity
                output['water_source_heat_exchanger_cooling_capacity'] = htl.water_source_heat_exchanger_cooling_capacity
                output['heat_rejection_equipment_capacity_cooling_tower'] = htl.heat_rejection_equipment_capacity_cooling_tower
                output['heat_rejection_equipment_capacity_fluid_cooler'] = htl.heat_rejection_equipment_capacity_fluid_cooler
                
                output["boilers"] = []
                for boiler in htl.boilers:              
                    boiler_data = {}
                    boiler_data["name"] = boiler.reference
                    boiler_data["capacity"] = boiler.output_capacity_all_kw
                    output["boilers"].append(boiler_data)

                pp.pprint(output)