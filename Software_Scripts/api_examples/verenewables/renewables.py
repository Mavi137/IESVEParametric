""""
This sample shows Renewables data
"""

from typing import Any
import iesve    # the VE api
import pprint   # standard Python library for better format output
from pint import UnitRegistry   # python library for units conversion

# create the pint unit registry (global variable)
ureg = UnitRegistry()
Q_: Any = ureg.Quantity

def convert_pv_units(pv):
    if ve_display_units == iesve.DisplayUnits.metric:
        return # no conversions required if the VE is set to metric
    else:
        pv["area"] = Q_(pv["area"], ureg.centiare).to(ureg.square_feet).magnitude
        return

def convert_pv_type_units(type):
    if ve_display_units == iesve.DisplayUnits.metric:
        return # no conversions required if the VE is set to metric
    else:
        type["ref_irradiance"] = Q_(type["ref_irradiance"], ureg.W / ureg.centiare).to(ureg.W / ureg.square_feet).magnitude
        type["temp_coefficient"] = 5 / 9 * type["temp_coefficient"] # convert to delta degF
        return

def convert_wind_units(wind):
    if ve_display_units == iesve.DisplayUnits.metric:
        return # no conversions required if the VE is set to metric
    else:
        wind["hub_height"] = Q_(wind["hub_height"], ureg.metres).to(ureg.feet).magnitude
        return

def convert_chp_units(chp):
    if ve_display_units == iesve.DisplayUnits.metric:
        return # no conversions required if the VE is set to metric
    else:
        chp["heat_output"] = Q_(chp["heat_output"], ureg.kW).to(ureg.kBtu / ureg.hour).magnitude
        return

# # MAIN BODY STARTS HERE # #
if __name__ == '__main__':
    project = iesve.VEProject.get_current_project()

    # The VE API returns all data in metric units,
    # so we need to check the VE UI display units setting
    # to see if we should convert fields that differ between IP and metric
    ve_display_units = project.get_display_units()

    renewables = iesve.VERenewables()
    pp = pprint.PrettyPrinter(indent=4)

    # PV Data
    pvs = renewables.get_pv_data()

    pp.pprint("PVs:")
    for pv in pvs:
        convert_pv_units(pv)
        pp.pprint(pv)

    # Wind Data
    wind = renewables.get_wind_data()
    convert_wind_units(wind)

    pp.pprint("Wind:")
    pp.pprint(wind)

    # CHP Data
    chp = renewables.get_chp_data()
    convert_chp_units(chp)

    pp.pprint("CHP:")
    pp.pprint(chp)

    # PV Types
    types = renewables.get_pv_types()

    pp.pprint("PV Types:")
    for type in types:
        convert_pv_type_units(type)
        pp.pprint(type)