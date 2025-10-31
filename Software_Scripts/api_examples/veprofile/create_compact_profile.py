""""
This sample shows how to create a compact profile for the currently loaded VE project

For a more in-depth sample on using profiles and accessing the data
for profiles, see the plot_profiles script in the Tools folder
"""

import iesve   # the VE api

# Get the current VE project... 
# Profiles (ApPro) are stored on a per-project basis
project = iesve.VEProject.get_current_project()

print('Creating compact profile')
modulating_compact_profile = project.create_profile(type='compact', reference='Sample compact profile')

modulating_compact_profile_data = [[[31, 12],
["Weekday Open", [True, 9, 0, 12, 0], [True, 13, 0, 17, 0]],
["Weekday Closed", [True, 12, 0, 13, 0], [True, 17, 0, 0, 0]],
["Saturday Open", [True, 9, 0, 12, 0], [False, 0, 0]],
["Saturday Closed", [True, 0, 0, 8, 59], [True, 12, 1, 23, 59]],
["Sunday", [True, 0, 0, 23, 59], [False, 0, 0]],
["Holidays", [True, 0, 0, 23, 59], [False, 0, 0]]
]]

modulating_compact_profile.set_data(modulating_compact_profile_data)

# the profile is now visible and ready for use in ApPro

