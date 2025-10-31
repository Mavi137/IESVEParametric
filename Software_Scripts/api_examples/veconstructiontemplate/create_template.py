""""
This sample shows how to create and access the construction template list.
"""

import iesve

project = iesve.VEProject.get_current_project()

test_template = project.create_construction_template("test_template")
print(test_template.name) # Should be "test_template" if no other template of that name exists

test_template_2 = project.create_construction_template("test_template")
print(test_template_2.name) # will be "test_template (2)" as names are unique

test_template_3 = project.create_construction_template("test_template")
test_template_3.name = "test_template 3" # Rename the template
print(test_template_3.name) # will be "test_template 3"

all_templates = project.construction_templates(False)

for handle, template in all_templates.items():
    print(f"{handle}: {template.name}")