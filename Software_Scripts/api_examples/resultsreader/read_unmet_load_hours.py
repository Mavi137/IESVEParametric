""""
This sample shows how to access unmet load hours data
"""

import iesve        # the VE api
from ies_file_picker import IesFilePicker   # File picker utility

# Choose APS file
file_name = IesFilePicker.pick_aps_file()

# Open APS file:
results_reader = iesve.ResultsReader.open(file_name)
assert results_reader is not None, "Error opening results file"

umlh = results_reader.get_unmet_hours()
print("Cooling: " + str(umlh['cooling']))
print("Heating: " + str(umlh['heating']))

results_reader.close()