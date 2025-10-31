# Sample showing a data plot from a weather file variable
# Also shows how to load a weather file from filename

import os
import iesve
from matplotlib.projections import PolarAxes
import numpy as np
import matplotlib.pyplot as plt

from ies_file_picker import IesFilePicker

# prompt the user for an APS file using a file browser dialog
try:
    file_name = IesFilePicker.pick_aps_file()
except:
    # the file browser throws an assert if the user cancels
    # so for (any) exception in the file browser, just stop the script
    quit()

# Open APS file:
aps_file = iesve.ResultsReader.open(file_name)
assert aps_file is not None, "Error opening simulation results file"

# Get the weather file name from the APS file:
weather_file_name = aps_file.weather_file

# close the aps file, as all further data gathering is from the weather file
aps_file.close()

# Open the weather file:
wea_file = iesve.WeatherFileReader()
result = wea_file.open_weather_file(weather_file_name)
assert result > 0, "Error opening weather file."

# Retrieve the wind direction variable
wind_direction_variable = 2  # see API documentation in the help guide
wind_speed_variable = 10     # see API documentation in the help guide
num_days = 365 if wea_file.feb29 == 0 else 366
wind_direction = wea_file.get_results(wind_direction_variable, 1, num_days)
wind_speed = wea_file.get_results(wind_speed_variable, 1, num_days)

# ensure that we read the data correctly
assert (wind_direction is not None) and (wind_speed is not None), "Error reading data"
assert len(wind_direction) == len(wind_speed), "Unexpected data mismatch"
assert len(wind_direction) != 0, "No data"

# clear any old plotting data, also in case a previous plot was cancelled / interrupted
plt.clf()
plt.close('all')

# create new windrose plot
ax = plt.subplot(111, projection="polar")

assert isinstance(ax, PolarAxes), "Axes are not Polar"
ax.set_theta_direction(-1)
ax.set_theta_zero_location('N')

N = 12 # no. direction tiers
directionTierWidth=360/N # as of VE sim
windTierWidth=3 # as of VE sim

# BUCKETS
bins, windSpeedTiers, windDirectionTiers = [],[],[]
maxSpeedTier = np.amax(wind_speed) + windTierWidth
for sTier in range (0, maxSpeedTier.astype(np.int64), windTierWidth):
   windSpeedTiers.append(sTier)
   bins.append([])

for dTier in range(0, N+1):
    windDirectionTiers.append( dTier*directionTierWidth )

# ------------ bucketing of data by speed tiers (3 m/s increments) ----------------
# Bucketing of windSpeed values (tier size: 3 m/s), with buckets containing related wind direction of speed-direction pair (stored separately in wind_speed and wind_direction)
for entryNo in range(0, len( wind_speed ) ):
     bin = np.floor( wind_speed[entryNo] / windTierWidth )
     bins[bin.astype(np.int64)].append( wind_direction[entryNo] )

# ------------ per-bin bucketing by direction tiers ----------------
binsAccumulated=0
for binNo in range(0,len(bins)):
    bin=np.histogram(bins[binNo], bins=windDirectionTiers)[0]
    ax.bar(np.radians(windDirectionTiers[:-1]), bin, np.radians(directionTierWidth), color=(plt.get_cmap('jet')( int( 125+ (150/len(bins))*binNo) ) ), bottom=binsAccumulated)
    binsAccumulated+=bin

weather_file_basename = os.path.basename(weather_file_name)
plt.suptitle('Windrose [' + weather_file_basename + ']', fontsize=12)

# save to content manager
# now get the project data
proj = iesve.VEProject.get_current_project()
target_folder = proj.content_folder + '\\Windrose\\'
if not os.path.exists(target_folder):
    os.makedirs(target_folder)

# save plot to disk inside the content folder
aps_cm_filename = os.path.splitext(os.path.basename(file_name))[0]
weather_file_cm_filename = os.path.splitext(weather_file_basename)[0]
cm_filename = aps_cm_filename + "-" + weather_file_cm_filename + ".png"
content_manager_fullpath = target_folder + cm_filename
plt.savefig(content_manager_fullpath)

# register the image with content manager
proj.register_content(content_manager_fullpath, 'Windrose', cm_filename, True)

# also show plot on screen
plt.show()

# Close the weather file:
wea_file.close()