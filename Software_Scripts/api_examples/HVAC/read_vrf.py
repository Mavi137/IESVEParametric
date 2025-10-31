""""
This sample shows how to get HVAC VRFV data
"""

import iesve   # the VE api
from ies_file_picker import IesFilePicker
import pprint
pp = pprint.PrettyPrinter()

# Open ASP file:
file_name = IesFilePicker.pick_asp_file()

# Load HVAC network
hvac = iesve.HVACNetwork
network = hvac.load_network(file_name)

# Display the VRF systems data
vrf_systems = network.vrf_systems
for vrf_system in vrf_systems:
    print("")
    print(vrf_system)
    print("-------------", vrf_system.id, "-------------")
    print("Reference:", vrf_system.reference)
    
    print("System data:")
    pp.pprint(vrf_system.system_data)
    
    print("Design parameters:")
    pp.pprint(vrf_system.design_parameters)
    
    print("Design condition outdoor unit data:")
    pp.pprint(vrf_system.design_condition_outdoor_unit_data)
    
    print("Reference condition outdoor unit data:")
    pp.pprint(vrf_system.reference_condition_outdoor_unit_data)
    
    print("Reference condition indoor unit data:")
    pp.pprint(vrf_system.reference_condition_indoor_unit_data)