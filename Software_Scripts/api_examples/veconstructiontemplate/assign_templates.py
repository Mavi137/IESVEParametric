""""
This sample resets the selected rooms in the real model back to the "Default"
construction template.

If no rooms are selected, it resets ALL rooms!

CAUTION: this script will modify your model!

"""

import iesve   # the VE api

# the list of models is accessed through the project API
project = iesve.VEProject.get_current_project()

# get the real building
real_building = project.models[0]

# build the list of room IDs to assign template to
room_id_list = []

# first we get only the selected rooms - if no rooms were selected
# (empty list returned), then we get all rooms
selected_rooms = real_building.get_bodies(True)
if len(selected_rooms) == 0:
    print("No rooms were selected - resetting all rooms back to default template")
    selected_rooms = real_building.get_bodies(False)

# now build a list of room IDs
for body in selected_rooms:
    if body.type == iesve.VEBody_type.room:
        room_id_list.append(body.id)

print("Assigning default template to {} room(s)".format(len(room_id_list)))

# find the default construction template
# we start with getting the full list of construction templates
templates = project.construction_templates(False)

# the templates are returned as a dictionary
# for this sample we don't need the key (the template handle)
# so iterate over the dictionary values only
# and we look for a template with the name "default" - this should
# always exist in every project!
templates_iter = templates.values()
for template in templates_iter:
    if template.name == "default":
        real_building.assign_construction_template_to_rooms(template, room_id_list)
        # no need to process further templates, so break out of the for loop
        break

# end of sample