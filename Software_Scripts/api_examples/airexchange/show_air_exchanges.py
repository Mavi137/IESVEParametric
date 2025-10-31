""""
This sample demonstrates the available air exchange data
"""

from typing import Any
import iesve   # the VE api
import pprint
pp = pprint.PrettyPrinter()

# The VE returns its data in metric units.  This sample uses
# the pint package to also display the results in IP units
from pint import UnitRegistry   # python library for units conversion
# create the pint unit registry (global variable)
ureg = UnitRegistry()
Q_: Any = ureg.Quantity

# a utility function to do some sample unit conversions
def convert_units_if_required(air_exchange_data, ve_display_units):
    # check the units mode in the VE...  convert to IP if that
    # is what the VE is currently set to
    # note - we're checking the global value that has been
    # fetched at the start of the script, just for convenience
    if ve_display_units == iesve.DisplayUnits.metric:
        return      # no conversions required if the VE is set to metric

    # if adjacent condition = external air + offset temperature
    # then convert offset_temperature to F
    if air_exchange_data['adjacent_condition_val'] == 2:
        degrees_C = Q_(air_exchange_data['offset_temperature'], ureg.delta_degC)
        air_exchange_data['offset_temperature'] = degrees_C.to(ureg.delta_degF).magnitude

    # convert the max flow fields
    # note: units_val = 0 is ach, no conversion required
    current_units = air_exchange_data['units_val']
    if current_units in [1, 3]:   # l/s -> cfm
        liters_per_second = Q_(air_exchange_data['max_flow'], ureg.liters / ureg.seconds)
        air_exchange_data['max_flow'] = liters_per_second.to(ureg.cu_ft / ureg.minutes).magnitude
        air_exchange_data['units_str'] = "cfm" if current_units == 1 else "cfm/person"
    elif current_units in [2,4]:   # l/s/m2 -> l/s/ft2
        liters_per_sec_per_sqm = Q_(air_exchange_data['max_flow'], ureg.liters / ureg.seconds / ureg.centiare)
        air_exchange_data['max_flow'] = liters_per_sec_per_sqm.to(ureg.cu_ft / ureg.minutes / ureg.sq_ft).magnitude
        air_exchange_data['units_str'] = "cfm/ft\xb2" if current_units == 2 else "cfm/ft\xb2 fac"

# main code starts here
if __name__ == '__main__':
    # we will get the list of defined air exchanges
    # in order to do this, we start with the currently loaded VE project
    project = iesve.VEProject.get_current_project()

    # get list of known air exchange objects from the project:
    air_exchanges = project.air_exchanges()

    # check what units mode the VE is in
    # the API returns all data in Metric units - if you want IP output
    # we will show some sample conversions
    ve_display_units = iesve.VEProject.get_current_project().get_display_units()

    # Print information about individual air exchanges:
    for air_exchange in air_exchanges:
        # query the air exchange object for its data
        air_exchange_data = air_exchange.get()

        # all data from the API is returned in metric units
        # if the VE is set to display IP units, we can choose to convert
        # the unit-sensitive numbers.  Call a helper function for this
        convert_units_if_required(air_exchange_data, ve_display_units)

        # print the available data to output
        pp.pprint(air_exchange_data)
        print()
        # print an empty line to separate output
        print()