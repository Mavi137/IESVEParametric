""""
This sample sets construction template data
"""

import iesve   # the VE api

# Get the current VE project.
# Getting the construction templates is a project-level operation
proj = iesve.VEProject.get_current_project()

# Get a list of the known construction templates
# Pass True to only get templates in use (assigned), False to get all templates
templates = proj.construction_templates(False)

# the templates are returned as a dictionary
# for this sample we don't need the key (the template handle)
# so iterate over the dictionary values only
templates_iter = templates.values()
for template in templates_iter:
    settings = {
    "roof": "STD_ROOF",
    "internal_ceiling_floor": "STD_CEIL",
    "external_wall": "STD_WAL1",
    "internal_partition": "STD_PART",
    "ground_exposed_floor": "STD_FLO1",
    "roof_light": "STD_RFLT",
    "external_window": "STD_EXTW",
    "internal_window": "STD_INTW",
    "door": "STD_DOOR",
    "road": "ROAD",
    "parking": "PARKING",
    "hard_landscape": "CONPAT",
    "pavement_sidewalk": "PAVING",
    "pervious_hard_landscape": "PCONPAT",
    "turf": "LAWN",
    "mixed_vegetation": "VEG",
    "tree": "TEG",
    "vegetated_shade": "VEG",
    "shrubs": "SHRUBS",
    "ground_cover": "GRNDCVR",
    "wetlands": "WTLNDS",
    "water": "WTR",
    "local_shade": "LSHADE",
    "topographical_shade": "TSHADE"
    }

    template.set(settings)

print("Templates set!")