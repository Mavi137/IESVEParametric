""""
This sample shows how to run Suncast simulations
"""

import iesve   # the VE api
import pprint
pp = pprint.PrettyPrinter(indent=4)

# get the current VE project
project = iesve.VEProject.get_current_project()

# Set some values for later
start_month = 1
end_month = 12
design_day = 15

# from the project, get the list of current models.  A project will
# always have at least 1 model (id: real building, and real building is
# always at position 0 of the returned list)
# if the project is a PRM or NCM or similar rating system where baseline
# etc buildings are created, these variant buildings will appear in the 
# list after the real building.  
models = project.models
for model in models:
    
    # Run a suncast simulation for this model
    suncast = model.suncast()
    suncast.run(start_month, end_month, design_day, True)
    print("Launched suncast simulation!")