""""
This sample shows how to get information on the models stored in the
currently loaded VE project
"""

import iesve   # the VE api

# the list of models is accessed through the project API
project = iesve.VEProject.get_current_project()

# the list of currently available models is an attribute of the project.
# Typically a project will only have a single model defined, this is
# usually the real (proposed) building.
# When working with rating or compliance systems where baseline / reference etc
# models are created, these will follow the real model in the models list
models = project.models

# for best results, run this sample on a PRM or NCM Compliance project
# where you will typically find multiple models
for model in models:
    print("Model:                                       ", model)

    # the Model ID tells you what building variant this is
    # the following values are currently defined:
    #   "Real Building"
    #   "NB Variant":   UK NCM Compliance - notional building
    #   "RB Variant":   UK NCM Compliance - reference building
    #   "New Zealand Proposed Building"
    #   "New Zealand Reference Building"
    #   "GreenMark Proposed Building"
    #   "GreenMark Reference Building"
    #   "SunCast Solar Vis Variant"
    #   "BB Variant":  PRM baseline building (used for all 4 rotations)
    print("Model ID:                                    ", model.id)

    # get all the bodies in the model...  A VEBody represents a number of different
    # objects in the VE: 3D (rooms / shades), 2D (masterplanning surfaces) and
    # point objects (annotations).
    #
    # Bodies are referenced by a unique ID.  Note that the ID is unique only
    # within a model - the same room in proposed and baseline variant have the
    # same ID, which allows you to compare the rooms between variants
    # for more information on VE bodies and their type, see the VEBody sample
    bodies_by_ID = model.get_bodies_and_ids(False)
    print("All bodies in model along with their ID:     ", bodies_by_ID)

    # The previous API call returned a dictionary of ID + Body objects, using
    # the body ID as key in the dictionary.  This makes it easy to quickly get
    # a room by ID.
    # As an alternative, you can also get a simple list of bodies, the advantage
    # to the list is that the bodies will be in the same order as the VE object
    # browser (the tree control below the Navigator pane)
    sorted_bodies = model.get_bodies(False)
    print("All bodies in model in browser order:        ", sorted_bodies)

    # The VE model object gives access to various other mechanism, such as a
    # convenient function to get all the profiles referenced by the rooms
    # in that particular model (different model variants will typically be
    # configured with different profiles)
    profiles = model.get_assigned_profiles()
    print("Profiles referenced in model (by ID):        ", profiles)


    # Current ashrae standard
    print("model.get_current_ashrae_standard:           ", model.get_current_ashrae_standard())
