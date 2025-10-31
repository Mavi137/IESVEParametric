""""
This sample shows how to get HVAC DHW data
"""

import iesve   # the VE api
from ies_file_picker import IesFilePicker

# Open ASP file:
file_name = IesFilePicker.pick_asp_file()

# Load HVAC network
hvac = iesve.HVACNetwork
network = hvac.load_network(file_name)

# Display the DHW systems data
dhw_systems = network.dhw_systems
for dhw_system in dhw_systems:
    print("")
    print("-------------", dhw_system.id, "-------------")
    print("Reference:", dhw_system.reference)
    print("Is to be autosized:", str(dhw_system.is_to_be_autosized))
    print("Design cold water inlet temperature:", dhw_system.design_cold_water_inlet_temperature)
    print("Cold water inlet temperature set point type:", dhw_system.cold_water_inlet_temperature_set_point_type)  
    print("Cold water inlet temperature set point value:", dhw_system.cold_water_inlet_temperature_value)          
    print("Cold water inlet temperature set point profile:", dhw_system.cold_water_inlet_temperature_set_point_profile)
    print("DHW model:", dhw_system.dhw_model)
    print("Heat source:", dhw_system.heat_source)
    print("Design supply temperature:", dhw_system.dhw_design_supply_temperature)
    print("Design supply temperature set point type:", dhw_system.dhw_design_supply_temperature_set_point_type)
    print("Design supply temperature set point value:", dhw_system.dhw_design_supply_temperature_set_point_value)
    print("Design supply temperature set point profile:", dhw_system.dhw_design_supply_temperature_set_point_profile)
    print("Solar water heater (SWH) pre-heat used:", dhw_system.solar_water_heater_pre_heat_used)
    print("Solar water heater (SWH):", dhw_system.solar_water_heater)
    print("Condenser heat recovery pre-heat used:", dhw_system.condenser_heat_recovery_pre_heat_used)
    print("Condenser water loop:", dhw_system.condenser_water_loop)
    
    # Branches
    branches = dhw_system.branches
    
    for branch in branches:
        print("-------------", branch, "-------------")
        print("Branch", dhw_system.get_branch_by_id(branch.id))
        print("ID:", branch.id)
        print("Reference:", branch.reference)
        print("DHW heat exchanger (HX) location on HWL:", branch.dhw_location_on_hwl)
        print("HX DHW Supply flow rate:", branch.hx_supply_flow_rate)
        print("HX Source-side flow rate:", branch.hx_source_side_flow_rate)
        print("HX Approach:", branch.hx_approach)
        print("HX Effectiveness:", branch.hx_effectiveness)
        print("HX Load HWL HX Capacity:", branch.hx_load_hwl_hx_capacity)
        print("Design supply temperature set point type:", branch.dhw_design_supply_temperature_set_point_type)
        print("Design supply temperature set point value:", branch.dhw_design_supply_temperature_set_point_value)
        print("Design supply temperature set point profile:", branch.dhw_design_supply_temperature_set_point_profile)
        print("Delivery efficiency:", branch.delivery_efficiency)
        print("Is storage tank used?:", branch.is_storage_tank_used)
        print("Tank storage volume:", branch.tank_storage_volume)
        print("Tank type:", branch.tank_type)
        print("Tank insulation type:", branch.tank_insulation_type)
        print("Tank insulation thickness:", branch.tank_insulation_thickness)
        print("Tank heat loss:", branch.tank_heat_loss)
        print("Is DHW recirculation used?:", branch.is_recirculation_used)
        print("Recirculation flow rate:", branch.recirculation_flow_rate)
        print("Is recirculation % of flow rate?:", branch.is_recirculation_percent_of_flow)
        print("% of DHW design supply flow rate:", branch.recirculation_percent_of_supply_flow_rate)
        print("Is recirculation scheduled?:", branch.is_recirculation_scheduled)
        print("Recirculation schedule type:", branch.recirculation_schedule_type)
        print("Recirculation schedule profile ID:", branch.recirculation_profile_id)
        print("Recirculation Losses:", branch.recirculation_losses)
        print("Recirculation loop length:", branch.recirculation_loop_length)
        print("Recirculation pump power:", branch.recirculation_pump_power)
        print("Recirculation pump meter:", branch.recirculation_pump_meter)
        print("Is DHW pump used?:", branch.is_pump_used)
        print("Specific pump power at rated speed:", branch.specific_pump_power_at_rated_speed)
        print("Pump heat gain fraction:", branch.pump_heat_gain_fraction)
        print("Is DHW pre-heat using Solar Water Heater (SWH)?:", branch.is_pre_heat_using_solar_water_heater)
        print("Solar water heater (SWH):", branch.solar_water_heater)
        
        # Pump
        pump = branch.pump
        if pump is not None:
            print("-------------", pump, "-------------")
            print("Pump power:", pump.pump_power)
            print("Pump efficiency factor:", pump.efficiency_factor)
            print("Pump meter:", pump.meter)
            
            curve = pump.power_curve
            print("Power curve:", curve)
            print("Curve name:", curve.curve_name)
            print("Curve description:", curve.curve_description)
            print("Curve type:", curve.curve_type)
            print("Curve role:", curve.curve_role)
            print("Curve role name:", curve.curve_role_string)
        
        # HWL DHW HX
        hwl_dhw_hx = branch.hwl_dhw_heat_exchanger
        if hwl_dhw_hx is not None:
            print("-------------", hwl_dhw_hx, "-------------")
            print("Load side entering temperature:", hwl_dhw_hx.get_load_side_entering_temperature(iesve.HVACWaterWaterHeatExchangerDataType.heating))
            print("Load side leaving temperature:", hwl_dhw_hx.get_load_side_leaving_temperature(iesve.HVACWaterWaterHeatExchangerDataType.heating))
            print("Source side entering temperature:", hwl_dhw_hx.get_source_side_entering_temperature(iesve.HVACWaterWaterHeatExchangerDataType.heating))
            print("Source side leaving temperature:", hwl_dhw_hx.get_source_side_leaving_temperature(iesve.HVACWaterWaterHeatExchangerDataType.heating))
            print("Inlet temperature delta T:", hwl_dhw_hx.inlet_temperature_delta_t)
    
    # Condenser heat recovery data
    print("------------------------------------")
    chr = dhw_system.condenser_heat_recovery
    if chr is not None:
        print("Condenser heat recovery:", chr)
        print("Capacity:", chr.capacity)
        print("Inlet temperature delta T:", chr.inlet_temperature_delta_t)
        print("Approach:", chr.get_approach(iesve.HVACWaterWaterHeatExchangerDataType.heating))
        print("Supply flow rate:", chr.get_supply_flow_rate(iesve.HVACWaterWaterHeatExchangerDataType.heating))
        print("Source flow rate:", chr.get_source_flow_rate(iesve.HVACWaterWaterHeatExchangerDataType.heating))
        print("Effectiveness:", chr.get_effectiveness(iesve.HVACWaterWaterHeatExchangerDataType.heating))
        print("Load side entering temperature:", chr.get_load_side_entering_temperature(iesve.HVACWaterWaterHeatExchangerDataType.heating))
        print("Load side entering temperature:", chr.get_load_side_leaving_temperature(iesve.HVACWaterWaterHeatExchangerDataType.heating))
        print("Source side entering temperature:", chr.get_source_side_entering_temperature(iesve.HVACWaterWaterHeatExchangerDataType.heating))
        print("Source side leaving temperature:", chr.get_source_side_leaving_temperature(iesve.HVACWaterWaterHeatExchangerDataType.heating))
    else:
        print("Condenser heat recovery:", chr)