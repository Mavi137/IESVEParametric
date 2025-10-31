""""
This sample shows how to get a list of Construction Templates and
how to read data from them
"""

import iesve   # the VE api
import pprint  # standard Python library, makes output more readable

# create a pretty printer object
pp = pprint.PrettyPrinter()

# # MAIN BODY STARTS HERE # #
if __name__ == '__main__':
    # Get the current VE project.
    # Getting the construction templates is a project-level operation
    proj = iesve.VEProject.get_current_project()

    # Get a list of the known construction templates
    # Pass True to only get templates in use (assigned), False to get all templates
    templates = proj.construction_templates(False)

    # Prefix the output with project name
    print("Template details for project:" + proj.name)

    # the templates are returned as a dictionary
    # for this sample we don't need the key (the template handle)
    # so iterate over the dictionary values only
    for template in templates.values():
        pp.pprint(template.get())