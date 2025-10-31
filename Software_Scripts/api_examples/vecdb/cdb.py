""""
This sample shows basic CDB functionality
"""

import iesve
import pprint

pp = pprint.PrettyPrinter(indent=4, width=30)

# print the text strings corresponding to the three project types
print("Project type 0 = " + iesve.VECdbDatabase.get_project_type_string(iesve.project_types.project))
print("Project type 1 = " + iesve.VECdbDatabase.get_project_type_string(iesve.project_types.system))
print("Project type 2 = " + iesve.VECdbDatabase.get_project_type_string(iesve.project_types.manufacturer))

# get the database
db = iesve.VECdbDatabase.get_current_database()

# get all the projects in the database - list of tuples (type, list of projects)
# (Project types "Project" and "System" always have one project in the list, type "Manufacturer" can have many)
# (There will always be 3 entries)
projects = db.get_projects()

# for each tuple - (type, list of projects) - in projects
for type, project_list in projects.items():
    s_type = db.get_project_type_string(type)
    print("Found a project list of type " + s_type)
    # for each project in list of projects, show some general information
    for project in project_list:
        print("\tName= %s" % project.name)
        print("\tPath=%s" % project.path)
        print("\tTitle=%s" % project.title)
        print("\tHas constructions: ", project.has_constructions)
        print("\tHas materials: ", project.has_materials)
        # show number of constructions in the project
        print("\tNumber of constructions is %d" % project.number_of_constructions)
        if project.number_of_constructions > 0:
            # show number of constructions the wall category
            catStr = project.get_category_string(iesve.element_categories.wall)
            print("\tNumber of constructions in category '%s' is %d" % (catStr, project.get_number_of_constructions_in_category(iesve.element_categories.wall)))
            # show number of constructions in class "Opaque"
            # (classes are "Opaque", "Glazed", "Hard Landscaping", "Soft Landscaping", "Shade", and "Miscellaneous")
            c_class = iesve.construction_class.opaque
            s_class = project.get_class_string(c_class)
            ids = project.get_construction_ids(c_class)
            print("\tConstruction IDs in class '%s' (%d):" % (s_class, c_class))
            # show id and description of each construction in class "Opaque"
            for id in ids:
                construction = project.get_construction(id, c_class)
                print("\t\tsearch id is '%s', found construction with description '%s'" % (id, construction.reference))

# get the Project (type=0) tuple (this is what we are normally interested in, the project list associated with the VE model)
project_list = projects[0]
# this tuple will always have a project list of length 1, the only project associated with the VE model
project = project_list[0]
# we will search all classes (slower, but more certain to find the construction and without having to know what class it is in)
c_class = iesve.construction_class.none

# get first opaque construction
ids = project.get_construction_ids(iesve.construction_class.opaque)
id = ids[0] # to test for error handling below, set id to an id you know does not exist in the project
construction = project.get_construction(id, c_class)
# print its summary
print ("\r\nConstruction " + id + ":")
print (construction.get_review_summary_string())
# print its properties
properties = construction.get_properties()

print("\r\nProperties:\r\n")
pp.pprint(properties)

print("\r\nInside surface solar absorptivity: %f" % properties["inside_surface_solar_absorptivity"])

u = iesve.uvalue_types.cibse
construction.regulation = u
print("\r\nRegulation=%d, c Factor=%f, f Factor=%f, u Factor=%f" % (construction.regulation, construction.c_factor, construction.f_factor, construction.get_u_factor(u)))

u = iesve.uvalue_types.ashrae
construction.regulation = u
print("\r\nRegulation=%d, c Factor=%f, f Factor=%f, u Factor=%f" % (construction.regulation, construction.c_factor, construction.f_factor, construction.get_u_factor(u)))

# get its layers - a list
layers = construction.get_layers()
i = 0
# for each layer in list
for layer in layers:
    # print its summary
    print("\r\nlayer %d:\r\n%s" % (i, layer.get_review_summary_string(construction.opaque)))
    # get the associated material (returns None if cavity layer)
    material = layer.get_material(construction.opaque)
    # print its summary if not a cavity layer (no material associated)
    if material is not None:
        print("\r\nmaterial %d:\r\n%s" % (i, material.get_review_summary_string()))
    else:
        print("\r\nmaterial %d:\r\nNo material" % i)
    i = i + 1

# get first glazed construction
ids = project.get_construction_ids(iesve.construction_class.glazed)
id = ids[0] # to test for error handling below, set id to an id you know does not exist in the project
construction = project.get_construction(id, c_class)
# print its summary
print ("\r\nConstruction " + id + ":")
print (construction.get_review_summary_string())
# print its properties
properties = construction.get_properties()

print("\r\nProperties:\r\n")
pp.pprint(properties)

print("\r\nFrame material: %d" % properties["frame_material"])

u = iesve.uvalue_types.cibse
construction.regulation = u
print("\r\nRegulation=%d, c Factor=%f, f Factor=%f, u Factor=%f" % (construction.regulation, construction.c_factor, construction.f_factor, construction.get_u_factor(u)))

u = iesve.uvalue_types.ashrae
construction.regulation = u
print("\r\nRegulation=%d, c Factor=%f, f Factor=%f, u Factor=%f" % (construction.regulation, construction.c_factor, construction.f_factor, construction.get_u_factor(u)))

# get its layers - a list
layers = construction.get_layers()
i = 0
# for each layer in list
for layer in layers:
    # print its summary
    print("\r\nlayer %d:\r\n%s" % (i, layer.get_review_summary_string(construction.opaque)))
    # get the associated material (returns None if cavity layer)
    material = layer.get_material(construction.opaque)
    # print its summary if not a cavity layer (no material associated)
    if material is not None:
        print("\r\nmaterial %d:\r\n%s" % (i, material.get_review_summary_string()))
    else:
        print("\r\nmaterial %d:\r\nNo material" % i)
    i = i + 1
    
# now access constructions via model-->body
ve_project = iesve.VEProject.get_current_project()
models = ve_project.models
for model in models:
    bodies = model.get_bodies(False)
    print("\r\nAll bodies in the model and their assigned construction ids:", bodies)
    for body in bodies:
        print("----------------------------------------------")
        print("\r\nBody:", body)
        print("\r\n\tId:\t\t", body.id)
        print("\r\n\tIs selected:\t", body.selected)
        constructions = body.get_assigned_constructions()
        print("\r\n\tAssigned construction ids:\t", constructions)
        if len(constructions) > 0:
            id, desc = constructions[0]
            c_class = iesve.construction_class.none
            construction = project.get_construction(id, c_class)
            # print summary of first construction
            print ("\r\n\tFirst construction " + id + ":")
            print ("\r\n\t" + construction.get_review_summary_string())
