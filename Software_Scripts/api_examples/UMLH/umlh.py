""""
This sample shows how to get unmet load hours data
"""

import iesve
from ies_file_picker import IesFilePicker

umlh = iesve.UMLH()

aps_name = IesFilePicker.pick_aps_file()
asp_name = IesFilePicker.pick_asp_file()

print(umlh.get_unmet_hours(aps_name, asp_name, False))