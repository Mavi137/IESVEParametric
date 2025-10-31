""""
This sample writes Renewables data
"""

import iesve    # the VE api

# # MAIN BODY STARTS HERE # #
if __name__ == '__main__':   
    renewables = iesve.VERenewables()
    
    # Write PV type data
    pv_types = renewables.get_pv_types()   
    for pv_type in pv_types:
        renewables.set_pv_type_data({'degradation_factor': 0.99,
                                     'description': 'Python PV type',
                                     'electrical_conversion_efficiency': 0.85,
                                     'module_nominal_efficiency': 0.07,
                                     'noct': 46.0,
                                     'ref_irradiance': iesve.reference_irradiance.irad_800wm2,
                                     'technology': iesve.pvs_type.other_thin_film,
                                     'temp_coefficient': 0.0024}, pv_type["id"])

    # Write PV Data
    pvs = renewables.get_pv_data()
    for pv in pvs:
        if pv["class"] == "Parametric panel":
            renewables.set_pv_data({'description': "Python parametric panel",
                                    'area': 5.0,
                                    'azimuth': 180.0,
                                    'inclination': 90.0,
                                    'shading_factor': 1.0,
                                    'type_id': pv_types[0]["id"]}, pv["id"])
                                    
        elif pv["class"] == "Free-standing panel":
            renewables.set_pv_data({'description': "Python free-standing panel",
                                    'area': 5.0,
                                    'azimuth': 180.0,
                                    'inclination': 90.0,
                                    'type_id': pv_types[0]["id"]}, pv["id"])
            
        elif pv["class"] == "High concentration panel":
            renewables.set_pv_data({'description': "Python high concentration panel",
                                    'cell_surface': 1.0,
                                    'num_cells': 100,
                                    'geometric_concentration': 500.0,
                                    'power_temperature_coefficient': -0.0015,
                                    'optical_efficiency': 0.98,
                                    'cell_efficiency': 0.40,
                                    'spectral_factor': 0.85,
                                    'tracking_device_power_losses': 0.5,
                                    'linear_temperature_factor': 0.002,
                                    'tracking_error': 0.01,
                                    'type_id': pv_types[0]["id"]}, pv["id"])
    
    # Write wind data
    renewables.set_wind_data({'hub_height': 10.0,
                              'is_enabled': False,
                              'rated_power': 200.0})

    # Write CHP data
    renewables.set_chp_data({'min_fraction_rated_heat_output': 0.5,
                             'rated_heat_output': 1000.0,
                             'is_enabled': False,
                             'min_power_efficiency': 0.2,
                             'min_thermal_efficiency': 0.57,
                             'rated_power_efficiency': 0.28,
                             'profile': 'ON',
                             'quality_index': 0.0,
                             'rated_thermal_efficiency': 0.5})