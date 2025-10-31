""""
This sample shows how to get and set data for the project information dialog
"""

import iesve
import pprint
pp = pprint.PrettyPrinter(indent=4)

project_info = iesve.ProjectInfo()

# Read
pp.pprint(project_info.get())

# Write
project_info_data = {
    'address': 'IES HQ',
    'building_owner': 'IES',
    'conditioned_floor_area': '200',
    'design_team': 'IES Consulting',
    'energy_analyst': 'Joe Bloggs',
    'project_name': 'Helix Building'
    }

project_info.set(project_info_data)
