""""
This sample shows how to create and access the thermal template list.
"""

import iesve

project = iesve.VEProject.get_current_project()

test_template = project.create_thermal_template("test_template")
print(test_template.name) # Should be "test_template" if no other template of that name exists

test_template_2 = project.create_thermal_template("test_template")
print(test_template_2.name) # will be "test_template (2)" as names are unique

all_templates = project.thermal_templates(False)

for handle, template in all_templates.items():
    print(f"{handle}: {template.name}")