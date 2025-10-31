""""
This sample shows how to get data for the currently loaded VE project
"""

import iesve   # the VE api

# get an object that represents the current object
# Note! When you switch projects (load a new project etc) in the VE
# this object becomes invalid.  Do not store this object for re-use
# across scripts etc - ensure you always get the current project!
project = iesve.VEProject.get_current_project()
display_units = "Metric" if project.get_display_units() == iesve.DisplayUnits.metric else "IP"

print("Name:\t\t\t\t", project.name)
print("Path:\t\t\t\t", project.path)
print("Units displayed in:\t\t {} mode".format(display_units))
print("VE version:\t\t\t", project.get_version())
print("Nr of Models in project:\t", len(project.models))


