""""
This sample gets NCM room data
"""

import iesve    # the VE api
import pprint
   
project = iesve.VEProject.get_current_project()
models = project.models

for model in models:
    print('\n', model.id)
    # get all the bodies in the building
    bodies = model.get_bodies(False)
    for body in bodies:
        # skip any bodies that aren't thermal rooms
        if body.type != iesve.VEBody_type.room:
            continue

        # the Real building stores generic data
        # so ask for generic room data
        print("\n", body.id)
        room_data = body.get_room_data(iesve.attribute_type.ncm_attributes)
        
        # Print all the room data
        pp = pprint.PrettyPrinter(indent=4)
        
        print("\nGeneral Data:\n")
        pp.pprint(room_data.get_general())
        
        print("\nSpace Conditions Data:\n")
        pp.pprint(room_data.get_room_conditions())
        
        print("\nSystem Data:\n")
        pp.pprint(room_data.get_apache_systems())
        
        print("\nInternal Gains Data:\n")
        pp.pprint(room_data.get_internal_gains())
        
        print("\nAir Exchange Data:\n")
        pp.pprint(room_data.get_air_exchanges())
        
        print("\nBuilding Regulations Data:\n")
        pp.pprint(room_data.get_building_regs())
        
        print("\nTranspired Solar Collectors:\n")
        pp.pprint(room_data.get_transpired_solar_collectors())
        
        print("\nNCM Lighting Data:")
        pp.pprint(room_data.get_ncm_lighting())