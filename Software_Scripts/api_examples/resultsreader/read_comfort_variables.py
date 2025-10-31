import iesve        # the VE api
from ies_file_picker import IesFilePicker   # File picker

# Choose APS file
file_name = IesFilePicker.pick_aps_file()

# Open APS file:
results_reader = iesve.ResultsReader.open(file_name)
assert results_reader is not None, "Error opening results file"

# Specify the room to query
room_id = 'NR000000' # Change this to your room name

def print_result(var_name):
  print(var_name + ':', results_reader.get_room_results(room_id, var_name, var_name, 'z'))

# Display the results
print_result('People dissatisfied')
print_result('Predicted mean vote')
print_result('Comfort index')
print_result('CLO')
print_result('PMV  (ASHRAE 55 Analytical)')
print_result('PPD  (ASHRAE 55 Analytical)')
print_result('PMV  (ASHRAE 55 Analytical direct-solar)')
print_result('PPD  (ASHRAE 55 Analytical direct-solar)')
print_result('CLO  (ASHRAE 55 Analytical direct-solar)')
print_result('MRT  (ASHRAE 55 Analytical direct-solar)')
print_result('Top  (ASHRAE 55 Analytical direct-solar)')
print_result('PMV  (ASHRAE 55 Adaptive)')
print_result('PPD  (ASHRAE 55 Adaptive)')
print_result('CLO  (ASHRAE 55 Adaptive)')
print_result('PMV  (ASHRAE 55 Adaptive direct-solar)')
print_result('PPD  (ASHRAE 55 Adaptive direct-solar)')
print_result('CLO  (ASHRAE 55 Adaptive direct-solar)')
print_result('MRT  (ASHRAE 55 Adaptive direct-solar)')
print_result('Top  (ASHRAE 55 Adaptive direct-solar)')
print_result('PMV(ISO 7730 nominal air speed)')
print_result('PPD(ISO 7730 nominal air speed)')
print_result('PMV(ISO 7730 elevated air speed)')
print_result('PPD(ISO 7730 elevated air speed)')
print_result('PMV(ISO 7730 nom & elev air speed cat A)')
print_result('PPD(ISO 7730 nom & elev air speed cat A)')
print_result('PMV(ISO 7730 nom & elev air speed cat B)')
print_result('PPD(ISO 7730 nom & elev air speed cat B)')
print_result('PMV(ISO 7730 nom & elev air speed cat C)')
print_result('PPD(ISO 7730 nom & elev air speed cat C)')
print_result('Relative humidity')
print_result('Moisture content')
print_result('Wet bulb temperature')
print_result('Standard effective temperature')
print_result('Operative temperature (ASHRAE)')
print_result('Operative temperature (TM 52/CIBSE)')
print_result('Degrees > Max. adaptive temp. (TM 52 criterion 1)')
print_result('Daily weighted exceedance (TM 52 criterion 2)')
print_result('Room CO2 concentration')