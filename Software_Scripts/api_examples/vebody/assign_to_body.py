""""
This sample assigns constructions to a body
"""

import iesve   # the VE api

# Get the current VE project.
veproject = iesve.VEProject.get_current_project()

# get the database
db = iesve.VECdbDatabase.get_current_database()

# get all the projects in the database - list of tuples (type, list of projects)
# (Project types "Project" and "System" always have one project in the list, type "Manufacturer" can have many)
# (There will always be 3 entries)
projects = db.get_projects()

# get the Project (type=0) tuple (this is what we are normally interested in, the project list associated with the VE model)
project_list = projects[0]
# this tuple will always have a project list of length 1, the only project associated with the VE model
project = project_list[0]

# Get all glazing construction IDs
g_class = iesve.construction_class.glazed
glazing_ids = project.get_construction_ids(g_class)

# Get all opaque construction IDs
o_class = iesve.construction_class.opaque
opaque_ids = project.get_construction_ids(o_class)

# from the project, get the list of current models.  A project will
# always have at least 1 model (id: real building, and real building is
# always at position 0 of the returned list)
# if the project is a PRM or NCM or similar rating system where baseline
# etc buildings are created, these variant buildings will appear in the
# list after the real building.
models = veproject.models
for model in models:
    # get a list of bodies in this model.  By passing False, we're asking
    # for all bodies, pass True to get only the selected bodies
    # In the VE, bodies can be of various types:
    #   3D bodies: rooms, local or topographical shades, adjacent buildings
    #   2D bodies: masterplanning surfaces, boundaries
    #   1D bodies: annotations
    # The VEBody object has a type attribute to discover the body type
    # Note that each body has a unique ID.  The ID is unique only within the
    # model that contains the room.  In a variant model, the same room will have
    # the same ID - this allows you to find the same room across models and compare them
    bodies = model.get_bodies_and_ids(False)
    for id, body in bodies.items():
        # we only want to process thermal rooms here, so filter by type
        if body.type != iesve.VEBody_type.room:
            continue

        # Get all surfaces in this room
        surfaces = body.get_surfaces()

        # Loop through all the surfaces
        for surface in surfaces:

            # Check if it is an external wall
            if surface.type == iesve.VESurface_type.ext_wall:

                # Loop through the opaque constructions
                for id in opaque_ids:
                    construction = project.get_construction(id, o_class)

                    # Check if this is a wall construction
                    if construction.category == iesve.element_categories.wall:

                        # Assign the opaque construction to the wall
                        body.assign_construction(construction, surface)

                        # Skip the rest of the opaque constructions
                        break

                # Get the openings for this surface
                openings = surface.get_openings()

                for opening in openings:
                    # Apply an opening type
                    body.assign_opening_type_by_id(surface.index, opening.get_macroflo_id(), opening.get_id())

                    # Look for any external glazing constructions
                    for glazing_id in glazing_ids:
                        construction = project.get_construction(glazing_id, g_class)
                        
                        if construction.category == iesve.element_categories.ext_glazing:
                            # Assign the construction to the opening
                            body.assign_construction_to_opening(construction, surface, opening.get_id())
                            break