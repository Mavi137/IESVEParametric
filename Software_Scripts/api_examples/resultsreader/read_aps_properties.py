""""
Shows how to access supplementary simulation data, including room geometry

Remember that data from an APS file may no longer resemble the current model
if the model has changed.

Notes on APS property data:
- room geometry field num_surf: is only available when detailed surface-level
    output is selected for that room
- room geometry field num_open: is only available when Macroflo was selected
    as output
- glazed area inside APS files is excluding frame area.  Therefore it does
    not match VE window opening area (which includes frame area)

"""

from typing import Any
import iesve        # the VE api
from ies_file_picker import IesFilePicker   # handy little file picker utility for samples

# The VE returns its data in metric units.  This sample uses
# the pint package to also display the results in IP units
from pint import UnitRegistry   # python library for units conversion

# create the pint unit registry (global variable)
ureg = UnitRegistry()
Q_: Any = ureg.Quantity

# little helper function to do unit conversion for areas
def convert_roomlist_details(room_list):
    # check the units mode in the VE...  convert to IP if that
    # is what the VE is currently set to
    # note - we're checking the global value that has been
    # fetched at the start of the script, just for convenience
    if ve_display_units == iesve.DisplayUnits.metric:
        return      # no conversions required if the VE is set to metric

    # if we didn't return, then we need to convert the area and
    # volume fields of the room list
    # note that the list stores tuples, and tuples are read-only
    # so we need to replace the entire tuple in the list with a new one
    for index, room in enumerate(room_list):
        room_list[index] = (room[0], room[1],       # copy room name and ID
            Q_(room[2], ureg.centiare).to(ureg.sq_ft).magnitude,  # use pint library to convert m2 -> ft2
            Q_(room[3], ureg.stere).to(ureg.cu_ft).magnitude      # use pint to convert m3 -> ft3
            )

# little helper function to convert units for room geometry
def convert_room_geometry(geometry_dict):
    # check the units mode in the VE...  convert to IP if that
    # is what the VE is currently set to
    # note - we're checking the global value that has been
    # fetched at the start of the script, just for convenience
    if ve_display_units == iesve.DisplayUnits.metric:
        return      # no conversions required if the VE is set to metric

    # all the geometry fields are m2, except for num_surf and num_open
    # so check the key to make sure conversion is necessary
    for key, value in geometry_dict.items():
        if key not in ['num_surf', 'num_open']:
            geometry_dict[key] = Q_(value, ureg.centiare).to(ureg.sq_ft).magnitude

# convenience function to convert a whole list of geometry dicts at once
def convert_room_geometry_list(geometry_list):
    if ve_display_units == iesve.DisplayUnits.metric:
        return      # no conversions required if the VE is set to metric
    for geo in geometry_list:
        convert_room_geometry(geo)

# # MAIN BODY STARTS HERE # #
if __name__ == '__main__':
    # Choose APS file
    file_name = IesFilePicker.pick_aps_file()

    # Open APS file:
    results_reader = iesve.ResultsReader.open(file_name)
    assert results_reader is not None, "Error opening results file"

    # General info:
    print("Weather file:\t\t", results_reader.weather_file)
    print("First day:\t\t", results_reader.first_day)
    print("Last day:\t\t", results_reader.last_day)
    print("Year:\t\t\t", results_reader.plot_year)
    print("Results per day:\t", results_reader.results_per_day)
    print("")

    # The VE API returns all data in metric units,
    # so we need to check the VE UI display units setting
    # to see if we should convert fields that differ between IP and metric
    ve_display_units = iesve.VEProject.get_current_project().get_display_units()

    # Rooms - get_room_list, two variants of get_room_geometry_details
    # Note, get_room_list returns a list of tuples
    # each tuple contains: (room name, room ID, room area, room volume)
    room_list = results_reader.get_room_list()
    convert_roomlist_details(room_list)
    print("Rooms (name, ID, area, volume):")
    for room in room_list:
        print("   ", room)
    if room_list:
        # Look at all rooms:
        # some APIs take a list of room IDs, so we extract the 2nd field (ID)
        # from the room list tuples into a new list
        room_id_list = [room[1] for room in room_list]

        # get geometry details for all the rooms
        all_room_geo = results_reader.get_room_geometry_details(room_id_list)
        convert_room_geometry_list(all_room_geo)
        print("Geometry of all rooms:")
        for index, geo in enumerate(all_room_geo):
            print("   Room: {}, geometry: {}".format(room_id_list[index], geo))
    print("")


    results_reader.close()
