""""
This sample sets NCM room data
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
    room_data = body.get_room_data(iesve.attribute_type.ncm_attributes)
    room_data.set_collector_area(surface_number = 1, collector_area = 100)
    
    room_data.set_building_regs(
    {'air_permeability': 1.0,
    'associated_occupied_room': '',
    'destratification_fans': False,
    'dhw_pipe_length': 3.0,
    'external_ventilation_rate': 1.0,
    'external_ventilation_rate_from_template': False,
    'high_pressure_drop_air_treatment': 1.0,
    'high_pressure_drop_air_treatment_from_template': False,
    'include_room_in_building_regs_analysis': True,
    'ncm_activity': 'NCM Office: Office',
    'ncm_activity_from_template': False,
    'ncm_building_area_type': 'NCM OfficeOrWorkshop (Office)',
    'ncm_building_area_type_from_template': False,
    'room_part_of_core_area': True,
    'room_type': iesve.room_type.heated,
    'room_type_from_template': False,
    'section_63_loft_access': False,
    'section_63_loft_access_from_template': True}
    )
    
    room_data.set_ncm_lighting(
    {'automatic_daylight_zoning': True,
    'automatic_daylight_zoning_percentage': 100,
    'constant_illuminance_control': True,
    'control_type': iesve.photoelectric_control_type.dimming,
    'design_illuminance': 500.0,
    'different_sensor_control_back': True,
    'display_lighting_time_switching': True,
    'lamp_efficacy': 22.0,
    'lamp_type': iesve.lamp_types.t8_halophosphate_fluorescent_low_frequency,
    'light_output_ratio': 0.5,
    'lighting_case': iesve.lighting_case.full,
    'lumens_circuit_watt': 200.0,
    'luminaires_fitted': False,
    'occupancy_parasitic_power': 0.3,
    'occupancy_parasitic_power_default': False,
    'occupancy_parasitic_power_unit': iesve.wattage_unit.wm2,
    'occupancy_sensing': iesve.occupancy_sensing.manual_on_auto_off,
    'occupancy_time_switch_control': True,
    'photoelectric_parasitic_power': 0.1,
    'photoelectric_parasitic_power_default': False,
    'photoelectric_parasitic_power_unit': iesve.wattage_unit.wm2,
    'photoelectric_time_switch_control': True,
    'sensor_type': iesve.sensor_type.addressable,
    'use_efficient_lamps': True,
    'use_photoelectric': True,
    'wattage': 20,
    'wattage_unit': iesve.wattage_unit.wm2}
    )
    
    room_data.set_room_conditions(
    {'cooling_profile': 'ON',
     'cooling_profile_from_template': False,
     'cooling_setpoint': 0.0,
     'cooling_setpoint_constant': False,
     'cooling_setpoint_from_template': False,
     'cooling_setpoint_profile': 'ON',
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
     'heating_setpoint_constant': False,
     'heating_setpoint_from_template': False,
     'heating_setpoint_profile': 'ON',
     'ncm_plant_profile': 'NCAW0005',
     'plant_profile': 'ON',
     'plant_profile_from_template': False,
     'plant_profile_type': 0,
     'sat_perc_lower': 0.0,
     'sat_perc_lower_from_template': False,
     'sat_perc_upper': 100.0,
     'sat_perc_upper_from_template': False,
     'solar_reflected_fraction': 0.05,
     'solar_reflected_fraction_from_template': False}
    )
    
    room_data.set_apache_systems(
   {'HVAC_methodology': iesve.hvac_methodology.apache_system,
    'HVAC_methodology_from_template': False,
    'HVAC_system': 'NOTS0000',
    'HVAC_system_from_template': False,
    'associated_return_air_plenum': '',
    'associated_supply_air_plenum': '',
    'auto_associate_adjacent_plenums': True,
    'aux_vent_system': 'NOTS0000',
    'aux_vent_system_from_template': False,
    'aux_vent_system_same': True,
    'conditioned': iesve.conditioned_flag.yes,
    'cooling_capacity_unit': -1,
    'cooling_capacity_unlimited': True,
    'cooling_capacity_unlimited_from_template': False,
    'cooling_capacity_value': 0.0,
    'cooling_design_sensible_load': 0.0,
    'cooling_design_supply_air_temperature': 12.0,
    'cooling_design_supply_air_temperature_from_template': False,
    'cooling_plant_radiant_fraction': 0.0,
    'cooling_plant_radiant_fraction_from_template': False,
    'cooling_unit_size': 0.0,
    'demand_controlled_ventilation_air_flow': iesve.air_flow_regulation_type.air_flow_speed_control,
    'demand_controlled_ventilation_type': iesve.demand_controlled_ventilation.gas_sensors,
    'dhw_system': 'NOTS0000',
    'dhw_system_from_template': False,
    'dhw_system_same': False,
    'has_mech_exhaust': False,
    'heat_recovery': iesve.heat_recovery.no_heat_recovery,
    'heating_capacity_unit': -1,
    'heating_capacity_unlimited': True,
    'heating_capacity_unlimited_from_template': False,
    'heating_capacity_value': 0.0,
    'heating_design_sensible_load': 0.0,
    'heating_design_supply_air_temperature': 32.0,
    'heating_design_supply_air_temperature_from_template': False,
    'heating_plant_radiant_fraction': 0.0,
    'heating_plant_radiant_fraction_from_template': False,
    'heating_unit_size': 0.0,
    'include_in_room_zone_loads_analysis': False,
    'include_in_room_zone_loads_analysis_template': False,
    'mech_sfp': 0.0,
    'mech_supply_in_room': True,
    'night_cooling_max_flow_rate': 1.0,
    'night_cooling_max_hrs_month': 200.0,
    'night_cooling_sfp': 2.5,
	'scope_of_extract_system': iesve.extract_system_scope.fan_within_zone,
    'seasonal_efficiency': 0.0,
    'supply_condition': iesve.condition_type.temperature_from_profile,
    'supply_condition_profile': '0',
    'supply_condition_template': False,
    'system_air_free_cooling': 0.0,
    'system_air_free_cooling_from_template': False,
    'use_default_seasonal_efficiency': False,
    'use_night_cooling': False}
    )

print("Room data set!")