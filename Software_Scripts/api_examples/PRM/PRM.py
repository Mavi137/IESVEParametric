""""
This sample shows how to get and set PRM data
"""

import iesve        # the VE api
import pprint
pp = pprint.PrettyPrinter(indent=4)

prm = iesve.PRM()

# Modify this so that there is one entry for each of the spaces in your model
thermal_comfort_room_categories_data = [{'activity': 'Room (ApSys, metric)',
        'analyse': False,
        'id': 'RM000000',
        'name': 'room'},
    {   'activity': 'Room (ApSys, metric)',
        'analyse': True,
        'id': 'RM000001',
        'name': 'room2'}]

unmet_load_hour_parameters = {'override_hvac_throttling_ranges': True, 'cooling_tolerance': 3, 'heating_tolerance': 3, 'exclude_nonmaster_rooms': False}

original_thermal_comfort= prm.get_thermal_comfort_room_categories_data()
original_unmet_load = prm.get_unmet_load_hour_parameters()
prm.set_thermal_comfort_room_categories_data(thermal_comfort_room_categories_data)
prm.set_unmet_load_hour_parameters(unmet_load_hour_parameters)

pp.pprint(prm.get_thermal_comfort_room_categories_data())
pp.pprint(prm.get_unmet_load_hour_parameters())

prm.set_thermal_comfort_room_categories_data(original_thermal_comfort)
prm.set_unmet_load_hour_parameters(original_unmet_load)

pp.pprint(prm.get_designer_contractor())

pp.pprint(prm.get_owner_agent())

pp.pprint(prm.get_site_permit_software())

florida_data = prm.get_florida()
prm.set_florida(florida_data)
pp.pprint(florida_data)

florida_certifications_data = prm.get_florida_certifications()
prm.set_florida_certifications(florida_certifications_data)
pp.pprint(florida_certifications_data)

print("Draw pattern:", prm.get_draw_pattern())