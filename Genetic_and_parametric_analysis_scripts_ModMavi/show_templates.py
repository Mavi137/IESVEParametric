""""
This sample shows how to get a list of Thermal Templates,
how to read data from them, and it also writes a small
selection of data to a csv file
"""

import sys
from typing import Any
import iesve   # the VE api
import csv     # standard Python library for writing csv files
import pprint  # standard Python library, makes output more readable

# The VE returns its data in metric units.  This sample uses
# the pint package to also display the results in IP units
from pint import UnitRegistry
ureg = UnitRegistry()
Q_: Any = ureg.Quantity

# create a pretty printer object
pp = pprint.PrettyPrinter()

# The functions below convert metric data to IP for display purposes
# if the VE is set to IP display
# # UNIT CONVERSION HELPER FUNCTIONS # #
# a utility function to do some sample unit conversions
def convert_airexchange(air_exchange_data):
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

# This function does unit conversion for lighting gains
def convert_lighting_gain(gains_data):
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
def convert_people_gain(gains_data):
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
def convert_other_gains(gains_data):
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
def convert_casualgains(gains_data):
    # check the units mode in the VE...  convert to IP if that
    # is what the VE is currently set to
    # note - we're checking the global value that has been
    # fetched at the start of the script, just for convenience
    if ve_display_units == iesve.DisplayUnits.metric:
        return      # no conversions required if the VE is set to metric

    gains_type = gains_data['type_str']
    if gains_type in ['Fluorescent Lighting', 'Tungsten Lighting'] :
        convert_lighting_gain(gains_data)
    elif gains_type == "People":
        convert_people_gain(gains_data)
    else:  # the 'misc' gains incl machinery, cooking, computers etc
        convert_other_gains(gains_data)

# Convert DHW consumption
def convert_DHW(thermal_details):
    if ve_display_units == iesve.DisplayUnits.metric:
        return      # no conversions required if the VE is set to metric

    dhw_val = thermal_details['dhw']
    dhw_units = thermal_details['dhw_units']

    # dhw is expressed in either l/h or l/h/p
    # either way, the conversion is the same (USgall / hour)
    thermal_details['dhw'] = Q_(dhw_val, ureg.liter / ureg.hour).to(ureg.gallons / ureg.hour).magnitude
    if dhw_units == 'l/h':
        thermal_details['dhw_units'] = 'USgall/h'
    else:
        thermal_details['dhw_units'] = 'USgall/(h\xb7pers)'
    
# Convert Apache Systems data
def convert_apsys(ap_sys):
    if ve_display_units == iesve.DisplayUnits.metric:
        return      # no conversions required if the VE is set to metric

    capacities = ['cooling_capacity', 'heating_capacity']
    for cap in capacities:
        if ap_sys[cap + '_unlimited'] == False:
            cap_val = ap_sys[cap + '_value']
            cap_units = ap_sys[cap + '_units'] 
            
            if cap_units == 0: # kw -> kbtu/h
               cap_val_q = Q_(cap_val, ureg.kW).to(ureg.kBtu / ureg.hour)
            elif cap_units == 1: # W/m2 -> W/ft2
                cap_val_q = Q_(cap_val, ureg.W / ureg.centiare).to(ureg.W / ureg.sq_ft)
            else:
                raise ValueError("Unrecognised capacity units")
            
            ap_sys[cap + '_value'] = cap_val_q.magnitude

    # convert the system air fields
    flows = ['system_air_free_cooling', 'system_air_minimum_flowrate']
    for flow in flows:
        flow_val = ap_sys[flow]
        flow_units = ap_sys[flow + '_units']
        
        if flow_units == 0:
            continue        # ach - no conversion required
        elif flow_units in [1, 3]:   # l/s and l/s/p -> same conversion to cfm
            flow_val_q = Q_(flow_val, ureg.liter / ureg.second).to(ureg.cu_ft / ureg.minute)
        elif flow_units == 2:    # l/s/m2 -> cfm/ft2
            flow_val_q = Q_(flow_val, ureg.liter / ureg.second / ureg.centiare).to(ureg.cu_ft / ureg.minute / ureg.sq_ft)
        else:
            raise ValueError("Unrecognised system air flow units")
        
        ap_sys[flow] = flow_val_q.magnitude

# The functions below are used to display the contents of
# various categories of template data, the actual fetching
# of templates is done at the bottom of the file, inside the
# main function

# # DATA DISPLAY HELPER FUNCTIONS # #

# setpoints can be either constant value or based on a profile
# this function checks which value is applicable and returns it
def set_point_detail(project, spval, is_constant, sp_prof):
    if is_constant:
        # the set point is a constant temperature...
        # check to see if we convert the units
        setpoint_temp = spval
        if ve_display_units != iesve.DisplayUnits.metric:
            setpoint_temp = Q_(spval, ureg.degC).to(ureg.degF).magnitude
        return '{:.2f}'.format(setpoint_temp)
    sp_prof = project.group_profile(sp_prof)
    return sp_prof.reference

# display the air exchange details
def print_air_exchanges(template):
    airs = template.get_air_exchanges()
    print("Template: {}".format(template.name))
    if len(airs) == 0:
        print("  No air exchanges")
    else:
        print("  Air exchanges: {}".format(len(airs)))
    for ae in airs:
        data = ae.get()
        convert_airexchange(data)
        pp.pprint(data)
    print("")

# display the internal gains
def print_casual_gains(template):
    gains = template.get_casual_gains()
    print("Template: {}".format(template.name))
    if len(gains) == 0:
        print("  No internal gains")
    else:
        print("  Internal gains: {}".format(len(gains)))
    for gain in gains:
        data = gain.get()
        convert_casualgains(data)
        pp.pprint(data)
    print("")

# display the Systems details
def print_apsys_details(template):
    ap_sys = template.get_apache_systems()
    print("Template: {}".format(template.name))
    convert_apsys(ap_sys)
    pp.pprint(ap_sys)
    print("")

# display the Thermal details
def print_thermal_details(template, project, csvwriter):
    thermal_details = template.get_room_conditions()

    heat_profile = project.group_profile(thermal_details['heating_profile'])
    cool_profile = project.group_profile(thermal_details['cooling_profile'])
    aux_plant_profile = project.group_profile(thermal_details['plant_profile'])

    if heat_profile is None:
        heat_profile = project.daily_profile(thermal_details['heating_profile'])

    if cool_profile is None:
        cool_profile = project.daily_profile(thermal_details['cooling_profile'])

    if aux_plant_profile is None:
        aux_plant_profile = project.daily_profile(thermal_details['plant_profile'])

    if (cool_profile is None) or (heat_profile is None) or (aux_plant_profile is None):
        print("Warning: an assigned profile could not be found, skipping template\n", file=sys.stderr)
        return

    if thermal_details['dhw_profile'] == '-':
        dhw_profile_string = "Occupancy"
    else:
        if thermal_details['dhw_profile'] != "":
            dhw_profile = project.group_profile(thermal_details['dhw_profile'])
            dhw_profile_string = dhw_profile.reference
        else:
            dhw_profile_string = ""

    coolingsp = set_point_detail(project, thermal_details['cooling_setpoint'],
                                 thermal_details['cooling_setpoint_type'] == iesve.setpoint_type.constant,
                                 thermal_details['cooling_setpoint_profile'])
    heatingsp = set_point_detail(project, thermal_details['heating_setpoint'],
                                 thermal_details['heating_setpoint_type'] == iesve.setpoint_type.constant,
                                 thermal_details['heating_setpoint_profile'])

    convert_DHW(thermal_details)
    
    print('Template: {}.'.format(template.name))
    msg = '\tHeating (setpoint/profile): {} [{}].\n\tCooling (setpoint/profile): {} [{}].'
    print(msg.format(heatingsp, heat_profile.reference, coolingsp, cool_profile.reference))
    print('\tDHW: %.4f %s %s' % (thermal_details['dhw'], thermal_details['dhw_units'], dhw_profile_string))
    print('\tPlant (aux) profile: %s' % (aux_plant_profile.reference))

    # write the same to csv
    csvwriter.writerow(
        [template.name, heatingsp, heat_profile.reference, coolingsp,
         cool_profile.reference, thermal_details['dhw'],
         thermal_details['dhw_units'], dhw_profile_string,
         aux_plant_profile.reference])

# # MAIN BODY STARTS HERE # #
if __name__ == '__main__':
    # Get the current VE project.  
    # Getting the thermal templates is a project-level operation
    proj = iesve.VEProject.get_current_project()
    
    # check what units mode the VE is in
    # the API returns all data in Metric units - if you want IP output
    # we will show some sample conversions
    ve_display_units = proj.get_display_units()

    # Get a list of the known thermal templates
    # Pass True to only get templates in use (assigned), False to get all templates
    templates = proj.thermal_templates(False)
    
    # Prefix the output with project name
    print("Template details for project:" + proj.name)
    
    # We write some sample data to a csv file, stored in project folder
    # so open / create this file
    output_file = proj.path + 'profiles_thermal.csv'
    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, dialect='excel', delimiter=',',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)

        # write a csv header
        csvwriter.writerow(
            ['Template', 'Heating SP', 'Heating Prof', 'Cooling SP',
             'Cooling Prof', 'DHW', 'DHW Units', 'DHW Profile', 'Aux Profile'])

        # the templates are returned as a dictionary
        # for this sample we don't need the key (the template handle)
        # so iterate over the dictionary values only
        for template in templates.values():
            
            # we can check the type of a template by checking its 'standard' attribute
            # this returns an enum that can represent: generic, NCM, or PRM
            # this allows filtering of templates similar to BTM's behaviour of not showing
            # NCM templates by default
            if template.standard != iesve.VEThermalTemplate_standard.generic:
                continue  # skip PRM and NCM templates
            
            # the following functions display data from the template
            # the first one also writes some data to csv
            print_thermal_details(template, proj, csvwriter)
            print_apsys_details(template)
            print_casual_gains(template)
            print_air_exchanges(template)

    # done with the output - the csv file will be closed automatically when the 
    # with statement goes out of scope...