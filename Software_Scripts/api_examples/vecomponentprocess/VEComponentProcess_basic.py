# This sample script shows how to use the VEComponentProcess class to
# get process object data.

import pprint
import inspect

import iesve

# Iterate through the bodies in the model and print out any component processes
# that we find
print("----- Usage of class -----")
pp = pprint.PrettyPrinter(indent=4)
project = iesve.VEProject.get_current_project()
models = project.models
for model in models:
    bodies = model.get_bodies(False)
    for body in bodies:
        print("----------------------------------------------")
        print("Body: ({})".format(body.id))
        procs = body.get_processes()
        if not procs:
            print("Body has no processes")
            continue
        for proc in procs:
            print("Process name:", proc.get_name())
            print("Product:", proc.get_product())
            print('Material inputs :')
            pp.pprint(proc.get_material_inputs())
            print('Material outputs:')
            pp.pprint(proc.get_material_outputs())
            print('Energy inputs:')
            pp.pprint(proc.get_energy_inputs())
            print("System inputs:")
            pp.pprint(proc.get_system_inputs())
            print('Heat outputs:')
            pp.pprint(proc.get_heat_outputs())
            print("Waste heats:")
            pp.pprint(proc.get_waste_heats())
            print('Miscellaneous:')
            pp.pprint(proc.get_miscellaneous())
            print("")
        print("")
