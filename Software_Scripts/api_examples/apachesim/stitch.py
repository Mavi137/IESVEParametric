""""
This sample shows how to stich
Apache simulation files
"""

import iesve        # the VE api

sim = iesve.ApacheSim()
project = iesve.VEProject.get_current_project()

# Replace this list with the files you wish to stitch
list_of_aps_files = [project.path + "Month 1.aps", project.path + "Month 2.aps", project.path + "Month 3.aps",
                     project.path + "Month 4.aps", project.path + "Month 5.aps", project.path + "Month 6.aps",
                     project.path + "Month 7.aps", project.path + "Month 8.aps", project.path + "Month 9.aps",
                     project.path + "Month 10.aps", project.path + "Month 11.aps", project.path + "Month 12.aps"]

# Stitch into a file called 'example.aps'
sim.stitch(project.path + "example.aps", list_of_aps_files)