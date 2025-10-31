""""
This sample shows how to get data from energy meters and sources
"""

import iesve   # the VE api
import pprint
pp = pprint.PrettyPrinter(indent=4)

# Output all energy source data
energy_source_data = iesve.EnergySources.get_all_energy_source_data()
pp.pprint(energy_source_data)

# Output all energy meter data
for energy_source in energy_source_data:
    for energy_meter in energy_source['meters']:
        pp.pprint(energy_meter.get())