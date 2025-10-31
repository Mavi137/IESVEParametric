""""
This sample sets thermal template data
"""

import iesve   # the VE api

# Get the current VE project.  
# Getting the thermal templates is a project-level operation
proj = iesve.VEProject.get_current_project()

# Get a list of the known thermal templates
# Pass True to only get templates in use (assigned), False to get all templates
templates = proj.thermal_templates(False)
    
# the templates are returned as a dictionary
# for this sample we don't need the key (the template handle)
# so iterate over the dictionary values only
templates_iter = templates.values()
for template in templates_iter:
    
    # we can check the type of a template by checking its 'standard' attribute
    # this returns an enum that can represent: generic, NCM, or PRM
    # this allows filtering of templates similar to BTM's behaviour of not showing
    # NCM templates by default
    if template.standard != iesve.VEThermalTemplate_standard.generic:
        continue  # skip PRM and NCM templates
    
    sys_settings = { 'HVAC_system': 'SYST0000',
                     'HVAC_methodology': iesve.hvac_methodology.apache_system,
                     'conditioned': iesve.conditioned_flag.yes,
                     'aux_vent_system': 'SYST0000',
                     'aux_vent_system_same': False,
                     'cooling_capacity_units': iesve.heating_cooling_capacity_unit.unlimited,
                     'cooling_capacity_value': 0.0,
                     'cooling_plant_radiant_fraction': 0.0,
                     'dhw_system': 'SYST0000',
                     'dhw_system_same': False,
                     'heating_capacity_units': iesve.heating_cooling_capacity_unit.unlimited,
                     'heating_capacity_value': 0.0,
                     'heating_plant_radiant_fraction': 0.2,
                     'system_air_free_cooling': 0.0,
                     'system_air_free_cooling_units': 0,
                     'system_air_minimum_flowrate': 0.800000011920929,
                     'system_air_minimum_flowrate_units': 2,
                     'system_air_variation_profile': 'OFF'}
    
    room_settings = {'sat_perc_lower': 0.0,
                     'heating_setpoint': 19.0,
                     'cooling_setpoint': 23.0,
                     'dhw_units': 'l/h',
                     'cooling_setpoint_profile': '0',
                     'dhw_profile': '-', 
                     'plant_profile_type': 0, 
                     'dhw': 10.0,
                     'cooling_setpoint_type': iesve.setpoint_type.constant,
                     'cooling_profile': 'ON',
                     'plant_profile': 'ON',
                     'sat_perc_upper': 100.0, 
                     'heating_setpoint_type': iesve.setpoint_type.constant,
                     'heating_profile': 'ON', 
                     'heating_setpoint_profile': '0'}
    
    template.set(room_settings, sys_settings)
    template.apply_changes()
    
print("Templates set!")
