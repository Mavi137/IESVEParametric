""""
This sample creates a new room grouping scheme with two
sample groups, and then assigns model rooms to the groups
"""

import iesve   # the VE api

# instantiate the room groups interface object
rg = iesve.RoomGroups()

# Create the 'Python Scheme' room group scheme
scheme_index = rg.create_grouping_scheme("Python Scheme")

# Create some sample room groups
# Note that a newly created scheme will already contain 1 group called "All Rooms"
# And All Rooms will hold all rooms in the model at this point
# After creating more groups, you can reassign the rooms to those groups

# Create 2 sample groups
# the first one with a lovely green colour
# the second is created with the default black colour
group_index_1 = rg.create_room_group(scheme_index, "Python Group 1",  (0, 117, 94))
group_index_2 = rg.create_room_group(scheme_index, "Python Group 2")

# Now we will evenly split the rooms across the 2 newly created groups
# Assigning rooms is done by ID (or VEBody object)

# First get a list of all rooms in the model
all_bodies = iesve.VEProject.get_current_project().models[0].get_bodies(False)

# we want to assign half to the first group, so count half the number of rooms
# then we use slicing to split the room object list
half_the_bodies = len(all_bodies) // 2

# Assign half of the rooms to Group 1
rg.assign_rooms_to_group(scheme_index, group_index_1, all_bodies[:half_the_bodies])

# Assign the rest of the rooms to Group 2, if there are any left
rg.assign_rooms_to_group(scheme_index, group_index_2, all_bodies[half_the_bodies:])

# Note - assigning a none-existent room ID will throw a script exception, eg:
# rg.assign_rooms_to_group(scheme_index, group_index_2, ['FAKEID'])
