""""
This sample shows how to create simple profiles for the currently loaded VE project

For a more in-depth sample on using profiles and accessing the data
for profiles, see the plot_profiles script in the Tools folder
"""

import iesve   # the VE api

# Get the current VE project... 
# Profiles (ApPro) are stored on a per-project basis
project = iesve.VEProject.get_current_project()

print('Creating absolute daily profile...')
abs_day_profile = project.create_profile(type='daily', reference='My absolute IP profile', modulating=False, 
    units=iesve.ProfileUnits.imperial)

#set this profile to be 9am-5pm at 60 (IP Units), then from 5pm-10:30pm at 45, then 10:30pm-midnight back to 0
abs_profile_data = [ [0, 0, '-'], [9, 0, '-'], [9, 60, '-'], [17, 60, '-'], [17, 40.5, '-'], [22.5, 40.5, '-'], [22.5, 0, '-'], [24, 0.0, '-']]
abs_day_profile.set_data(abs_profile_data)

# Create 2 sample modulating daily profiles, then create a new weekly profile referencing these daily profiles
print('Creating 2 modulating daily profiles and assigning them to a new weekly profile...')
modulating_weekday_profile = project.create_profile(type='daily', reference='Sample modulating weekday profile', modulating=True)
modulating_weekday_profile_data = [ [0, 0, '-'], [9, 0, '-'], [9, 0.8, '-'], [17, 0.8, '-'], [17, 0.2, '-'], [22.5, 0.2, '-'], [22.5, 0, '-'], [24, 0.0, '-']]
modulating_weekday_profile.set_data(modulating_weekday_profile_data)

modulating_weekend_profile = project.create_profile(type='daily', reference='Sample modulating weekend profile', modulating=True)
modulating_weekend_profile_data = [ [0, 0, '-'], [12, 0, '-'], [12, 0.5, '-'], [16.5, 0.5, '-'], [16.5, 0.0, '-'], [24, 0.0, '-']]
modulating_weekend_profile.set_data(modulating_weekend_profile_data)

mod_weekly_prof = project.create_profile(type='weekly', reference='Sample weekly profile', modulating=True)

num_weekday_profiles = 5
num_non_weekday_profiles = 7

weekly_ids = ([modulating_weekday_profile.id ] * num_weekday_profiles) + ([modulating_weekend_profile.id ] * num_non_weekday_profiles)
mod_weekly_prof.set_data(weekly_ids)

# save the new profiles back to the profile database on disk
print('saving changes back to disk')
project.save_profiles()

# the profiles are now visible and ready for use in ApPro

