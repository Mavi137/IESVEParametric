""""
This sample demonstrates geometry functionality
"""

import iesve    # the VE api

# First, centre the model to the origin
geom = iesve.VEGeometry
geom.centre_to_origin()
print("Model centred to origin")

# Now change the window-to-wall ratio
print("Old window-to-wall ratio: ", geom.get_wwr())
geom.reduce_ext_windows(2)
print("Window-to-wall ratio reduced to 2")
print("New window-to-wall ratio: ", geom.get_wwr())
print("-------------------------")

# Display the building orientation
print("Building orientation (degrees):", geom.get_building_orientation())

# Get the current VE project.
project = iesve.VEProject.get_current_project()

# get the list of models.  The first model is always the 'real' model
# subsequent models in the list (if present) are variants
# such as PRM baseline model, NCM variants, etc
models = project.models
for model in models:
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
        body.select()
        if (body.selected):
            geom.set_body_opening_type("window")
            print("Openings changed to windows")
            geom.remove_openings_below_area_threshold(2.5)
            print("Openings less than 2.5 square metres removed")
            geom.remove_doors(iesve.opening_internality.internal, 0)
            print("All doors removed")
            geom.remove_holes(iesve.opening_internality.internal, 0)
            print("All holes removed")
            geom.set_percent_glazing(25)
            print("Percent external surface glazing set to 25")
            geom.set_percent_wall_glazing(10)
            print("Percent wall glazing set to 10")
            geom.set_percent_doors(10)
            print("Percent doors set to 10")
            geom.set_percent_holes(10)
            print("Percent holes set to 10")
            geom.set_colour(1) # green
            print("Body colour set to green")
        print("-------------------------")

        # Get all surfaces in this room
        surfaces = body.get_surfaces()
        for surface in surfaces:
            openings = surface.get_openings()
            # Get the openings
            for opening in openings:
                print("Macroflo Opening ID: ", opening.get_macroflo_id())
                opening_properties = opening.get_properties()
                print("Aspect Ratio:", opening_properties["aspect_ratio"])
                print("Perimeter:", opening_properties["perimeter"]) # In metres
                print("APS Handle:", opening_properties["aps_handle"])
                print("Macroflo Type:", opening_properties["macroflo_type"])
                print("Index:", opening_properties["index"])
                print("Area:", opening_properties["area"]) # In metres
                print("Width:", opening_properties["width"]) # In metres
                print("Height:", opening_properties["height"]) # In metres
                print("Sill Height:", opening_properties['sill_height'])

                print("-------------------------")

        body.deselect()
        if body.selected == False:
            print("Body has been deselected")