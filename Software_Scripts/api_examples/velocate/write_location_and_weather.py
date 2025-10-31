""""
This sample shows how to set information in ApLocate
"""

import iesve   # the VE api

# # MAIN BODY STARTS HERE # #
if __name__ == '__main__':
    # create the API object for ApLocate data
    loc = iesve.VELocate()

    # Open the weather file for writing
    loc.open_wea_data()

    # Set ApLocate data using a dictionary
    loc.set({ 'altitude': 24.0,
              'city': 'London/Heathrow',
              'cooling_loads_percentile': 0.4,
              'country': 'United Kingdom',
              'dst_correction': 1.0,
              'dst_from_month': iesve.month.april,
              'dst_to_month': iesve.month.october,
              'external_CO2': 400.0,
              'ground_reflectance_summer': 0.2,
              'ground_reflectance_summer_from_month': iesve.month.april,
              'ground_reflectance_summer_to_month': iesve.month.october,
              'ground_reflectance_winter': 0.2,
              'heating_loads_percentile': 99.6,
              'latitude': 51.48,
              'longitude': 0.45,
              'ref_air_density': 1.2,
              'time_zone': -0.0,
              'weather_file': "HeathrowEWY.fwt",
              'winter_drybulb': -4.65})
    
    # Set dry and wet bulb temperatures
    loc.set_max_dry_bulb(31.4, iesve.month.june)
    loc.set_max_wet_bulb(19.9, iesve.month.june)
    loc.set_min_dry_bulb(9.9, iesve.month.january)
    
    # Save and close
    loc.save_and_close()
