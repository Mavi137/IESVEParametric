""""
This sample shows how to determine which weather file was used
to generate a simulation results file (APS file)

It also shows how to load that weatherfile and read some sample
data from the weatherfile.
"""

from typing import Any
import iesve   # the VE api
from ies_file_picker import IesFilePicker   # file picker

# time-series results are returned by the API as numpy arrays
# so load the numpy package to process these further
import numpy as np

# The VE returns its data in metric units.  This sample uses
# the pint package to also display the results in IP units
from pint import UnitRegistry
ureg = UnitRegistry()
Q_: Any = ureg.Quantity

# Open APS file, using a file picker helper function
file_name = IesFilePicker.pick_aps_file()
aps_file = iesve.ResultsReader.open(file_name)
assert aps_file is not None, "Error opening results file"

# Query the APS file for the weather file used for simulation
weather_file_name = aps_file.weather_file

# Close the APS file, we're done with it now
aps_file.close()

# Open the weather file for further processing
wea_file = iesve.WeatherFileReader()
result = wea_file.open_weather_file(weather_file_name)
if result <= 0:
    print("The weather file hasn't opened correctly.")

print("Weather file: {0}".format(weather_file_name))

# Access and print general weather file data:
print ("Site:       {0}".format(wea_file.site))
print ("Lat:        {0:.2f}".format(wea_file.lat))
print ("Long:       {0:.2f}".format(wea_file.long))
print ("Time zone:  {0}".format(wea_file.time_zone))

print ("Year:       {0}".format(wea_file.year))

print ("Solar rad convention: {0}".format(wea_file.solar_rad_convention))
print ("Time convention:      {0}".format(wea_file.time_convention))
print ("Feb 29th:             {0}".format(wea_file.feb29))
print ("Start week day:       {0}".format(wea_file.start_weekday))

# Calculate the mean / min / max dry bulb temperature
# Note that the output is metric, as the API always returns metric data
varId = iesve.weather_variable.dry_bulb_temperature  # see note about variable numbers at end of this script
num_days = 365 if wea_file.feb29 == 0 else 366
data = wea_file.get_results(varId, 1, num_days)
averaged_data = np.average(data)
min_value = np.min(data)
max_temp = np.max(data)
print("dry bulb temperature \u00b0C (average / min / max): {0:.2f}, {1:.2f}, {2:.2f}".format(averaged_data, min_value, max_temp))

# also convert numbers to IP units and display
averaged_data_IP = Q_(averaged_data, ureg.degC).to(ureg.degF).magnitude
min_value_IP = Q_(min_value, ureg.degC).to(ureg.degF).magnitude
max_temp_IP = Q_(max_temp, ureg.degC).to(ureg.degF).magnitude
print("dry bulb temperature \u00b0F (average / min / max): {0:.2f}, {1:.2f}, {2:.2f}".format(averaged_data_IP, min_value_IP, max_temp_IP))

# Close the weather file:
wea_file.close()

# Note - the weather variable identifiers are as follows:
# 1  # Cloud cover (Units: Oktas)
# 2  # Wind direction  [E of N] (Units: Degrees)
# 3  # Dry bulb temperature (Units: Degrees C)
# 4  # Wet bulb temperature (Units: Degrees C)
# 5  # Direct normal radiation (Units: W/m2)
# 6  # Diffuse horizontal radiation (Units: W/m2)
# 7  # Solar altitude (Units: Degrees)
# 8  # Solar azimuth (Units: Degrees)
# 9  # Atmospheric pressure (Pa)
# 10 # Wind speed (m/s)
# 11 # Relative humidity (Units: %)
# 12 # Humidity ratio (moisture content) (Units: kg/kg)
# 13 # Global radiation (Units: W/m2)
# 14 # Dew point temperature (Units: Degrees C)
#
# Since VE 2019 FP2, an enum has been added to clarify weather variables.
# See the VEScripts documentation for more information.