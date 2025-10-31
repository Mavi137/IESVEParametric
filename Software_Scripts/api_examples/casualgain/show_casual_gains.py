""""
This sample demonstrates the available internal gains data
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

# This function does unit conversion for lighting gains
def convert_lighting_gain(gains_data, ve_display_units):
    if ve_display_units == iesve.DisplayUnits.metric:
        return      # no conversions required if the VE is set to metric

    # we check the value of the units field to see what the currently
    # active units are.  When they come from the API, all units and
    # values will be in Metric units.  Here we check what the
    # units are, and convert them to IP (updating both the numeric data
    # and the units string to indicate that the conversion has taken place)
    current_units = gains_data['units_val']
    if current_units == 0:   # W/m2 -> W/ft2
        mpc_w_per_m2 = Q_(gains_data['max_power_consumption'], ureg.W / ureg.centiare)
        msg_w_per_m2 = Q_(gains_data['max_sensible_gain'], ureg.W / ureg.centiare)

        gains_data['max_power_consumption'] = round(mpc_w_per_m2.to(ureg.W / ureg.sq_ft).magnitude, 3)
        gains_data['max_sensible_gain'] = round(msg_w_per_m2.to(ureg.W / ureg.sq_ft).magnitude, 3)

        gains_data['units_str'] = "W/ft\xb2"
    elif current_units == 1:   # W -> btu/h
        mpc_w = Q_(gains_data['max_power_consumption'], ureg.W)
        msg_w = Q_(gains_data['max_sensible_gain'], ureg.W)

        gains_data['max_power_consumption'] = round(mpc_w.to(ureg.Btu / ureg.hour).magnitude, 3)
        gains_data['max_sensible_gain'] = round(msg_w.to(ureg.Btu / ureg.hour).magnitude, 3)

        gains_data['units_str'] = "Btu/h"
    elif current_units == 2:    # lux -> fc
        # note, lux -> fc conversion is not in pint, so doing it manually
        mi_lux = gains_data['minimum_illuminance']
        msg_w_per_m2 = Q_(gains_data['max_sensible_gain'], ureg.W / ureg.centiare)

        gains_data['minimum_illuminance'] = round(mi_lux / 10.7639104, 3)
        gains_data['max_sensible_gain'] = round(msg_w_per_m2.to(ureg.W / ureg.sq_ft).magnitude, 3)

        gains_data['units_str'] = "fc"
    else:
        raise ValueError('Lighting gain: unexpected unit conversion required')

# This function does unit conversion for people gains
def convert_people_gain(gains_data, ve_display_units):
    if ve_display_units == iesve.DisplayUnits.metric:
        return      # no conversions required if the VE is set to metric

    # people energies are always expressed in W/p, so convert to Btu/h*p
    mlg_w = Q_(gains_data['max_latent_gain'], ureg.W)
    msg_w = Q_(gains_data['max_sensible_gain'], ureg.W)

    gains_data['max_latent_gain'] = round(mlg_w.to(ureg.Btu / ureg.hour).magnitude, 3)
    gains_data['max_sensible_gain'] = round(msg_w.to(ureg.Btu / ureg.hour).magnitude, 3)

    # however, the people calculation itself can be also be m2/person:
    if gains_data['units_val'] == 0:    # m2 / person
        occ_m2_per_p = Q_(gains_data['occupancy_density'], ureg.centiare)
        gains_data['occupancy_density'] = round(occ_m2_per_p.to(ureg.sq_ft).magnitude, 3)
        gains_data['units_str'] = "ft\xb2/person"

# This function does unit conversion for the misc energy gains
# (not lighting, not people)
def convert_other_gains(gains_data, ve_display_units):
    if ve_display_units == iesve.DisplayUnits.metric:
        return      # no conversions required if the VE is set to metric

    current_units = gains_data['units_val']
    if current_units == 0:   # W/m2 -> W/ft2
        mpc_w_per_m2 = Q_(gains_data['max_power_consumption'], ureg.W / ureg.centiare)
        msg_w_per_m2 = Q_(gains_data['max_sensible_gain'], ureg.W / ureg.centiare)

        gains_data['max_power_consumption'] = round(mpc_w_per_m2.to(ureg.W / ureg.sq_ft).magnitude, 3)
        gains_data['max_sensible_gain'] = round(msg_w_per_m2.to(ureg.W / ureg.sq_ft).magnitude, 3)

        gains_data['units_str'] = "W/ft\xb2"
    elif current_units == 1:   # W -> btu/h
        mpc_w = Q_(gains_data['max_power_consumption'], ureg.W)
        msg_w = Q_(gains_data['max_sensible_gain'], ureg.W)

        gains_data['max_power_consumption'] = round(mpc_w.to(ureg.Btu / ureg.hour).magnitude, 3)
        gains_data['max_sensible_gain'] = round(msg_w.to(ureg.Btu / ureg.hour).magnitude, 3)

        gains_data['units_str'] = "Btu/h"
    else:
        raise ValueError('Other gains: unexpected unit conversion required')

# a utility function to do unit conversions per type of internal gain
def convert_units_if_required(gains_data, ve_display_units):
    # check the units mode in the VE...  convert to IP if that
    # is what the VE is currently set to
    # note - we're checking the global value that has been
    # fetched at the start of the script, just for convenience
    if ve_display_units == iesve.DisplayUnits.metric:
        return      # no conversions required if the VE is set to metric

    gains_type = gains_data['type_str']
    if gains_type in ['Fluorescent Lighting', 'Tungsten Lighting'] :
        convert_lighting_gain(gains_data, ve_display_units)
    elif gains_type == "People":
        convert_people_gain(gains_data, ve_display_units)
    else:  # the 'misc' gains incl machinery, cooking, computers etc
        convert_other_gains(gains_data, ve_display_units)


# main code starts here
if __name__ == '__main__':
    # we will get the list of defined internal gain objects
    # in order to do this, we start with the currently loaded VE project
    project = iesve.VEProject.get_current_project()

    # Get list of casual gain objects from the project:
    casual_gains = project.casual_gains()

    # check what units mode the VE is in
    # the API returns all data in Metric units - if you want IP output
    # we will show some sample conversions
    ve_display_units = iesve.VEProject.get_current_project().get_display_units()

    # Print details of each of the casual gains:
    for casual_gain in casual_gains:
        gains_data = casual_gain.get()

        # all data from the API is returned in metric units
        # if the VE is set to display IP units, we can choose to convert
        # the unit-sensitive numbers.  Call a helper function for this
        convert_units_if_required(gains_data, ve_display_units)

        # print the available data to output
        print("Name:", casual_gain.name)
        print("ID:",  casual_gain.id)
        pp.pprint(gains_data)
        print()