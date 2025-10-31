""""
This sample shows how to import gem files
"""

import iesve   # the VE api

import_path = "C:/VE-Projects/example project/example.gem" # Set to the path of your GEM file

# Import model geometry and location from GEM file
iesve.ImportGEMFile().import_file(import_path)