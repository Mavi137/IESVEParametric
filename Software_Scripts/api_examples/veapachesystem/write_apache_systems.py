""""
This sample writes Apache Systems data
"""

import iesve    # the VE api

project = iesve.VEProject.get_current_project()
ap_systems = project.apache_systems()

# Change all existing systems
sys_count = 0
for ap_sys in ap_systems:
    ap_sys.set_name('VE Script System ' + str(sys_count))
    
    heating_data = { 'HR_effectiveness': 0.0,
                     'HR_return_temp': 21.0,
                     'SCoP': 0.800000011920929,
                     'fuel': iesve.fuel_type.nat_gas,
                     'gen_seasonal_eff': 0.8899999856948853,
                     'gen_size': 0.0,
                     'used_with_CHP': False}
    
    ap_sys.set_heating(heating_data)
    
    cooling_data = {'SEER': 2.5,
                    'SSEER': 2.0,
                    'cool_vent_mechanism': iesve.CoolingMechanism_type.air_conditioning,
                    'del_eff': 1.0800000429153442,
                    'fuel': iesve.fuel_type.nat_gas.elec,
                    'gen_size': 0.0,
                    'has_absorption_chiller': False,
                    'pump_and_fan_power_perc': 10.0}
    
    ap_sys.set_cooling(cooling_data)
    
    hot_water = {'cold_water_inlet_temp': 10.0,
                 'del_eff': 0.949999988079071,
                 'has_ApHVAC_boiler': False,
                 'has_secondary_circulation': False,
                 'is_storage_system': False,
                 'supply_temp': 60.0}
    
    ap_sys.set_hot_water(hot_water)
    
    solar_water_heating = {'HX_effectiveness': 0.4000000059604645,
                           'abso_absorptance': 0.949999988079071,
                           'abso_radius': 0.017500000074505806,
                           'azimuth': 90.0,
                           'coeff_c1': 0.4000000059604645,
                           'coeff_c2': 0.001500000013038516,
                           'cover_trans': 0.8199999928474426,
                           'fluid_flow': 50.0,
                           'has_space_or_process_heating': False,
                           'heat_capacity': 4100.0,
                           'intercept_factor': 0.9900000095367432,
                           'mirror_reflectance': 0.949999988079071,
                           'num_rows': 1,
                           'pump_fuel': 6,
                           'pump_power': 0.20000000298023224,
                           'refl_focal_length': 0.30000001192092896,
                           'refl_length': 3.0,
                           'refl_width': 1.0,
                           'tank_heat_loss': 0.007499999832361937,
                           'tank_volume': 1000.0,
                           'tube_extension': 0.20000000298023224,
                           'type': iesve.SolarHeating_type.parabolic,
                           'units_per_row': 3}
    
    ap_sys.set_solar_water_heating(solar_water_heating)
    
    aux_data = {'AEV': 8.286999702453613,
                'fan_fraction': 0.5,
                'method': iesve.AuxEnergyMethod_type.AEV,
                'off_schedule_AEV': 0.0}
    
    ap_sys.set_auxiliary_energy(aux_data)
    
    air_supply_data = { 'OA_max_flow': 0.0,
                        'condition': iesve.Conditioning_type.external_air,
                        'cooling_max_flow': 0.0,
                        'temperature_difference': 8.0}
    
    ap_sys.set_air_supply(air_supply_data)
    
    sys_count = sys_count + 1

# Set the default Apache System ID
iesve.VEApacheSystem.set_default('PY0')

print("Apache system data written!")