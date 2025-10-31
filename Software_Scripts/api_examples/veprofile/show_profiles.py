""""
This sample shows how to get profile data for the currently loaded VE project

For a more in-depth sample on using profiles and accessing the data
for profiles, see the plot_profiles script in the Tools folder
"""

import iesve   # the VE api
import pprint  # standard Python library, makes output more readable

# Get the current VE project... 
# Profiles (ApPro) are stored on a per-project basis
project = iesve.VEProject.get_current_project()

# Group profiles - look at ON and OFF, which are default VE profiles
# Weekly, Yearly, Compact and Free-Form profiles are all considered group
# profiles.  
# A weekly group profile associates a daily profile with a weekday / holiday
# A yearly group profile allows assignment of different weekly profiles for the year
group_profiles = project.group_profiles(["ON", "OFF"])
print("Getting ON/OFF group profiles result: {} group profiles".format(len(group_profiles)))

# Daily profiles - look at ON and OFF, which all models should have.
# Daily profiles describe a 24-hour period.  They can be modulating or absolute.  
daily_profiles = project.daily_profiles(["ON", "OFF"])
print("Getting ON/OFF daily profiles result: {} daily profiles", len(daily_profiles))

# Getting a single group profile
group_profile = project.group_profile("OFF")

# Getting a single daily profile
daily_profile = project.daily_profile("OFF")

# Show some extra information about the daily profile:
pp = pprint.PrettyPrinter()
print("Daily profile's data for OFF:")
pp.pprint(daily_profile.get_data())

# Show how the weekly profile references the dailies
print("Weekly profile referencing daily profile IDs:")
pp.pprint(group_profile.get_data())

# A few sample data calls on a daily profile
print("OFF daily profile is modulating: ", daily_profile.is_modulating())
print("OFF daily profile is group:      ", daily_profile.is_group())
