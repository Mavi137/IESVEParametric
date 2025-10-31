""""
This sample sets room data
"""

import iesve    # the VE api
   
project = iesve.VEProject.get_current_project()
real_building = project.models[0]

# get all the bodies in the building
bodies = real_building.get_bodies(False)
for body in bodies:
    # skip any bodies that aren't thermal rooms
    if body.type != iesve.VEBody_type.room:
        continue

    # the Real building stores generic data
    # so ask for generic room data
    room_data = body.get_room_data(iesve.attribute_type.real_attributes)
    
    # Prepare the data to set
    # If setting templates to True, do not set the corresponding values
    
    # General
    general_data = { 'circ_perc': 0,
                     'circ_perc_from_template': False,
                     'included_in_building_floor_area': True,
                     'included_in_building_floor_area_from_template': False,
                     'lettable_perc': 100,
                     'lettable_perc_from_template': False,
                     'name': 'PYROOM'}
    
    # Room conditions
    room_conditions_data = { 'cooling_profile': 'ON',
                             'cooling_profile_from_template': False,
                             'cooling_setpoint': 0.0,
                             'cooling_setpoint_type': iesve.setpoint_type.variable,
                             'cooling_setpoint_from_template': False,
                             'cooling_setpoint_profile': '0',
                             'dhw': 10.0,
                             'dhw_from_template': False,
                             'dhw_linked_to_occupancy': False,
                             'dhw_linked_to_occupancy_from_template': False,
                             'dhw_profile': 'ON',
                             'dhw_profile_from_template': False,
                             'furniture_mass_factor': 1.0,
                             'furniture_mass_factor_from_template': False,
                             'heating_profile': 'ON',
                             'heating_profile_from_template': False,
                             'heating_setpoint': 0.0,
                             'heating_setpoint_type': iesve.setpoint_type.variable,
                             'heating_setpoint_from_template': False,
                             'heating_setpoint_profile': '0',
                             'plant_profile': 'ON',
                             'plant_profile_from_template': False,
                             'plant_profile_type': 0,
                             'sat_perc_lower': 0.0,
                             'sat_perc_lower_from_template': False,
                             'sat_perc_upper': 100.0,
                             'sat_perc_upper_from_template': False,
                             'solar_reflected_fraction': 0.05,
                             'solar_reflected_fraction_from_template': False}
    # System Data
    system_data = { 'HVAC_system': 'SYST0000',
                    'HVAC_system_from_template': False,
                    'HVAC_methodology': iesve.hvac_methodology.apache_system,
                    'HVAC_methodology_from_template': False,
                    'aux_vent_system': 'SYST0000',
                    'aux_vent_system_from_template': False,
                    'aux_vent_system_same': True,
                    'conditioned': iesve.conditioned_flag.yes,
                    'cooling_capacity_unit': -1,
                    'cooling_capacity_unlimited': False,
                    'cooling_capacity_unlimited_from_template': False,
                    'cooling_capacity_value': 0.0,
                    'cooling_plant_radiant_fraction': 0.0,
                    'cooling_plant_radiant_fraction_from_template': False,
                    'cooling_unit_size': 0.0,
                    'dhw_system': 'SYST0000',
                    'dhw_system_from_template': False,
                    'dhw_system_same': True,
                    'extract_fan_is_remote': False,
                    'extract_flow_rate': 0.8,
                    'extract_flow_rate_unit': 2,
                    'has_mech_exhaust': False,
                    'heating_capacity_unit': -1,
                    'heating_capacity_unlimited': False,
                    'heating_capacity_unlimited_from_template': False,
                    'heating_capacity_value': 0.0,
                    'heating_plant_radiant_fraction': 0.2,
                    'heating_plant_radiant_fraction_from_template': False,
                    'heating_unit_size': 0.0,
                    'system_air_free_cooling': 0.0,
                    'system_air_free_cooling_from_template': False,
                    'system_air_minimum_flowrate': 0.8,
                    'system_air_minimum_flowrate_from_template': False,
                    'system_air_variation_profile': 'OFF',
                    'system_air_variation_profile_from_template': False,
                    'cooling_design_supply_air_temperature': 12.78,
                    'cooling_design_supply_air_temperature_from_template': False,
                    'heating_design_supply_air_temperature': 32.22,
                    'heating_design_supply_air_temperature_from_template': False}
             
    room_data.set(general_data, room_conditions_data, system_data)
    break

print("Room data set!")