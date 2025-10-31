""""
This sample shows the room data that can be read from a VEBody object

Note: for large models this script will print a lot of data and may take some time!

Note: this script converts the units to IP if the active model is in that mode.

"""

import sys
from typing import Any
import iesve    # the VE api
import pprint   # standard Python library for better format output
pp = pprint.PrettyPrinter()

# The VE returns its data in metric units.  This sample uses
# the pint package to also display the results in IP units
from pint import UnitRegistry   # python library for units conversion
# create the pint unit registry (global variable)
ureg = UnitRegistry()
Q_: Any = ureg.Quantity

def convert_units(data):
    # check what units mode the VE is in - the API returns all data
    # in Metric units - this helper function does unit conversions
    # on the unit-sensitive data for Apache Systems
    ve_display_units = iesve.VEProject.get_current_project().get_display_units()
    if ve_display_units == iesve.DisplayUnits.metric:
        return

    # convert m2 -> ft2
    floor_area = data.get('floor_area')
    if floor_area is not None:
        data['floor_area'] = Q_(floor_area, ureg.centiare).to(ureg.sq_ft).magnitude

    # convert m3 -> ft3
    volume = data.get('volume')
    if volume is not None:
        data['volume'] = Q_(volume, ureg.stere).to(ureg.cu_ft).magnitude

    # convert degrees C -> Fahrenheit
    cooling_setpoint = data.get('cooling_setpoint')
    if cooling_setpoint is not None and cooling_setpoint != '-':
        data['cooling_setpoint'] = Q_(cooling_setpoint, ureg.degC).to(ureg.degF).magnitude
    heating_setpoint = data.get('heating_setpoint')
    if heating_setpoint is not None and heating_setpoint != '-':
        data['heating_setpoint'] = Q_(heating_setpoint, ureg.degC).to(ureg.degF).magnitude

    # dhw - can have multiple unit types, so probe first
    dhw_unit_val = data.get('dhw_unit_val')
    if dhw_unit_val is not None:
        dhw = data.get('dhw')
        if dhw is not None:
            data['dhw'] = Q_(dhw, ureg.liter / ureg.hour).to(ureg.gallon / ureg.hour).magnitude
        if dhw_unit_val == 0:
            data['dhw_unit'] = 'USgall/(h\xb7pers)'
        else:
            data['dhw_unit'] = 'USgall/h'

    # convert W -> btu/h
    powers = [
        'max_humidification', 'max_dehumidification',                           # room conditions
        'max_heating_and_humidification', 'max_cooling_and_dehumidification',   # room conditions
        'heating_unit_size', 'cooling_unit_size',                               # system
        ]
    for power in powers:
        power_val = data.get(power)
        if power_val is not None:
            data[power] = Q_(power_val, ureg.W).to(ureg.Btu / ureg.hour).magnitude

    # check heating/cooling unit capacity...
    hc_prefix = ['cooling_capacity', 'heating_capacity']
    for hc_entry in hc_prefix:
        hc_is_unlimited = data.get(hc_entry + '_unlimited')
        if hc_is_unlimited is not None:
            if hc_is_unlimited == False:
                hc_val = data.get(hc_entry + '_value')
                hc_unit = data.get(hc_entry + '_unit')
                if hc_val is not None and hc_unit is not None:
                    if hc_unit == 0:  # kw -> kbtu/h
                        data[hc_entry + '_value'] = Q_(hc_val, ureg.kW).to(ureg.kBtu / ureg.hour).magnitude
                        data[hc_entry + '_unit_str'] = 'kBtu/h'
                    else:
                        data[hc_entry + '_value'] = Q_(hc_val, ureg.W / ureg.centiare).to(ureg.W / ureg.sq_ft).magnitude
                        data[hc_entry + '_unit_str'] = 'W/ft\xb2'

    # system air supply fields...
    sys_air_fields = ['system_air_minimum_flowrate', 'system_air_free_cooling']
    for air_supply_entry in sys_air_fields:
        air_vals = data.get(air_supply_entry + 's')  # get the air flows dictionary
        if air_vals is not None:
            air_vals[1] = Q_(air_vals[1], ureg.liter / ureg.second).to(ureg.cu_ft / ureg.minute).magnitude
            air_vals[2] = Q_(air_vals[2], ureg.liter / ureg.second / ureg.centiare).to(ureg.cu_ft / ureg.minute / ureg.sq_ft).magnitude
            air_vals[3] = Q_(air_vals[3], ureg.liter / ureg.second).to(ureg.cu_ft / ureg.minute).magnitude
            air_vals[4] = Q_(air_vals[4], ureg.liter / ureg.second / ureg.centiare).to(ureg.cu_ft / ureg.minute / ureg.sq_ft).magnitude

            data[air_supply_entry] = air_vals[data[air_supply_entry + '_unit']]

    # check system -> mechanical exhaust
    has_exhaust = data.get('has_mech_exhaust')
    if has_exhaust is not None:
        if has_exhaust == True:
            sfp = data.get('extract_SFP')
            if sfp is not None:
                data['extract_SFP'] = Q_(sfp, ureg.W / (ureg.liter / ureg.second)).to(ureg.W / (ureg.cu_ft / ureg.minute)).magnitude

            fr = data.get('extract_flow_rate')
            fr_unit = data.get('extract_flow_rate_unit')
            if fr is not None and fr_unit is not None:
                if fr_unit == 1:    # l/s
                    data['extract_flow_rate'] = Q_(fr, ureg.liter / ureg.second).to(ureg.cu_ft / ureg.minute).magnitude
                    data['extract_flow_rate_unit_str'] = 'cfm'
                elif fr_unit == 2:   # l/s/m2
                    data['extract_flow_rate'] = Q_(fr, ureg.liter / ureg.second / ureg.centiare).to(ureg.cu_ft / ureg.minute / ureg.sq_ft).magnitude
                    data['extract_flow_rate_unit_str'] = 'cfm/ft\xb2'
                elif fr_unit == 3:    # l/s/p
                    data['extract_flow_rate'] = Q_(fr, ureg.liter / ureg.second).to(ureg.cu_ft / ureg.minute).magnitude
                    data['extract_flow_rate_unit_str'] = 'cfm/person'

    flow_units = data.get('flow_units')
    if flow_units is not None:
        flow_units[1] = 'cfm'
        flow_units[2] = 'cfm/ft\xb2'
        flow_units[3] = 'cfm/person'
        flow_units[4] = 'cfm/(ft\xb2 fac)'


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

    # convert the max power consumptions and max_sensible_gain fields
    derived_fields = ['max_power_consumption', 'max_sensible_gain']
    for df in derived_fields:
        data_dict = gains_data.get(df + 's')
        if data_dict is not None:
            val_0_w_per_m2 = Q_(data_dict[0], ureg.W / ureg.centiare)
            val_1_w = Q_(data_dict[1], ureg.W)

            data_dict[0] = round(val_0_w_per_m2.to(ureg.W / ureg.sq_ft).magnitude, 3)
            data_dict[1] = round(val_1_w.to(ureg.Btu / ureg.hour).magnitude, 3)

    light_unit = gains_data['units_str']
    if light_unit == 'W/m\xb2':
        gains_data['units_str'] = 'W/ft\xb2'
    elif light_unit == 'W':
        gains_data['units_str'] = 'Btu/h'
    elif light_unit == 'lux':
        gains_data['units_str'] = "fc"

    power_units = gains_data['power_units']
    power_units[0] = 'W/ft\xb2'
    power_units[1] = 'Btu/h'

    if current_units == 2:    # lux -> fc
        # note, lux -> fc conversion is not in pint, so doing it manually
        mi_lux = gains_data['minimum_illuminance']
        gains_data['minimum_illuminance'] = round(mi_lux / 10.7639104, 3)


# This function does unit conversion for people gains
def convert_people_gain(gains_data, ve_display_units):
    if ve_display_units == iesve.DisplayUnits.metric:
        return      # no conversions required if the VE is set to metric

    current_units = gains_data['units_val']

    # convert the max power consumptions and max_sensible_gain fields
    derived_fields = ['max_latent_gain', 'max_sensible_gain']
    for df in derived_fields:
        data_dict = gains_data.get(df + 's')
        if data_dict is not None:
            val_0_w = Q_(data_dict[0], ureg.W)
            val_1_w = Q_(data_dict[1], ureg.W)

            data_dict[0] = round(val_0_w.to(ureg.Btu / ureg.hour).magnitude, 3)
            data_dict[1] = round(val_1_w.to(ureg.Btu / ureg.hour).magnitude, 3)

    power_unit = gains_data['units_strs'][current_units]
    if power_unit == 'W/P':
        gains_data['power_unit'] = 'Btu/h\xb7p'
        gains_data['max_latent_gain'] = gains_data['max_latent_gains'][0]
        gains_data['max_sensible_gain'] = gains_data['max_sensible_gains'][0]
    elif power_unit == 'W':
        gains_data['power_unit'] = 'Btu/h'
        gains_data['max_latent_gain'] = gains_data['max_latent_gains'][1]
        gains_data['max_sensible_gain'] = gains_data['max_sensible_gains'][1]

    power_units = gains_data['power_units']
    power_units[0] = 'Btu/h\xb7p'
    power_units[1] = 'Btu/h'

    # fix up occupancies
    occupancies = gains_data['occupancies']
    occ_m2_per_p = Q_(occupancies[0], ureg.centiare)
    occupancies[0] = round(occ_m2_per_p.to(ureg.sq_ft).magnitude, 3)

    gains_data['units_strs'][0] = 'ft\xb2/person'

# This function does unit conversion for the misc energy gains
# (not lighting, not people)
def convert_other_gains(gains_data, ve_display_units):
    if ve_display_units == iesve.DisplayUnits.metric:
        return      # no conversions required if the VE is set to metric

    current_units = gains_data['units_val']

    # convert the max power consumptions and max_sensible_gain fields
    derived_fields = ['max_power_consumption', 'max_sensible_gain', 'max_latent_gain']
    for df in derived_fields:
        data_dict = gains_data.get(df + 's')
        if data_dict is not None:
            val_0_w_per_m2 = Q_(data_dict[0], ureg.W / ureg.centiare)
            val_1_w = Q_(data_dict[1], ureg.W)

            data_dict[0] = round(val_0_w_per_m2.to(ureg.W / ureg.sq_ft).magnitude, 3)
            data_dict[1] = round(val_1_w.to(ureg.Btu / ureg.hour).magnitude, 3)

    power_units = gains_data['units_strs']
    power_units[0] = 'W/ft\xb2'
    power_units[1] = 'Btu/h'


# a utility function to do unit conversions per type of internal gain
def convert_internal_gain(gains_data, casual_gain, ve_display_units):
    # check the units mode in the VE...  convert to IP if that
    # is what the VE is currently set to
    # note - we're checking the global value that has been
    # fetched at the start of the script, just for convenience
    if ve_display_units == iesve.DisplayUnits.metric:
        return      # no conversions required if the VE is set to metric

    if isinstance(casual_gain, iesve.RoomLightingGain):
        convert_lighting_gain(gains_data, ve_display_units)
    elif isinstance(casual_gain, iesve.RoomPeopleGain):
        convert_people_gain(gains_data, ve_display_units)
    elif isinstance(casual_gain, iesve.RoomPowerGain):
        # the 'misc' gains incl machinery, cooking, computers etc
        convert_other_gains(gains_data, ve_display_units)
    else:
        print("Error: unknown internal gain type", file=sys.stderr)

def convert_air_exchange(air_exchange_data, ve_display_units):
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

    # convert all the max flows
    max_flows = air_exchange_data['max_flows']
    for key, val in max_flows.items():
        if key == 0:      # ach (no conversion required)
            continue
        elif key in [1, 3]:   # l/s -> cfm
            liters_per_second = Q_(val, ureg.liters / ureg.seconds)
            max_flows[key] = liters_per_second.to(ureg.cu_ft / ureg.minutes).magnitude
        elif key in [2,4]:   # l/s/m2 -> l/s/ft2
            liters_per_sec_per_sqm = Q_(val, ureg.liters / ureg.seconds / ureg.centiare)
            max_flows[key] = liters_per_sec_per_sqm.to(ureg.cu_ft / ureg.minutes / ureg.sq_ft).magnitude

    # convert the units strings
    units_strs = air_exchange_data['units_strs']
    units_strs[1] = 'cfm'
    units_strs[2] = 'cfm/ft\xb2'
    units_strs[3] = 'cfm/person'
    units_strs[4] = 'cfm/ft\xb2 fac'

def print_room_data(room_data):
    """
    Prints a VEBody's room data.
    Args:
        room_data: VERoomData of a VEBody.
    """
    ve_display_units = iesve.VEProject.get_current_project().get_display_units()

    print("\nGeneral:")
    general_data = room_data.get_general()
    convert_units(general_data)
    pp.pprint(general_data)
    print("\nRoom conditions:")
    room_conditions = room_data.get_room_conditions()
    convert_units(room_conditions)
    pp.pprint(room_conditions)
    print("\nApache systems:")
    apache_systems = room_data.get_apache_systems()
    convert_units(apache_systems)
    pp.pprint(apache_systems)
    print("\nInternal gains:")
    cas_gains = room_data.get_internal_gains()
    for cas_gain in cas_gains:
        gains_data = cas_gain.get()
        convert_internal_gain(gains_data, cas_gain, ve_display_units)
        pp.pprint(gains_data)
    print("\nAir exchanges:")
    air_exs = room_data.get_air_exchanges()
    for air_ex in air_exs:
        air_ex_data = air_ex.get()
        convert_air_exchange(air_ex_data, ve_display_units)
        pp.pprint(air_ex_data)

# # MAIN BODY STARTS HERE # #
if __name__ == '__main__':
    project = iesve.VEProject.get_current_project()
    real_building = project.models[0]

    # get all the bodies in the building
    bodies = real_building.get_bodies(False)
    print("Real building:")
    for body in bodies:
        # skip any bodies that aren't thermal rooms
        if body.type != iesve.VEBody_type.room:
            continue

        print("  ----------------------------------------------")

        # the Real building stores generic data
        # so ask for generic room data
        room_data = body.get_room_data(iesve.attribute_type.real_attributes)
        print("Room: ", body.id)
        print_room_data(room_data)
        print()

    # test and see if we have any variants (skip the first building, that's the real building)
    for variant in project.models[1:]:
        # test to see if this building is NCM Notional (NB Variant)
        # or Reference (RB Variant) building
        if variant.id in ['NB Variant', 'RB Variant']:
            print("# # # # # # # # # # # # # # # # # # # # ")
            print("Variant building: ", variant.id)

            bodies = variant.get_bodies(False)
            # print the details of the first room only...
            for body in bodies:
                # skip any bodies that aren't thermal rooms
                if body.type != iesve.VEBody_type.room:
                    continue

                print("  ----------------------------------------------")

                #  NCM compliance room data
                room_data = body.get_room_data(iesve.attribute_type.ncm_attributes)
                print("NCM Room: ", body.id)
                print_room_data(room_data)
                print()

                # only do 1 room, skip the rest...
                break

        # test for PRM variant
        elif variant.id in ['BB Variant']:
            print("# # # # # # # # # # # # # # # # # # # # ")
            print("Variant building: ", variant.id)

            bodies = variant.get_bodies(False)
            # print the details of the first room only...
            for body in bodies:
                # skip any bodies that aren't thermal rooms
                if body.type != iesve.VEBody_type.room:
                    continue

                print("  ----------------------------------------------")

                #  PRM data
                room_data = body.get_room_data(iesve.attribute_type.t24_attributes)
                print("PRM Room: ", body.id)
                print_room_data(room_data)
                print()

                # only do 1 room, skip the rest...
                break

        # all other variants take generic parameter
        else:
            print("# # # # # # # # # # # # # # # # # # # # ")
            print("Variant building: ", variant.id)
            print("... skipping for brevity")