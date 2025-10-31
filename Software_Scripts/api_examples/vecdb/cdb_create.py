""""
This sample:
    - creates a CDB construction
    - creates several CDB materials
    - accesses information on the CDB materials
    - deletes one of the created materials
"""

import iesve
import pprint

pp = pprint.PrettyPrinter()

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

# Create a new external glazing construction
construction = project.create_construction(iesve.element_categories.ext_glazing)
pp.pprint(construction.get_properties())


# Get an existing material
membrane = project.get_material("STD_MEM")
print(membrane.get_review_summary_string())


# Create several new materials
# Created glazed materials' IDs start with "PYGL", all others start with "PYOP"
materials = []

num_mats = project.get_number_of_materials_in_category(iesve.material_categories.glass)
mat_ids = project.get_material_ids(iesve.material_categories.glass)
print(
    "Before creating materials, there are {} glass materials. They are: {}".format(
        num_mats, ", ".join(mat_ids)
    )
)

materials.append(project.create_material(iesve.material_categories.glass))
materials.append(project.create_material(iesve.material_categories.plaster))
materials.append(project.create_material(iesve.material_categories.timber))

num_mats = project.get_number_of_materials_in_category(iesve.material_categories.glass)
mat_ids = project.get_material_ids(iesve.material_categories.glass)
print(
    "After creating materials, there are {} glass materials. They are: {}".format(
        num_mats, ", ".join(mat_ids)
    )
)

for mat in materials:
    mat_id = mat.get_properties()["id"]
    print("Created material with ID [{}]".format(mat_id))
    print("Deleting material...")
    try:
        project.delete_material(mat_id)
    except ValueError:
        print("Material not found.")
    except RuntimeError as e:
        # this error gets thrown when the material is referenced by at
        # least one construction
        raise e

