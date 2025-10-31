""""
This sample shows how to get information from ApLocate

It also shows some unit conversion for temperature and distance
"""

from typing import Any
import iesve   # the VE api
import pprint  # standard Python library, makes output more readable

# python libraries for unit conversion
from decimal import Decimal # for rounding to n decimal places
from pint import UnitRegistry
ureg = UnitRegistry()
Q_: Any = ureg.Quantity

# this little helper function converts metric data from API to IP for display
def convertUnits(data):
    # Unit Conversion
    data['altitude'] = getDisplayVal(Q_(data['altitude'], ureg.meter).to(ureg.ft), 1)
    data['summer_drybulb'] = getDisplayVal(Q_(data['summer_drybulb'], ureg.degC).to(ureg.degF), 2)
    data['summer_wetbulb'] = getDisplayVal(Q_(data['summer_wetbulb'], ureg.degC).to(ureg.degF), 2)
    data['winter_drybulb'] = getDisplayVal(Q_(data['winter_drybulb'], ureg.degC).to(ureg.degF), 2)

# utility function to format numbers to defined decimal places
def getDisplayVal(data, dp = 1):
    if data != None:
        decimal_places = 1 if dp == 0 else Decimal(10) ** -dp

        # assume the number is from pints conversion
        return float(Decimal(data.magnitude).quantize(decimal_places))
    else:
        return "-"

# # MAIN BODY STARTS HERE # #
if __name__ == '__main__':
    # create the API object for ApLocate data
    loc = iesve.VELocate()

    # read the data for the current project
    loc.open_wea_data()

    # get the currently available ApLocate data as a dictionary
    data = loc.get()

    # the VE API always returns its data in Metric units, so check
    # to see if we need to convert the numbers to IP for output
    ve_display_units = iesve.VEProject.get_current_project().get_display_units()
    if ve_display_units != iesve.DisplayUnits.metric:
        convertUnits(data)

    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(data)

    loc.close_wea_data()
