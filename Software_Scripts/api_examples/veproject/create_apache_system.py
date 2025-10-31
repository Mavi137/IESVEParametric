""""
This sample shows how to create an apache system for the currently loaded VE project

For a more in-depth sample on using apache systems and accessing the data
for them, see the veapachesystem examples
"""

# the VE api
import iesve

# Get the current VE project... 
project = iesve.VEProject.get_current_project()

#create new apache system
new_system = project.create_apache_system(system_name = "example_system")
print(new_system.name) # prints system name
print(new_system.id) # prints system id