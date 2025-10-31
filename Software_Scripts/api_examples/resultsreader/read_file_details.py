""""
This example shows how to view details of a results file
"""

import iesve        # the VE api
from ies_file_picker import IesFilePicker   # file picker utility
import pprint
pp = pprint.PrettyPrinter()

if __name__ == '__main__':
    # Choose file
    file_name = IesFilePicker.pick_vista_file([("CLG files", "*.clg"), ("HTG files", "*.htg"), ("APS files", "*.aps")], "Select a results file")

    # Open  file:
    results_reader = iesve.ResultsReader.open(file_name)
    assert results_reader is not None, "Error opening results file"

    pp.pprint(results_reader.get_data_file_details(file_name))

    results_reader.close()