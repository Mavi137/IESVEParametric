""""
This sample shows MacroFlo data
"""

from typing import Any
import iesve    # the VE api
import pprint   # standard Python library for better format output
from pint import UnitRegistry   # python library for units conversion

# create the pint unit registry (global variable)
ureg = UnitRegistry()
Q_: Any = ureg.Quantity

# Convenience function for unit conversion
def convert_units(data):
    if ve_display_units == iesve.DisplayUnits.metric:
        return      # no conversions required if the VE is set to metric
    else:
        data['opening_threshold'] = Q_(data['opening_threshold'], ureg.degC).to(ureg.degF).magnitude

        crack_flow_conversion_factor = 0.01182388
        data['crack_flow_coefficient'] = data['crack_flow_coefficient'] / crack_flow_conversion_factor
        return

# # MAIN BODY STARTS HERE # #
if __name__ == '__main__':
    project = iesve.VEProject.get_current_project()

    # The VE API returns all data in metric units,
    # so we need to check the VE UI display units setting
    # to see if we should convert fields that differ between IP and metric
    ve_display_units = project.get_display_units()

    opening_types = project.get_macro_flo_opening_types()

    pp = pprint.PrettyPrinter(indent=4)

    for opening in opening_types:
        opening_data = opening.get()
        convert_units(opening_data)
        pp.pprint(opening_data)