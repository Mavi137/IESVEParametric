""""
This sample shows how to get Suncast data
"""

import iesve   # the VE api
import pprint
pp = pprint.PrettyPrinter(indent=4)

# get the current VE project
project = iesve.VEProject.get_current_project()

# Set some values for later
start_month = 1
end_month = 12
design_day = 15

# from the project, get the list of current models.  A project will
# always have at least 1 model (id: real building, and real building is
# always at position 0 of the returned list)
# if the project is a PRM or NCM or similar rating system where baseline
# etc buildings are created, these variant buildings will appear in the 
# list after the real building.  
models = project.models
for model in models:
    
    # Get a suncast object
    suncast = model.suncast()
    
    # get the list of bodies in a models.  A VE body can be either
    # - a 3D body of type room, topographical shade, local shade, or adjacent building
    # - a 2D body (masterplanning)
    # - a 1D body (annotations)
    bodies = model.get_bodies_and_ids(False)
    for id, body in bodies.items():
        # we only want to process thermal rooms here, so filter by type
        if body.type != iesve.VEBody_type.room:
            continue
        
        print("Body:", id)

        # Get all surfaces in this room
        surfaces = body.get_surfaces()
        for surface in surfaces:
            print("----------------------------------------------")

            # Index of this surface within body (this should also follow the order
            # in the object browser tree!)
            print("Surface Index", surface.index)
            
            surface_props = surface.get_properties()
            filename = project.path + "Suncast\\" + project.name + ".shd" # Enter your shading filename here if it is named differently
            
            print("\nInsolation Data for July at 12:00")
            
            # Print July Insolation Data at 12:00      
            print('\nSurface:')
            results = suncast.get_results(filename, body.get_index(), surface.index, surface_props['id'])
            pp.pprint(results[6][11])
            
            # Print opening results, if they exist
            openings = surface.get_openings()
            opening_num = 1
            for opening in openings:
                results = suncast.get_results(filename, body.get_index(), surface.index, surface_props['id'], opening_num)
                print('\nOpening', str(opening_num) + ':')
                pp.pprint(results[6][11])
                opening_num = opening_num + 1
            
            print("\nSun Up/Down Data:")
            
            sun_up_down = suncast.get_sun_up_down()
            print(sun_up_down)
            
            solar_altitudes = suncast.get_solar_altitudes(filename, design_day)
            print("\nSolar Altitude for July at 12:00:")

            # Print July Altitude at 12:00
            pp.pprint(solar_altitudes[6][11])