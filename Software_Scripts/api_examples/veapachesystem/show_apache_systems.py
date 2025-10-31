""""
This sample shows Apache Systems data
"""

from typing import Any
import iesve    # the VE api
import pprint   # standard Python library for better format output

# The VE returns its data in metric units.  This sample uses
# the pint package to also display the results in IP units
from pint import UnitRegistry   # python library for units conversion
# create the pint unit registry (global variable)
ureg = UnitRegistry()
Q_: Any = ureg.Quantity

def convert_units(apSys_data):
    # check what units mode the VE is in - the API returns all data
    # in Metric units - this helper function does unit conversions
    # on the unit-sensitive data for Apache Systems
    ve_display_units = iesve.VEProject.get_current_project().get_display_units()
    if ve_display_units == iesve.DisplayUnits.metric:
        return

    # convert degrees C -> Fahrenheit
    HR_return_temp = apSys_data.get('HR_return_temp')
    if HR_return_temp is not None:
        apSys_data['HR_return_temp'] = Q_(HR_return_temp, ureg.degC).to(ureg.degF).magnitude
    cold_water_inlet_temp = apSys_data.get('cold_water_inlet_temp')
    if cold_water_inlet_temp is not None:
        apSys_data['cold_water_inlet_temp'] = Q_(cold_water_inlet_temp, ureg.degC).to(ureg.degF).magnitude
    supply_temp = apSys_data.get('supply_temp')
    if supply_temp is not None:
        apSys_data['supply_temp'] = Q_(supply_temp, ureg.degC).to(ureg.degF).magnitude

    # temperature differential C -> Fahrenheit
    temperature_difference = apSys_data.get('temperature_difference')
    if temperature_difference is not None:
        apSys_data['temperature_difference'] = Q_(temperature_difference, ureg.delta_degC).to(ureg.delta_degF).magnitude

    # convert W -> btu/h
    gen_size = apSys_data.get('gen_size')
    if gen_size is not None:
        apSys_data['gen_size'] = Q_(gen_size, ureg.W).to(ureg.Btu / ureg.hour).magnitude

    # convert W/m -> btu/(h*ft)
    circulation_losses = apSys_data.get('circulation_losses')
    if circulation_losses is not None:
        apSys_data['circulation_losses'] = Q_(circulation_losses, ureg.W / ureg.meter).to(ureg.Btu / ureg.hour / ureg.ft).magnitude

    # convert W/m2 -> btu/(h*ft2)
    AEV = apSys_data.get('AEV')
    if AEV is not None:
        apSys_data['AEV'] = Q_(AEV, ureg.W / ureg.centiare).to(ureg.Btu / ureg.hour / ureg.sq_ft).magnitude
    off_schedule_AEV = apSys_data.get('off_schedule_AEV')
    if off_schedule_AEV is not None:
        apSys_data['off_schedule_AEV'] = Q_(off_schedule_AEV, ureg.W / ureg.centiare).to(ureg.Btu / ureg.hour / ureg.sq_ft).magnitude
    # and per year (same conversion)
    equivalent_energy = apSys_data.get('equivalent_energy')
    if equivalent_energy is not None:
        apSys_data['equivalent_energy'] = Q_(equivalent_energy, ureg.W / ureg.centiare).to(ureg.Btu / ureg.hour / ureg.sq_ft).magnitude

    # convert mm -> inches
    insulation_thickness = apSys_data.get('insulation_thickness')
    if insulation_thickness is not None:
        apSys_data['insulation_thickness'] = Q_(insulation_thickness, ureg.mm).to(ureg.inches).magnitude

    # convert meters -> feet
    loop_length = apSys_data.get('loop_length')
    if loop_length is not None:
        apSys_data['loop_length'] = Q_(loop_length, ureg.m).to(ureg.ft).magnitude

    # convert m2 -> ft2
    area = apSys_data.get('area')
    if area is not None:
        apSys_data['area'] = Q_(area, ureg.centiare).to(ureg.sq_ft).magnitude

    # convert liter -> us gallons
    storage_volume = apSys_data.get('storage_volume')
    if storage_volume is not None:
        apSys_data['storage_volume'] = Q_(storage_volume, ureg.liter).to(ureg.gallon).magnitude

    # convert kWh/(l*day) -> btu/(gallon*day)
    storage_losses = apSys_data.get('storage_losses')
    if storage_losses is not None:
        apSys_data['storage_losses'] = Q_(storage_losses, ureg.kWh / ureg.liter).to(ureg.Btu / ureg.gallon).magnitude

    # convert l/(hour*m2) -> gallon/(hour*ft2)
    flow_rate = apSys_data.get('flow_rate')
    if flow_rate is not None:
        apSys_data['flow_rate'] = Q_(flow_rate, ureg.liter / ureg.hour / ureg.centiare).to(ureg.gallon / ureg.hour / ureg.sq_ft).magnitude

    # fan power: W/(l/s) -> W/cfm
    SFP = apSys_data.get('SFP')
    if SFP is not None:
        apSys_data['SFP'] = Q_(SFP, ureg.W / (ureg.liter / ureg.second)).to(ureg.W / (ureg.cu_ft / ureg.minute)).magnitude

    # air flow: l/s -> cfm
    cooling_max_flow = apSys_data.get('cooling_max_flow')
    if cooling_max_flow is not None:
        apSys_data['cooling_max_flow'] = Q_(cooling_max_flow, ureg.liter / ureg.second).to(ureg.cu_ft / ureg.minute).magnitude
    OA_max_flow = apSys_data.get('OA_max_flow')
    if OA_max_flow is not None:
        apSys_data['OA_max_flow'] = Q_(OA_max_flow, ureg.liter / ureg.second).to(ureg.cu_ft / ureg.minute).magnitude

# # Main script starts here # #
if __name__ == '__main__':
    # Print ID of default system in the current project
    default_sys_id = iesve.VEApacheSystem.default()
    print("Default system:", default_sys_id, "\n")

    pp = pprint.PrettyPrinter(indent=4)

    # Print details of all systems in the current project
    project = iesve.VEProject.get_current_project()
    ap_systems = project.apache_systems()
    for ap_sys in ap_systems:
        print("System")
        print("  ID:\t{}".format(ap_sys.id))
        print("  Name:\t{}".format(ap_sys.name))
        print("")

        # Heating
        print("  Heating:")
        heating = ap_sys.heating()
        convert_units(heating)
        pp.pprint(heating)
        fuel_id = heating.get('fuel')
        meter_branch = heating.get('meter_branch')
        if fuel_id is not None and meter_branch is not None:
            print("  Heating fuel name:", iesve.VEApacheSystem.fuel_name(fuel_id))
            print("  Heating meter name:", iesve.VEApacheSystem.meter_name(fuel_id, meter_branch))
        else:
            print("  Heating has no fuel.")
        print("")

        # Cooling
        print("  Cooling:")
        cooling = ap_sys.cooling()
        convert_units(cooling)
        pp.pprint(cooling)
        mech_id = cooling.get('cool_vent_mechanism')
        if mech_id is None:
            print("  No cooling mechanism.")
        fuel_id = cooling.get('fuel')
        meter_branch = cooling.get('meter_branch')
        if fuel_id is not None and meter_branch is not None:
            print("  Cooling fuel name:", iesve.VEApacheSystem.fuel_name(fuel_id))
            print("  Cooling meter name:", iesve.VEApacheSystem.meter_name(fuel_id, meter_branch))
        else:
            print("  Cooling system has no fuel.")
        print("")

        # Hot water
        print("  Hot water:")
        hot_water = ap_sys.hot_water()
        convert_units(hot_water)
        pp.pprint(hot_water)
        insu_id = hot_water.get('insulation_type')
        if insu_id is None:
            print("  Hot water has no insulation type.")
        print("")

        # Solar water heating
        print("  Solar water heating:")
        shw = ap_sys.solar_water_heating()
        convert_units(shw)
        pp.pprint(shw)
        shw_type = shw.get('type')
        if shw_type is None:
            print("  Solar water heating has no type")
        fuel_id = shw.get('pump_fuel')
        meter_branch = shw.get('pump_meter_branch')
        if fuel_id is not None and meter_branch is not None:
            print("  SHW pump fuel name:", iesve.VEApacheSystem.fuel_name(fuel_id))
            print("  SHW pump meter name:", iesve.VEApacheSystem.meter_name(fuel_id, meter_branch))
        else:
            print("  SHW pump has no fuel.")
        print("  Solar water heating - derived values:")
        pp.pprint(ap_sys.solar_water_heating_derived())
        print("")

        # Auxiliary energy
        print("  Auxiliary energy:")
        aux_energy = ap_sys.auxiliary_energy()
        convert_units(aux_energy)
        pp.pprint(aux_energy)
        mech_id = aux_energy.get('method')
        if mech_id is None:
            print("  Auxiliary energy has no method.")
        print("")

        # Air supply
        print("  Air supply:")
        air_supply = ap_sys.air_supply()
        convert_units(air_supply)
        pp.pprint(air_supply)
        condition_id = air_supply.get('condition')
        if condition_id is None:
            print("  Air supply has no condition.")
        print("")

        # Control
        print("  Control:")
        pp.pprint(ap_sys.control())
        print("")
