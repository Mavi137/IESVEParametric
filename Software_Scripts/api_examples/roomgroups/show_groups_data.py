""""
This sample lists the room grouping schemes defined in the 
current project.

For each scheme, it will display all defined groups and which
rooms (by ID) that are assigned to each group
"""

import iesve   # the VE api

# instantiate the room groups interface object
rg = iesve.RoomGroups()

# Get and print the details of all room group schemes
print ("\nRoom Group Schemes:")
schemes = rg.get_grouping_schemes()
for scheme in schemes:
    scheme_handle = scheme['handle']
    print("  ----------------------------------------------")
    print("Scheme (name/handle): {} / {}".format(scheme['name'], scheme_handle))
    print("Groups:")
    # Get and print the room groups for this scheme
    groups = rg.get_room_groups(scheme_handle)
    for group in groups:
        print("   Group name / handle / colour:  {} / {} / {}".format(group['name'], group['handle'], group['colour']))
        print("   Rooms: ", group['rooms'])
