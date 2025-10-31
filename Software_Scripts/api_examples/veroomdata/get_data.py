""""
This sample gets room data
"""

import iesve    # the VE api
import pprint
   
project = iesve.VEProject.get_current_project()
real_building = project.models[0]

# get all the bodies in the building
bodies = real_building.get_bodies(False)
for body in bodies:
    # skip any bodies that aren't thermal rooms
    if body.type != iesve.VEBody_type.room:
        continue

    # the Real building stores generic data
    # so ask for generic room data
    room_data = body.get_room_data(iesve.attribute_type.real_attributes)
    
    # Print all the room data
    pp = pprint.PrettyPrinter(indent=4)
    
    print("General Data:\n")
    pp.pprint(room_data.get_general())
    
    print("\nSpace Conditions Data:\n")
    pp.pprint(room_data.get_room_conditions())
    
    print("\nSystem Data:\n")
    pp.pprint(room_data.get_apache_systems())
    
    print("\nInternal Gains Data:\n")
    pp.pprint(room_data.get_internal_gains())
    
    print("\nAir Exchange Data:\n")
    pp.pprint(room_data.get_air_exchanges())
    