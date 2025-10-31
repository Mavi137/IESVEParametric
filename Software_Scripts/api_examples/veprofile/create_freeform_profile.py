""""
This sample shows how to create a free-form profile for the currently loaded VE project

For a more in-depth sample on using profiles and accessing the data
for profiles, see the plot_profiles script in the Tools folder
"""

import iesve   # the VE api

# Get the current VE project... 
# Profiles (ApPro) are stored on a per-project basis
project = iesve.VEProject.get_current_project()

print('Creating free-form profile')
modulating_free_profile = project.create_profile(type='freeform', reference='Sample freeform profile')
modulating_free_profile_data = [[1, 1, 0, 0, 0], [3, 1, 0, 0, 1], [6, 1, 0, 0, 1], [9, 1, 0, 0, 1], [12, 31, 24, 0, 0]]
modulating_free_profile.set_data(modulating_free_profile_data)
modulating_free_profile.save_data()

# the profile is now visible and ready for use in ApPro

