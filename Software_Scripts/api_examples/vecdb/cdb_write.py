""""
This sample writes CDB Data

CAUTION: this script will modify your constructions!
"""

import iesve

# Get the current VE project.  
veproject = iesve.VEProject.get_current_project()

# get the database
db = iesve.VECdbDatabase.get_current_database()

# get all the projects in the database - list of tuples (type, list of projects)
# (Project types "Project" and "System" always have one project in the list, type "Manufacturer" can have many)
# (There will always be 3 entries)
projects = db.get_projects()

# get the Project (type=0) tuple (this is what we are normally interested in, the project list associated with the VE model)
project_list = projects[0]
# this tuple will always have a project list of length 1, the only project associated with the VE model
project = project_list[0]

# we will search glazing constructions
c_class = iesve.construction_class.glazed
ids = project.get_construction_ids(c_class)

for id in ids:
    construction = project.get_construction(id, c_class)
    
    if construction.is_editable:
        construction.set_properties({'outside_surface_emissivity': 1.0, 'inside_surface_emissivity': 1.0, 'outside_surface_resistance': 0.1, 'inside_surface_resistance': 0.1})
        construction.reference = "Python Sample Construction"
        layers = construction.get_layers()
        for layer in layers:
            layer.set_properties({'thickness': 1.0, 'resistance': 1.0, 'convection_coefficient': 1.0})
            material = layer.get_material(False)
            
            # Exclude cavity layers
            if material is not None:
                material.set_properties({'specific_heat_capacity': 2.0, 'inside_reflectance': 0.414, 'transmittance': 0.4, 'visible_transmittance': 0.78, 'outside_reflectance': 0.289, 'inside_visible_reflectance': 0.07, 'thickness': 0.006, 'refractive_index': 1.5, 'outside_visible_reflectance': 0.07, 'description': 'Python Sample Material'})