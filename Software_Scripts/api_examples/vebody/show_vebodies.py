""""
This sample displays basic data for all bodies in the VE project
"""

from typing import Any
import iesve   # the VE api
from pint import UnitRegistry   # python library for unit conversion

ureg = UnitRegistry()
Q_: Any = ureg.Quantity

# helper function for unit conversions
def convertAreasToIP(areas):
    for category, value in areas.items():
        areas[category] = round(Q_(value, ureg.centiare).to(ureg.sq_ft).magnitude, 1)

# # MAIN BODY STARTS HERE # #
if __name__ == '__main__':
    # get the current VE project
    project = iesve.VEProject.get_current_project()

    # from the project, get the list of current models.  A project will
    # always have at least 1 model (id: real building, and real building is
    # always at position 0 of the returned list)
    # if the project is a PRM or NCM or similar rating system where baseline
    # etc buildings are created, these variant buildings will appear in the
    # list after the real building.
    models = project.models
    for model in models:
        print("Model: ", model.id)

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
            print("----------------------------------------------")
            print("ID:", id)
            print("Body:", body)
            print("\tName / ID :\t {} / {}".format(body.name, body.id))
            print("\tIs selected:\t", body.selected)
            constructions = body.get_assigned_constructions()
            print("\tConstructions:\t", constructions)
            profiles = body.get_assigned_profiles()
            print("\tProfiles:\t", profiles)
            areas = body.get_areas()
            print("\tAreas (m2):\t", areas)
            convertAreasToIP(areas)
            print("\tAreas (ft2):\t", areas)
            print("\tProperties:\t", body.get_properties())
            print("\n")