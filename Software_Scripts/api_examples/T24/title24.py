""""
This sample shows how to get Title 24 data
"""

import iesve
from ies_file_picker import IesFilePicker
import pprint
pp = pprint.PrettyPrinter(indent=4)

t24 = iesve.T24()

pp.pprint(t24.get())

aps_name = IesFilePicker.pick_aps_file()
asp_name = IesFilePicker.pick_asp_file()

print(t24.get_unmet_hours(aps_name, asp_name))