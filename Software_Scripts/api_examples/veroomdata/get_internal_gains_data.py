""""
This sample gets room internal gains data
"""

import iesve    # the VE api
import pprint
   
project = iesve.VEProject.get_current_project()

for model in project.models:
    # get all the bodies in the building
    bodies = model.get_bodies(False)
    for body in bodies:
        # skip any bodies that aren't thermal rooms
        if body.type != iesve.VEBody_type.room:
            continue

        if model.model_type == iesve.VEModels.RealBuilding:
            # the Real building stores generic data
            # so ask for generic room data
            room_data = body.get_room_data(iesve.attribute_type.real_attributes)
        elif model.model_type == iesve.VEModels.NotionalBuilding:
            room_data = body.get_room_data(iesve.attribute_type.ncm_attributes)
        else:
            # Skip other models for this example
            continue
        
        pp = pprint.PrettyPrinter(indent=4)
        internal_gains = room_data.get_internal_gains()
        
        for gain in internal_gains:
            print(gain)
            pp.pprint(gain.get())