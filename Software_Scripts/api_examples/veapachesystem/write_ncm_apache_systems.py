""""
This sample writes Apache Systems NCM data
"""

import iesve    # the VE api

project = iesve.VEProject.get_current_project()
ap_systems = project.apache_systems()

# Change all existing systems
sys_count = 0
for ap_sys in ap_systems:
    ap_sys.set_name('VE Script System ' + str(sys_count))
    
    # General NCM
    general_ncm_data = {'is_proxy_for_hvac': False,
                        'ncm_system_type': iesve.ncm_system_type.single_duct_vav}
    
    ap_sys.set_general_ncm(general_ncm_data)
    
    # Get an energy meter to set
    energy_source_data = iesve.EnergySources.get_all_energy_source_data()
    energy_source = energy_source_data[0] # Get the 1st energy source
    energy_meter = energy_source['meters'][0] # Get the 1st energy meter
    
    # NCM wizard data
    # Heating NCM
    heating_ncm_data = {
    'boiler_over_15_years_old': False,
    'convectors_have_fans': False,
    'fan_power_ratio': 20.0,
    'fan_power_ratio_known': True,
    'generator_radiant_efficiency': 0.4,
    'generator_radiant_efficiency_known': True,
    'generator_seasonal_efficiency': 0.81,
    'generator_seasonal_efficiency_known': True,
    'heat_source': iesve.ncm_heat_source.lthw_boiler,
    'installed_after_98': True,
    'meter': energy_meter,
    'qualify_for_ecas': iesve.ncm_ea_list.not_on_list,
    'uses_chp': False
    }
    
    ap_sys.set_heating_ncm(heating_ncm_data)
    
    # Cooling NCM
    cooling_ncm_data = {
    'chiller_meter': energy_meter,
    'generator_nominal_eer': 2.5,
    'generator_nominal_eer_known': True,
    'generator_seasonal_eer': 2.0,
    'generator_seasonal_eer_known': True,
    'mixed_mode': False,
    'power': iesve.ncm_chiller_power.less_than_100_kw,
    'qualify_for_eca': iesve.ncm_ea_list.not_on_list,
    'type': iesve.ncm_chiller_type.air_cooled
    }
    
    ap_sys.set_cooling_ncm(cooling_ncm_data)
    
    # System adjustment NCM
    system_adjustment_data = {
    'ahu_meets_standards': True,
    'cen_class': iesve.ncm_leakage_standard.not_compliant,
    'ductwork_leakage_test': iesve.ncm_leakage_test.not_tested,
    'ductwork_leakage_test_done': True,
    'pump_type': iesve.ncm_pump_type.constant_speed,
    'specific_fan_power': 3.0,
    'specific_fan_power_known': True
    }
    
    ap_sys.set_system_adjustment_ncm(system_adjustment_data)
    
    # Metering provision NCM
    ap_sys.set_metering_provision_ncm(provision_for_metering = False, warns = False)
    
    # Ventilation NCM
    ventilation_data = {
    'air_supply_mechanism': iesve.ncm_air_supply_mechanism.centralised_ac,
    'heat_recovery_efficiency': 1.0,
    'heat_recovery_efficiency_known': True,
    'heat_recovery_type': iesve.ncm_heat_recovery.no_heat_recovery,
    'variable_heat_recovery': False
    }
    
    ap_sys.set_ventilation_ncm(ventilation_data)
    
    # System controls NCM
    system_controls_data = {
    'central_time_control': True,
    'local_temperature_control': True,
    'local_time_control': True,
    'optimum_start_stop_control': True,
    'weather_compensation_control': True
    }
    
    ap_sys.set_system_controls_ncm(system_controls_data)
    
    # Bivalent systems NCM
    bivalent_systems = [
    {
    'heat_source': iesve.ncm_heat_source.unflued_radiant_heater,
    'meter': energy_meter,
    'gen_seff': 0.8,
    'load': 20.0,
    }]
    
    ap_sys.set_bivalent_systems_ncm(bivalent_systems)
    
    # Apply the NCM wizard data to the system
    ap_sys.apply_ncm()
    
    # Non NCM Wizard data
    # NCM-only Heating data
    heating_data = { 'is_heat_pump': False,
                     'meter_cef': 0.2,
                     'meter_pef': 1.2,
                     'SCoP': 0.8}
    
    ap_sys.set_heating(heating_data)
    
    # Hot water NCM data
    hot_water_data = {
    'generator_type': iesve.dhw_parent_type.dedicated_dhw_boiler,
    'later_than_1998': True,
    'generator_meter': energy_meter,
    'use_default_generator_seasonal_efficiency': False,
    'generator_seasonal_efficiency': 0.8
    }
    
    ap_sys.set_hot_water(hot_water_data)
    
    # Solar water heating NCM data
    solar_heating_data = {
    'a1': 20.0,
    'a2': 0.0,
    'circulation_system': iesve.shw_circulation_sys.forced_circulation_system_with_no_pv,
    'heat_transfer_rate': 130.0,
    'iam': 1.0,
    'insulation_thickness': 25.0,
    'insulation_type': iesve.shw_insulation_type.loose_jacket,
    'is_heat_exchanger': True,
    'is_solar_heating': True,
    'nominal_pump_power': 500.0,
    'overall_heat_loss_coeff': 0.0,
    'panel_area': 0.0,
    'panel_azimuth': 180.0,
    'panel_tilt': 35.0,
    'performance_parameter': iesve.shw_collector_type.flat_panel,
    'performance_parameters_known': True,
    'pipes_insulated': False,
    'preheating_type': iesve.shw_preheating_type.separate_solar_cylinder,
    'sigma_0': 0.6,
    'volume': 800.0
    }
    
    ap_sys.set_solar_water_heating_ncm(solar_heating_data)
    
    # NCM-only Cooling data
    cooling_data = { 'nominal_eer': 2.5,
                     'free_cooling': iesve.cmm_free_cooling.not_a_cmm_system
                   }
    
    ap_sys.set_cooling(cooling_data)
    
    # NCM-only Auxiliary energy data
    ap_sys.set_auxiliary_energy(air_supply_mechanism = iesve.ncm_air_supply_mechanism.centralised_ac)
    
    sys_count = sys_count + 1

print("Apache system data written!")