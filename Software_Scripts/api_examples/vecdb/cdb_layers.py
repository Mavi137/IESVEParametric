""""
This sample demonstrates adding, inserting and deleting CDB layers
"""

import iesve
import pprint
pp = pprint.PrettyPrinter()

# Get the current VE project.  
veproject = iesve.VEProject.get_current_project()

# Get the database
db = iesve.VECdbDatabase.get_current_database()

# Get all the projects in the database - list of tuples (type, list of projects)
# (Project types "Project" and "System" always have one project in the list, type "Manufacturer" can have many)
# (There will always be 3 entries)
projects = db.get_projects()

# Get the Project (type=0) tuple (this is what we are normally interested in, the project list associated with the VE model)
project_list = projects[0]
# This tuple will always have a project list of length 1, the only project associated with the VE model
project = project_list[0]

# We will search opaque constructions
c_class = iesve.construction_class.opaque
ids = project.get_construction_ids(c_class)

# Add layers
for id in ids:
    construction = project.get_construction(id, c_class)
    
    if construction.is_editable:
        layers = construction.get_layers()
        
        if len(layers) > 0:
            material = layers[0].get_material(True)
            
            if material is not None:
                material_id = material.get_properties()["id"];
                print("Material:", material_id)
                construction.insert_layer(layers[0].get_id(), False)
                construction.delete_layer(layers[0].get_id())
                construction.add_layer(material_id, True) # Cavity
                construction.add_layer(material_id, False)
                
                for layer in layers:
                    print("Layer:", layer.get_id())