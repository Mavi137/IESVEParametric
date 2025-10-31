""""
This sample shows how to create a casual gain for the currently loaded VE project
"""

# The VE api
import iesve

# Get the current VE project...
project = iesve.VEProject.get_current_project()

# Create new gain
gain = project.create_casual_gain(iesve.CasualGain_type.tungsten_lighting)
print(gain)

# Add the gain to a new template
template = project.create_thermal_template("test_template")
template.add_gain(gain)