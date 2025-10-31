""""
This sample shows how to import gbXML
"""

import iesve   # the VE api

import_path = "C:/VE-Projects/example project/example.xml" # Set to the path of your gbXML file

# Import and heal geometry with volume capped at a fixed height of 1m
iesve.ImportGBXML.import_file(import_path, True, iesve.VolumeCapMode.fixed_height, 1.0)