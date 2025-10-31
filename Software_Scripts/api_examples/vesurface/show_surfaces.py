""""
This sample shows how to get data at the surface
level of a room
"""

from typing import Any
import iesve   # the VE api

# The VE returns its data in metric units.  This sample uses
# the pint package to also display the results in IP units
from pint import UnitRegistry
ureg = UnitRegistry()
Q_: Any = ureg.Quantity

# this little utility function searches for the data fields that
# are either areas (m2) or distances (meters) and converts them
# to ft2 and inches respectively
def convertAreas(data):
    # only convert if display is not metric
    if ve_display_units == iesve.DisplayUnits.metric:
        return

    keywords_area = ['gross', 'net', 'window', 'door', 'hole', 'gross_openings', 'area']
    keywords_distance = ['thickness', 'distance']

    for kwa in keywords_area:
        val = data.get(kwa)
        if val is not None:
            data[kwa] = Q_(val, ureg.centiare).to(ureg.sq_ft).magnitude

    for kwd in keywords_distance:
        val = data.get(kwd)
        if val is not None:
            data[kwd] = Q_(val, ureg.meter).to(ureg.inches).magnitude

# Get the current VE project.
project = iesve.VEProject.get_current_project()

# check what units mode the VE is in
# the API returns all data in Metric units - if you want IP output
# we will show some sample conversions
ve_display_units = project.get_display_units()

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

        # Get all surfaces in this room
        surfaces = body.get_surfaces()
        for surface in surfaces:
            print("----------------------------------------------")

            # Index of this surface within body (this should also follow the order
            # in the object browser tree!)
            print("\tSurface Index", surface.index)

            # Get and display surface areas
            areas = surface.get_areas()
            convertAreas(areas)
            print("\n\tSurface areas -")
            print("\t\t\tTotal Gross:", areas["total_gross"])
            print("\t\t\tTotal Net:", areas["total_net"])
            print("\t\t\tTotal Window:", areas["total_window"])
            print("\t\t\tTotal Door:", areas["total_door"])
            print("\t\t\tTotal Hole:", areas["total_hole"])
            print("\t\t\tTotal Gross Openings:", areas["total_gross_openings"])
            print("\t\t\tInternal Gross:", areas["internal_gross"])
            print("\t\t\tInternal Net:", areas["internal_net"])
            print("\t\t\tInternal Window:", areas["internal_window"])
            print("\t\t\tInternal Door:", areas["internal_door"])
            print("\t\t\tInternal Hole:", areas["internal_hole"])
            print("\t\t\tInternal Gross Openings:", areas["internal_gross_openings"])
            print("\t\t\tExternal Gross:", areas["external_gross"])
            print("\t\t\tExternal Net:", areas["external_net"])
            print("\t\t\tExternal Window:", areas["external_window"])
            print("\t\t\tExternal Door:", areas["external_door"])
            print("\t\t\tExternal Hole:", areas["external_hole"])
            print("\t\t\tExternal Gross Openings:", areas["external_gross_openings"])

            # Get details of openings in surface
            # An opening can be any of:
            #   - window
            #   - door
            #   - hole
            openings = surface.get_opening_totals()
            print("\n\tOpenings numbers -")
            print("\t\t\tDoors (total) =", openings["doors"])
            print("\t\t\tHoles (total) =", openings["holes"])
            print("\t\t\tWindows (total) =", openings["windows"])
            print("\t\t\tExternal Doors =", openings["external_doors"])
            print("\t\t\tExternal Holes =", openings["external_holes"])
            print("\t\t\tExternal Windows =", openings["external_windows"])
            print("\t\t\tTotal Openings =", openings["openings"])

            # Get surface properties
            properties = surface.get_properties()
            convertAreas(properties)
            print("\n\tProperties -")
            print("\t\t\ttype =", properties["type"])
            print("\t\t\tarea =", properties["area"])
            print("\t\t\tthickness =", properties["thickness"])
            print("\t\t\torientation =", properties["orientation"])
            print("\t\t\ttilt =", properties["tilt"])

            # Get adjacencies to surface (an adjacency is the section of wall
            # that has a room on both sides - ie it is internal rather than external)
            adjacencies = surface.get_adjacencies()
            print("\n\tAdjacencies -")
            for adjacency in adjacencies:

                # Get adjacency properties
                properties = adjacency.get_properties()
                convertAreas(properties)
                print("\t\t\tsurface index =", properties["surface_index"]) # index of surface in adjacent room
                print("\t\t\tbody id =", properties["body_id"])    # ID of room on other side of adjacency
                print("\t\t\tgross area =", properties["gross"])   # total adjacency area (including all openings)
                print("\t\t\tglazed area =", properties["window"]) # total area of windows in adjacency
                print("\t\t\thole area =", properties["hole"])     # total area of holes in adjacency
                print("\t\t\tdoor area =", properties["door"])     # total area of doors in adjacency
                print("\t\t\tDistance =", properties["distance"])  # distance between bodies

            # Get constructions used in this surface
            constructions = surface.get_constructions()
            print("\n\tConstructions -")
            for construction in constructions:
                print("\t\t\tconstruction id =", construction)
