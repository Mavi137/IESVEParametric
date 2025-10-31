""""
This sample shows how to get HVAC data
"""

import iesve # the VE api
from ies_file_picker import IesFilePicker
import pprint
pp = pprint.PrettyPrinter()

# Open APS file:
file_name = IesFilePicker.pick_aps_file()

# Load the HVAC network
with iesve.ResultsReader.open(file_name) as results_file_reader:
    hvac = iesve.HVACNetwork
    network = hvac.load_network(results_file_reader.hvac_file)

    # Print HVAC data
    print("Network data")
    print("\nName: " + network.name)
    print("Path: " + network.path)
    print("Is updated post-sizing:", network.is_updated_post_sizing())

    print("\nSystems:")
    print(network.systems_dict)

    num_layers = 0
    print("-----------------")
    print("Multiplexes")
    for multiplex in network.multiplexes:
        print("\n", multiplex)
        print("\nLayer editing mode:", multiplex.layer_editing_mode)
        num_layers = multiplex.number_of_layers
        print("Number of layers:", num_layers)

    print("-----------------")
    print ("Systems data")
    for system in network.systems:
        print("\n", system)
        print("\nStandard: "+ system.standard)
        print("System type:", system.system_type)
        print("Is valid:", system.is_valid)
        print("Is sizing enabled:", system.is_sizing_enabled)
        print("Number of layers:", system.number_of_layers)
        print("Multiplex:", system.multiplex)
        print("Components:", system.components)
        print("Controllers:", system.controllers)
        print("Guid:", system.guid)

        layer = 0
        while layer < num_layers:
            print ("\nLayer:", layer)
            print("\nSpace ID:", system.get_space_id(layer))
            print("Outdoor airflow of max cooling primary supply air %:", system.get_oa_percentage_of_max_cooling_primary_sa(layer))
            print("Outdoor airflow of max heating primary supply air %:", system.get_oa_percentage_of_max_heating_primary_sa(layer))
            print("Cooling max primary airflow:", system.get_cooling_max_primary_airflow(layer))
            print("Heating max primary airflows:", system.get_heating_max_primary_airflow(layer))
            print("Cooling design load:", system.get_cooling_design_load(layer))
            print("Cooling design load per area:",system.get_cooling_design_load_per_area(layer))
            print("Cooling design load per area inversed:",system.get_cooling_design_load_per_area_inversed(layer))
            print("Heating design load:", system.get_heating_design_load(layer))
            print("Heating design load per area:", system.get_heating_design_load_per_area(layer))
            print("Heating design load per area inversed:", system.get_heating_design_load_per_area_inversed(layer))
            print("Room cooling peak month:", system.get_room_cooling_peak_month(layer))
            print("Room cooling peak time:", system.get_room_cooling_peak_time(layer))
            print("Room heating peak month:", system.get_room_heating_peak_month(layer))
            print("Room heating peak time:", system.get_room_heating_peak_time(layer))
            print("Peak data:")
            pp.pprint(system.get_peak_data(layer))
            print("Node data:")
            print("is_single_zone_system", system.is_single_zone_system)
            if system.is_single_zone_system:
                pp.pprint(system.get_node_data(layer))
            else:
                pp.pprint(system.get_node_data())
            layer = layer + 1

    print("-----------------")
    print("Components")
    for component in network.components:
        print("\n", component)
        print("\nIs duct:", component.is_duct)
        print("Inlet nodes:", component.inlet_nodes)
        print("Outlet nodes:", component.outlet_nodes)
        print("Network:", component.network)
        print("ID:", component.id)
        print("Reference:", component.reference)
        print("System ID:", component.system_id)
        print("Multiplex ID:", component.multiplex_id)
        print("Network object type:", component.network_object_type)
        print("Is selected:", component.is_selected)
        print("Multiplex layer number:", component.multiplex_layer_number)
        print("Available system links:", component.available_system_links)
        print("System link:", component.system_link)
        print("Component type:", component.aps_component_type)

        if isinstance(component, iesve.HVACHeatingCoil):
            print("Model type:", component.model_type)
            print("System type:", component.system_type)
            print("Heat transfer loop:", component.htl)
            print("Hot water loop circuit:", component.hot_water_loop_circuit)

            print("Heat source:", component.heat_source)

            if isinstance(component.heat_source, iesve.HVACAbstractHeatPump):
                print("Min source temperature:", component.heat_source.min_source_temperature)
                print("Number of COP entries:", component.heat_source.number_of_cop_entries)
                print("Heat source ID:", component.heat_source.id)
                print("Heat pump type:", component.heat_source.heat_pump_type)
                print("Heat pump performance:", component.heat_source.performance)

            print("Design sizing parameters: ")
            pp.pprint(component.design_parameters)

        if isinstance(component, iesve.HVACCoolingCoil):
            print("Model type:", component.model_type)
            print("System type:", component.system_type)
            print("Cooling source:", component.cooling_source)

            if component.system_type is iesve.HVACCoolingSourceSystemType.chilled_water_loop:
                print("Chilled water loop circuit:", component.chilled_water_loop_circuit)

            print("Design sizing parameters: ")
            pp.pprint(component.design_parameters)

        if isinstance(component, iesve.HVACFan):
            print("Is autosizable:", component.is_autosizable)
            print("Is variable air volume:", component.is_variable_air_volume)
            print("Oversizing factor:", component.oversizing_factor)
            print("Design flow rate:", component.design_flow_rate)
            print("Design total pressure:", component.design_total_pressure)
            print("Fan efficiency at design flow rate:", component.fan_efficiency_at_design_flow_rate)
            print("Motor efficiency at design flow rate:", component.motor_efficiency_at_design_flow_rate)
            print("Motor airstream heat pickup factor:", component.motor_airstream_heat_pickup_factor)
            print("Design fan power:", component.design_fan_power)

        if isinstance(component, iesve.HVACThermalDuctProperties):
            print("Duct surface area:", component.duct_surface_area)
            print("Duct U-value:", component.duct_u_value)
            print("Space ID:", component.space_id)
            print("Body index:", component.body_index)
            print("Duct location:", component.duct_location)

        if isinstance(component, iesve.HVACRoom):
            print("Is disconnected room:", component.is_disconnected_room)
            print("Is principal:", component.is_principal)

            for radiator in component.radiator_units:
                print("Radiator ID:", radiator.radiator_id)
                print("Heat source ID:", radiator.heat_source_id)
                print("Get heat source type:", radiator.get_heat_source_type)

            for chilled_ceiling in component.chilled_ceiling_room_units:
                print("Cooling source type:", chilled_ceiling.cooling_source_type)
                print("Chilled ceiling ID:", chilled_ceiling.chilled_ceiling_id)
                print("Cooling source ID:", chilled_ceiling.cooling_source_id)
                print("Chiller ID:", chilled_ceiling.chiller_id)

            for direct_heater in component.direct_acting_heater_room_units:
                print("Direct acting heater ID:", direct_heater.direct_acting_heater_id)
                print("Heat output proportional controller ID:", direct_heater.heat_output_proportional_controller_id)
                print("Heat output for min control signal:", direct_heater.heat_output_for_min_control_signal)
                print("Heat output for max control signal:", direct_heater.heat_output_for_max_control_signal)
                print("Heat output proportional control:", direct_heater.heat_output_proportional_control)
                print("Heat output midband profile ID:", direct_heater.heat_output_midband_profile_id)
                print("Heat output midband:", direct_heater.heat_output_midband)
                print("Heat output proportional bandwidth:", direct_heater.heat_output_proportional_bandwidth)
                print("Heat output max change per time step:", direct_heater.heat_output_max_change_per_time_step)
                print("Heat output midband mode:", direct_heater.heat_output_midband_mode)
                print("Heat output proportional sensor location:", direct_heater.heat_output_proportional_sensor_location)
                print("Heat output proportional sensor room ID:", direct_heater.heat_output_proportional_sensor_room_id)
                print("Heat output proportional sensor body index:", direct_heater.heat_output_proportional_sensor_body_index)
                print("Heat output proportional sensed variable:", direct_heater.heat_output_proportional_sensed_variable)
                print("Prop heat output radiant fraction:", direct_heater.prop_heat_output_radiant_fraction)
                print("Prop heat output orientation:", direct_heater.prop_heat_output_orientation)
                print("Prop heat output slope:", direct_heater.prop_heat_output_slope)

        if isinstance(component, iesve.HVACZone):
            print("Zone ID:", component.zone_id)
            print("Room IDs:", component.room_ids)

        if isinstance(component, iesve.HVACSprayChamber):
            print("Circulation pump power:", component.circulation_pump_power)
            print("Spray efficiency:", component.spray_efficiency)

        if isinstance(component, iesve.HVACSteamHumidifier):
            print("Maximum output:", component.maximum_output)
            print("Maximum relative humidity:", component.maximum_relative_humidity)
            print("Total efficiency:", component.total_efficiency)
            print("Boiler supply flag:", component.boiler_supply_flag)
            print("Heat source ID:", component.heat_source_id)

        if isinstance(component, iesve.HVACDamper):
            print("Minimum flow:", component.minimum_flow)
            print("Modulating profile profile id:", component.modulating_profile_profile_id)
            print("Mid node:", component.mid_node)

        if isinstance(component, iesve.HVACRadiator):
            print("Distribution pump consumption:", component.distribution_pump_consumption)
            print("Max input from boiler:", component.max_input_from_boiler)
            print("Radiant fraction:", component.radiant_fraction)
            print("Reference temp difference:", component.reference_temp_difference)
            print("Output at ref temp difference:", component.output_at_ref_temp_difference)
            print("Weight:", component.weight)
            print("Water capacity:", component.water_capacity)
            print("Material index:", component.material_index)
            print("Orientation:", component.orientation)

        if isinstance(component, iesve.HVACChilledCeiling):
            print("Distribution pump consumption:", component.distribution_pump_consumption)
            print("Max cooling from chiller:", component.max_cooling_from_chiller)
            print("Radiant fraction:", component.radiant_fraction)
            print("Reference temp difference:", component.reference_temp_difference)
            print("Output at ref temp difference:", component.output_at_ref_temp_difference)
            print("Weight:", component.weight)
            print("Water capacity:", component.water_capacity)
            print("Material index:", component.material_index)
            print("Orientation:", component.orientation)

        if isinstance(component, iesve.HVACDirectActingHeater):
            print("Radiant fraction:", component.radiant_fraction)
            print("Efficiency:", component.efficiency)
            print("Uses CHP:", component.uses_chp)
            print("Sequence number:", component.sequence_number)

        if isinstance(component, iesve.HVACAirToAirHeatEnthalpyExchanger):
            print("Sensible heat effectiveness:", component.sensible_heat_effectiveness)
            print("Latent heat effectiveness:", component.latent_heat_effectiveness)
            print("Motor or pump power:", component.motor_or_pump_power)

        if isinstance(component, iesve.HVACUnitaryCoolingSystem):
            print("Design air flow rate:", component.design_air_flow_rate)
            print("Scale performance parameters with design air flow rate:", component.scale_performance_parameters_with_design_air_flow_rate)
            print("Low load COPR degradation factor:", component.low_load_copr_degradation_factor)
            print("Heat rejection fan power:", component.heat_rejection_fan_power)
            print("Supply fan power:", component.supply_fan_power)
            print("Extrapolate performance data:", component.extrapolate_performance_data)
            print("Design airflow autosized:", component.design_airflow_autosized)

        if isinstance(component, iesve.HVACDedicatedWatersideEconomizer):
            print("Back up chilled water loop ID:", component.back_up_chilled_water_loop_id)
            print("Use back up chilled water loop cooling tower and pump params:", component.use_back_up_chilled_water_loop_cooling_tower_and_pump_params)
            print("Design cooling tower approach:", component.design_cooling_tower_approach)
            print("Design cooling tower range:", component.design_cooling_tower_range)
            print("Design outside wet bulb temperature:", component.design_outside_wet_bulb_temperature)
            print("Design cooling tower load:", component.design_cooling_tower_load)
            print("Heat exchanger effectiveness:", component.heat_exchanger_effectiveness)
            print("Cooling coil design water delta T:", component.cooling_coil_design_water_delta_t)
            print("Cooling tower design fan power:", component.cooling_tower_design_fan_power)
            print("Fan control:", component.fan_control)
            print("Low speed fan flow fraction:", component.low_speed_fan_flow_fraction)
            print("Low speed fan power fraction:", component.low_speed_fan_power_fraction)
            print("Design pump power:", component.design_pump_power)
            print("Operates only when it can meet the coil load in full:", component.operates_only_when_it_can_meet_the_coil_load_in_full)

        if isinstance(component, iesve.HVACAbstractDXCoolingSystem):
            print("Min part load ratio:", component.min_part_load_ratio)
            print("Fan electric input ratio:", component.fan_electric_input_ratio)
            print("Condenser type:", component.condenser_type)
            print("Outdoor air dry bulb temp:", component.outdoor_air_dry_bulb_temp)
            print("Coil wet bulb temp:", component.coil_wet_bulb_temp)
            print("Coefficient:", component.coefficient)

        if isinstance(component, iesve.HVACHeatSource):
            print("Equipment:", component.equipment)
            print("Design heating capacity:", component.design_heating_capacity)


        if isinstance(component, iesve.HVACWaterSourceLoop):
            print("Specific pump power:", component.specific_pump_power)
            print("Pump efficiency:", component.pump_efficiency)
            print("Pump heat gain:", component.pump_heat_gain)
            print("Pump delta T:", component.pump_delta_t)

        if isinstance(component, iesve.HVACPreCoolingLoop):
            print("Heat recovery used:", component.heat_recovery_used)
            print("Water source loop used:", component.water_source_loop_used)
            print("Autosizable:", component.autosizable)
            print("Autosized:", component.autosized)
            print("Autosize value:", component.autosize_value)
            print("Capacity:", component.capacity)
            print("Heat recovery recipient set:", component.heat_recovery_recipient_set)
            print("Deprecated heat recovery:", component.deprecated_heat_recovery)
            print("Heat recovery recipient ID:", component.heat_recovery_recipient_id)
            print("Cooling tower autosizable:", component.cooling_tower_autosizable)
            print("Dry fluid cooler autosizable:", component.dry_fluid_cooler_autosizable)
            print("Water source loop autosizable:", component.water_source_loop_autosizable)
            print("Water source loop autosize value:", component.water_source_loop_autosize_value)

        if isinstance(component, iesve.HVACWaterWaterHeatExchanger):
            print("Is design heat rejection autosized:", component.HVACWaterWaterHeatExchanger)

        if isinstance(component, iesve.HVACGenericCoolingSource):
            print("Distribution losses:", component.distribution_losses)
            print("Oversizing factor:", component.oversizing_factor)
            print("PLC chiller:", component.plc_chiller)
            print("Is output capacity sized:", component.is_output_capacity_sized)

        if isinstance(component, iesve.HVACRoomUnit):
            print("Number of OR connections:", component.number_of_or_connections)
            print("High sensor input:", component.high_sensor_input)
            print("Sensed variable:", component.sensed_variable)
            print("Set point mode:", component.set_point_mode)
            print("On/off sensor body index:", component.on_off_sensor_body_index)
            print("Number of AND connections:", component.number_of_and_connections)
            print("Sensor location:", component.sensor_location)
            print("Set point value:", component.set_point_value)
            print("Deadband value:", component.deadband_value)
            print("Radiant fraction:", component.radiant_fraction)
            print("Orientation:", component.orientation)
            print("Slope:", component.slope)
            print("Time switch profile ID:", component.time_switch_profile_id)
            print("On/off controller ID:", component.on_off_controller_id)
            print("On/off sensor room ID:", component.on_off_sensor_room_id)
            print("Set point profile ID:", component.set_point_profile_id)
            print("Is setpoint sensor enabled:", component.is_setpoint_sensor_enabled)

        if isinstance(component, iesve.HVACSourceDependentRoom):
            print("Model ID:", component.model_id)
            print("Thermal source ID:", component.thermal_source_id)
            print("Flow proportional controller ID:", component.flow_proportional_controller_id)
            print("Temp proportional controller ID:", component.temp_proportional_controller_id)
            print("Flow midband profile ID:", component.flow_midband_profile_id)
            print("Temp midband profile ID:", component.temp_midband_profile_id)
            print("Flow proportional sensor room ID:", component.flow_proportional_sensor_room_id)
            print("Temp proportional sensor room ID:", component.temp_proportional_sensor_room_id)
            print("Flow for min control signal:", component.flow_for_min_control_signal)
            print("Flow for max control signal:", component.flow_for_max_control_signal)
            print("Temp for min control signal:", component.temp_for_min_control_signal)
            print("Temp for max control signal:", component.temp_for_max_control_signal)
            print("Flow midband:", component.flow_midband)
            print("Flow proportional bandwidth:", component.flow_proportional_bandwidth)
            print("Flow max change per time step:", component.flow_max_change_per_time_step)
            print("Temp midband:", component.temp_midband)
            print("Temp proportional bandwidth:", component.temp_proportional_bandwidth)
            print("Temp max change per time step:", component.temp_max_change_per_time_step)
            print("Prop flow radiant fraction:", component.prop_flow_radiant_fraction)
            print("Prop flow orientation:", component.prop_flow_orientation)
            print("Prop flow slope:", component.prop_flow_slope)
            print("Prop temp radiant fraction:", component.prop_temp_radiant_fraction)
            print("Prop temp orientation:", component.prop_temp_orientation)
            print("Prop temp slope:", component.prop_temp_slope)
            print("Number of units:", component.number_of_units)
            print("Design room air temp:", component.design_room_air_temp)
            print("Design room radiant temp:", component.design_room_radiant_temp)
            print("Design heating cooling load:", component.design_heating_cooling_load)
            print("Design water delta T:", component.design_water_delta_t)
            print("Oversizing factor:", component.oversizing_factor)
            print("Flow midband mode:", component.flow_midband_mode)
            print("Temp midband mode:", component.temp_midband_mode)
            print("Flow proportional sensor location:", component.flow_proportional_sensor_location)
            print("Temp proportional sensor location:", component.temp_proportional_sensor_location)
            print("Flow proportional sensor body index:", component.flow_proportional_sensor_body_index)
            print("Temp proportional sensor body index:", component.temp_proportional_sensor_body_index)
            print("Flow proportional sensed variable:", component.flow_proportional_sensed_variable)
            print("Temp proportional sensed variable:", component.temp_proportional_sensed_variable)
            print("Error code:", component.error_code)
            print("Flow proportional control:", component.flow_proportional_control)
            print("Temp proportional control:", component.temp_proportional_control)
            print("Water loop supply temperature used:", component.water_loop_supply_temperature_used)
            print("Autosize mode:", component.autosize_mode)

        if isinstance(component, iesve.HVACPump):
            print("Pump power:", component.pump_power)
            print("Efficiency factor:", component.efficiency_factor)

            curve = component.power_curve
            print("Power curve:", curve)
            print("Curve name:", curve.curve_name)
            print("Curve description:", curve.curve_description)
            print("Curve type:", curve.curve_type)
            print("Curve role:", curve.curve_role)
            print("Curve role name:", curve.curve_role_string)

        if isinstance(component, iesve.HVACWaterLoopHeatRecovery):
            print("Model:", component.model)

        if isinstance(component, iesve.HVACPCMBattery):
            print("Number of units:", component.number_of_units)
            print("Attached room ID:", component.attached_room_id)
            print("Model ID:", component.model_id)
            print("Model not found:", component.model_not_found)

        if isinstance(component, iesve.HVACSolarAirCollectorBIST):
            print("Attached room ID:", component.attached_room_id)

        if isinstance(component, iesve.HVACPlenum):
            print("Attached room ID:", component.attached_room_id)

        if isinstance(component, iesve.HVACThermalStorageLoop):
            print("Pump:", component.pump)
            print("Tank:", component.tank)
            print("Chillers:", component.chillers)
            print("Condenser water loop:", component.condenser_water_loop)

    print("-----------------")
    print("Controllers")
    for controller in network.controllers:
        print("\n", controller)
        print("\nIndependent mode:", controller.independent_mode)
        print("Time switch profile ID:", controller.time_switch_profile_id)
        print("Number of AND connections:", controller.number_of_and_connections)
        print("Control line orientation:", controller.control_line_orientation)
        print("Sensor line orientation:", controller.sensor_line_orientation)
        print("Control node:", controller.control_node)
        print("Sensor node:", controller.sensor_node)
        print("Reference node:", controller.reference_node)
        print("Reference line orientation:", controller.reference_line_orientation)
        print("Max control signal value:", controller.max_control_signal_value)
        print("Network:", controller.network)
        print("ID:", controller.id)
        print("Reference:", controller.reference)
        print("System ID:", controller.system_id)
        print("Multiplex ID:", controller.multiplex_id)
        print("Network object type:", controller.network_object_type)
        print("Is selected:", controller.is_selected)
        print("Multiplex layer number:", controller.multiplex_layer_number)
        print("Available system links:", controller.available_system_links)
        print("System link:", controller.system_link)

        if isinstance(controller, iesve.HVACTimeSwitchController):
            print("Max signal variation profile ID:", controller.max_signal_variation_profile_id)
            print("Max signal variation mode:", controller.max_signal_variation_mode)

        if isinstance(controller, iesve.HVACAbstractControllerWithSensor):
            print("Proportional controller ID:", controller.proportional_controller_id)
            print("Set point profile ID:", controller.set_point_profile_id)
            print("Midband point profile ID:", controller.midband_point_profile_id)
            print("On off max signal profile ID:", controller.on_off_max_signal_profile_id)
            print("Prop min signal profile ID:", controller.prop_min_signal_profile_id)
            print("Set point:", controller.set_point)
            print("Deadband:", controller.deadband)
            print("Radiant fraction:", controller.radiant_fraction)
            print("Orientation:", controller.orientation)
            print("Slope:", controller.slope)
            print("Midband:", controller.midband)
            print("Proportional bandwidth:", controller.proportional_bandwidth)
            print("Max change per time step:", controller.max_change_per_time_step)
            print("Min control signal value:", controller.min_control_signal_value)
            print("High sensor input:", controller.high_sensor_input)
            print("Sensed variable:", controller.sensed_variable)
            print("Set point mode:", controller.set_point_mode)
            print("Midband mode:", controller.midband_mode)
            print("Proportional min signal mode:", controller.proportional_min_signal_mode)
            print("On/off max signal mode:", controller.on_off_max_signal_mode)
            print("Is proportional control:", controller.is_proportional_control)
            print("Is active set point:", controller.is_active_set_point)

    print("-----------------")
    print("Generic heat sources")
    for heat_source in network.generic_heat_sources:
        print("\n", heat_source)
        print("\nUse air source heat pump:", heat_source.use_air_source_heat_pump)
        print("Autosize air source heat pump:", heat_source.autosize_air_source_heat_pump)
        print("% of heat source capacity:", heat_source.percentage_of_heat_source_capacity)
        print("Equipment:", heat_source.equipment)

    print("-----------------")
    print("Hot water loop IDs\n")

    for hwl_id in network.hot_water_loop_ids:
        print(hwl_id)

    print("-----------------")
    print("Hot water loops")
    for hwl in network.hot_water_loops:
        print('\nHot Water Loop', hwl)
        print("\nIs duct:", hwl.is_duct)
        print("Inlet nodes:", hwl.inlet_nodes)
        print("Outlet nodes:", hwl.outlet_nodes)
        print("Oversizing Factor:", hwl.oversizing_factor)
        print("Loop configuration (enum):", hwl.loop_configuration)
        print("Pre heating CHR capacity", hwl.pre_heating_chr_capacity)
        print("Pre heating HR WWHP capacity", hwl.pre_heating_hr_wwhp_capacity)
        print("Pre heating AWHP capacity", hwl.pre_heating_awhp_capacity)
        print("Is preheat using solar water heater", hwl.is_pre_heat_using_solar_water_heater)


        print("\nSupply Loop Data")
        supply_loop = hwl.supply_loop # AKA primary supply
        print("\nSupply Loop")
        print("  Flow Rate:", supply_loop.flow_rate)
        print("  Capacity in Watts:", supply_loop.capacity_w)
        print("  Pump power:", supply_loop.pump_power)
        print("  Is distribution branch used for coupling loads:",
                supply_loop.is_distribution_branch_used_for_coupling_loads)


        demand_loop = hwl.demand_loop
        print("\nDemand loop data", demand_loop)
        print("  Capacity:", demand_loop.capacity_w)
        print("  Demand Loop Type:", demand_loop.demand_loop_type)

        print("\nSecondary Loops data")
        for loop in hwl.secondary_loops:
            print("\nSecondary Loop", loop)
            print("  reference:", loop.reference)
            print("  pump power:", loop.pump_power)
            print("  demand loop type:", loop.demand_loop_type)

        swh = hwl.solar_water_heater
        print("\nSolar water heater:", swh)
        print("   Solar water heater panel type:", swh.panel_type)
        print("   Solar water heater is waterside component:", swh.is_waterside_component)
        print("   Solar water heater flat PV data:", swh.flat_solar_panel_data)
        print("   Solar water heater parabolic PV data:", swh.parabolic_solar_panel_data)

        # Boilers Data
        print("\nBoilers data")
        for boiler in hwl.boilers:
            print("\nBoiler", boiler)
            print("  reference all:", boiler.reference_all)
            print("  output capacity all kw", boiler.output_capacity_all_kw)
            print("  is parent equipment", boiler.is_parent_equipment)

            print("Model type:", boiler.model_type)
            print("Distribution losses:", boiler.distribution_losses)
            print("Electrical circulation power:", boiler.electrical_circulation_power)
            print("Number of part load entries:", boiler.number_of_part_load_entries)
            print("Uses CHP:", boiler.uses_chp)
            print("Sequence number:", boiler.sequence_number)
            print("Uses water source CHP:", boiler.uses_water_source_chp)
            print("Is DHW boiler:", boiler.is_dhw_boiler)
            print("Heating plant type:", boiler.heating_plant_type)
            print("Oversizing factor:", boiler.oversizing_factor)
            print("Output capacity sized:", boiler.is_output_capacity_sized)
            print("Output capacity:", boiler.output_capacity)
            print("Primary meter:", boiler.primary_meter)

            if isinstance(boiler, iesve.HVACBoiler):
                print("Part load performance:", boiler.part_load_performance)

            if isinstance(boiler, iesve.HVACEnhancedBoiler):
                print("Parasitic power:", boiler.parasitic_power)
                print("Max parasitic power:", boiler.max_parasitic_power)
                print("Parasitic ratio:", boiler.parasitic_ratio)
                print("Hot water pump power:", boiler.hot_water_pump_power)
                print("Hot water pump factor:", boiler.hot_water_pump_factor)
                print("Is two identical boiler:", boiler.is_two_identical_boiler)
                print("% of combined capacity:", boiler.percentage_of_combined_capacity)
                print("Rated condition data:")
                pp.pprint(boiler.rated_condition)

        print("\nAux Boiler Data")
        aux_boiler = hwl.aux_boiler_data
        if (aux_boiler): # empty dict is falsy.
            print("  Name:", aux_boiler['name'])
            print("  capacity:", aux_boiler['capacity'])

    print("-----------------")
    print("Chilled water loop IDs\n")

    for cwl_id in network.chilled_water_loop_ids:
        print(cwl_id)

    print("-----------------")
    print("Chilled water loops")
    for cwl in network.chilled_water_loops:
        print("\n", cwl)
        print("\nIs duct:", cwl.is_duct)
        print("Inlet nodes:", cwl.inlet_nodes)
        print("Outlet nodes:", cwl.outlet_nodes)
        print("Oversizing factor:", cwl.oversizing_factor)
        print("Distribution loss:", cwl.distribution_loss)
        print("Independent secondary loop enabled:", cwl.independent_secondary_loop_enabled)
        print("Primary chilled water supply temp reset type:", cwl.primary_chilled_water_supply_temp_reset_type)
        print("Primary chilled water supply temperature:", cwl.primary_chilled_water_supply_temperature)
        print("Primary outdoor dry bulb temp low threshold:", cwl.primary_outdoor_dry_bulb_temp_low_threshold)
        print("Primary chilled water demand side load fraction low threshold:", cwl.primary_chilled_water_demand_side_load_fraction_low_threshold)
        print("Primary chilled water supply temp low threshold:", cwl.primary_chilled_water_supply_temp_low_threshold)
        print("Primary chilled water supply temp high threshold:", cwl.primary_chilled_water_supply_temp_high_threshold)
        print("Primary outdoor dry bulb temp high threshold:", cwl.primary_outdoor_dry_bulb_temp_high_threshold)
        print("Primary chilled water demand side load fraction high threshold:", cwl.primary_chilled_water_demand_side_load_fraction_high_threshold)
        print("Primary chilled water temperature difference:", cwl.primary_chilled_water_temperature_difference)
        print("Primary outdoor dew point temp high threshold:", cwl.primary_outdoor_dew_point_temp_high_threshold)
        print("Primary outdoor dew point temp low threshold:", cwl.primary_outdoor_dew_point_temp_low_threshold)
        print("Primary circuit using dedicated chiller pumps:", cwl.primary_circuit_using_dedicated_chiller_pumps)
        print("Secondary chilled water supply temp reset type:", cwl.secondary_chilled_water_supply_temp_reset_type)
        print("Secondary chilled water supply temperature:", cwl.secondary_chilled_water_supply_temperature)
        print("Secondary outdoor dry bulb temp low threshold:", cwl.secondary_outdoor_dry_bulb_temp_low_threshold)
        print("Secondary chilled water demand side load fraction low threshold:", cwl.secondary_chilled_water_demand_side_load_fraction_low_threshold)
        print("Secondary chilled water supply temp low threshold:", cwl.secondary_chilled_water_supply_temp_low_threshold)
        print("Secondary chilled water supply temp high threshold:", cwl.secondary_chilled_water_supply_temp_high_threshold)
        print("Secondary outdoor dry bulb temp high threshold:", cwl.secondary_outdoor_dry_bulb_temp_high_threshold)
        print("Secondary chilled water demand side load fraction high threshold:", cwl.secondary_chilled_water_demand_side_load_fraction_high_threshold)
        print("Secondary chilled water temperature difference:", cwl.secondary_chilled_water_temperature_difference)
        print("Secondary outdoor dew point temp high threshold:", cwl.secondary_outdoor_dew_point_temp_high_threshold)
        print("Secondary outdoor dew point temp low threshold:", cwl.secondary_outdoor_dew_point_temp_low_threshold)
        print("\nThermal storage loop:", cwl.thermal_storage_loop)
        print("Number of cooling chillers:", cwl.get_chiller_count_by_type(iesve.HVACChillerType.CoolingChiller))
        print('Cooling capacity in kW: ', cwl.design_cooling_capacity_kw)
        print('Primary Design Loop Flow Rate in l/s: ', cwl.primary_design_flow_rate)
        print('Primary pump power in W: ', cwl.primary_pump_power_w)
        print('Secondary loop design flow rate in l/s: ', cwl.secondary_loop_design_flow_rate)
        print('Secondary loop design pump power in W: ', cwl.secondary_loop_pump_power_w)
        print('Condenser loop design pump power in W: ', cwl.condenser_loop_design_pump_power_w)

        print("Condenser Loop:", cwl.condenser_water_loop)
        print("Is Condenser water loop Used: ", cwl.is_condenser_water_loop_used)
        if cwl.condenser_water_loop is not None:
            print("Condenser water loop used:", cwl.condenser_water_loop.condenser_water_loop_used)
            print("Condenser water loop design outdoor dry bulb temp:", cwl.condenser_water_loop.design_outdoor_dry_bulb_temp)
            print("Condenser water loop design outdoor wet bulb temp:", cwl.condenser_water_loop.design_outdoor_wet_bulb_temp)
            print("Condenser water loop design condenser water loop supply temp:", cwl.condenser_water_loop.design_condenser_water_loop_supply_temp)
            print("Condenser water loop design condenser entering water temp:", cwl.condenser_water_loop.design_condenser_entering_water_temp)
            print("Condenser water loop design temperature diff:", cwl.condenser_water_loop.design_temperature_diff)
            print("Condenser water loop entering water constant value:", cwl.condenser_water_loop.entering_water_constant_value)
            print("Condenser water loop specific pump power:", cwl.condenser_water_loop.specific_pump_power)
            print("Condenser water loop motor efficiency factor:", cwl.condenser_water_loop.motor_efficiency_factor)
            print("Condenser water loop design condenser water loop flow rate:", cwl.condenser_water_loop.design_condenser_loop_flow_rate)
            print("Cooling tower:", cwl.condenser_water_loop.cooling_tower)

            if cwl.condenser_water_loop.cooling_tower is not None:
                print("Cooling tower design wet bulb temperature:", cwl.condenser_water_loop.cooling_tower.design_wet_bulb_temperature)
                print("Cooling tower design heat rejection:", cwl.condenser_water_loop.cooling_tower.design_heat_rejection)
                print("Cooling tower design flow rate:", cwl.condenser_water_loop.cooling_tower.design_flow_rate)
                print("Cooling tower design approach:", cwl.condenser_water_loop.cooling_tower.design_approach)
                print("Cooling tower design range:", cwl.condenser_water_loop.cooling_tower.design_range)
                print("Cooling tower design supply water temperature:", cwl.condenser_water_loop.cooling_tower.design_supply_water_temperature)
                print("Cooling tower design leaving temperature:", cwl.condenser_water_loop.cooling_tower.design_leaving_temperature)
                print("Cooling tower fan power:", cwl.condenser_water_loop.cooling_tower.fan_power)
                print("Cooling tower fan electric input ratio:", cwl.condenser_water_loop.cooling_tower.fan_electric_input_ratio)
                print("Cooling tower low speed fan flow fraction:", cwl.condenser_water_loop.cooling_tower.low_speed_fan_flow_fraction)
                print("Cooling tower low speed fan power fraction:", cwl.condenser_water_loop.cooling_tower.low_speed_fan_power_fraction)
                print("Cooling tower fan control:", cwl.condenser_water_loop.cooling_tower.fan_control)
                print("Cooling tower specific pump power:", cwl.condenser_water_loop.cooling_tower.specific_pump_power)
                print("Cooling tower pump efficiency:", cwl.condenser_water_loop.cooling_tower.pump_efficiency)
                print("Cooling tower pump heat gain:", cwl.condenser_water_loop.cooling_tower.pump_heat_gain)
                print("Cooling tower pump delta T:", cwl.condenser_water_loop.cooling_tower.pump_delta_t)
                print("Cooling tower HR device autosized:", cwl.condenser_water_loop.cooling_tower.hr_device_autosized)

            print("Dry fluid cooler:", cwl.condenser_water_loop.dry_fluid_cooler)

            if cwl.condenser_water_loop.dry_fluid_cooler is not None:
                print("Dry fluid design wet bulb temperature:", cwl.condenser_water_loop.dry_fluid_cooler.design_wet_bulb_temperature)
                print("Dry fluid design heat rejection:", cwl.condenser_water_loop.dry_fluid_cooler.design_heat_rejection)
                print("Dry fluid design flow rate:", cwl.condenser_water_loop.dry_fluid_cooler.design_flow_rate)
                print("Dry fluid design approach:", cwl.condenser_water_loop.dry_fluid_cooler.design_approach)
                print("Dry fluid design range:", cwl.condenser_water_loop.dry_fluid_cooler.design_range)
                print("Dry fluid design supply water temperature:", cwl.condenser_water_loop.dry_fluid_cooler.design_supply_water_temperature)
                print("Dry fluid design leaving temperature:", cwl.condenser_water_loop.dry_fluid_cooler.design_leaving_temperature)
                print("Dry fluid fan power:", cwl.condenser_water_loop.dry_fluid_cooler.fan_power)
                print("Dry fluid fan electric input ratio:", cwl.condenser_water_loop.dry_fluid_cooler.fan_electric_input_ratio)
                print("Dry fluid low speed fan flow fraction:", cwl.condenser_water_loop.dry_fluid_cooler.low_speed_fan_flow_fraction)
                print("Dry fluid low speed fan power fraction:", cwl.condenser_water_loop.dry_fluid_cooler.low_speed_fan_power_fraction)
                print("Dry fluid fan control:", cwl.condenser_water_loop.dry_fluid_cooler.fan_control)
                print("Dry fluid specific pump power:", cwl.condenser_water_loop.dry_fluid_cooler.specific_pump_power)
                print("Dry fluid pump efficiency:", cwl.condenser_water_loop.dry_fluid_cooler.pump_efficiency)
                print("Dry fluid pump heat gain:", cwl.condenser_water_loop.dry_fluid_cooler.pump_heat_gain)
                print("Dry fluid pump delta T:", cwl.condenser_water_loop.dry_fluid_cooler.pump_delta_t)
                print("Dry fluid HR device autosized:", cwl.condenser_water_loop.dry_fluid_cooler.hr_device_autosized)
                print("Dry fluid design dry bulb temperature:", cwl.condenser_water_loop.dry_fluid_cooler.design_dry_bulb_temperature)
                print("Dry fluid cooler mode:", cwl.condenser_water_loop.dry_fluid_cooler.fluid_cooler_mode)
                print("Dry fluid switch temperature:", cwl.condenser_water_loop.dry_fluid_cooler.switch_temperature)
                print("Dry fluid design wet bulb delta T:", cwl.condenser_water_loop.dry_fluid_cooler.design_wet_bulb_delta_t)
                print("Dry fluid spray pump power:", cwl.condenser_water_loop.dry_fluid_cooler.spray_pump_power)
                print("Dry fluid spray pump electric input ratio:", cwl.condenser_water_loop.dry_fluid_cooler.spray_pump_electric_input_ratio)

        print("\nChillers:")
        for chiller in cwl.chillers:
            print("\n", chiller)
            print("Name: " , chiller.reference)
            print("\nChiller type:", chiller.chiller_type)
            print("Output capacity:", chiller.output_capacity)
            print("Is output capacity sized:", chiller.is_output_capacity_sized)
            print("Is parent equipment: ", chiller.is_parent_equipment)
            print("Output capacity all: ", chiller.output_capacity_all_kw)

            if isinstance(chiller, iesve.HVACElectricChiller):
                print("Curve type names:", chiller.curve_type_names)
                print("COP:", chiller.cop)
                print("Min part load ratio:", chiller.min_part_load_ratio)
                print("Compressor heat gain to condenser loop:", chiller.compressor_heat_gain_to_condenser_loop)

            if isinstance(chiller, iesve.HVACEACChiller):
                print("Condenser fan power:", chiller.condenser_fan_power)
                print("Condenser fan EIR:", chiller.condenser_fan_eir)
                print("Is outdoor dry bulb temperature autosized:", chiller.is_outdoor_dry_bulb_temperature_autosized)

            if isinstance(chiller, iesve.HVACPLCChiller):
                print("Is absorption chiller:", chiller.is_absorption_chiller)
                print("Is CHR recipient set:", chiller.is_chr_recipient_set)
                print("Condenser water pump power:", chiller.condenser_water_pump_power)
                print("Cooling tower fan power:", chiller.cooling_tower_fan_power)
                print("Chiller pumps power:", chiller.chiller_pumps_power)
                print("Deprecated CHR %:", chiller.deprecated_chr_percentage)
                print("Outside temp for COP data:", chiller.outside_temp_for_cop_data)
                print("Number of temperature dependent COPs:", chiller.number_of_temperature_dependent_cops)
                print("Number of part load entries:", chiller.number_of_part_load_entries)
                print("Heat source ID:", chiller.heat_source_id)
                print("CHR recipient ID:", chiller.chr_recipient_id)

        pcl = cwl.pre_cooling_loop # HVACPreCoolingLoop
        print('\nPre Cooling Loop: ', pcl)
        print('Pre cooling loop is used: ', pcl.is_used)
        print('Capacity in kW: ', pcl.capacity)

        print("\nThermal Storage Loop")
        print("Is thermal storage loop used", cwl.is_thermal_storage_loop_used)
        if (cwl.is_thermal_storage_loop_used):
            print("Thermal storage loop", cwl.thermal_storage_loop)
            print("TSL Chillers", cwl.thermal_storage_loop.chillers)

        cooling_towers = cwl.cooling_towers
        print("\nCooling Towers: ", cooling_towers)
        for tower in cooling_towers:
            print("\nTower: ", tower)
            print("Name", tower.reference)
            print("Capacity", tower.design_heat_rejection)

        dry_fluid_coolers = cwl.dry_fluid_coolers
        print("\nDry Fluid Coolers: ", dry_fluid_coolers)
        for dfc in dry_fluid_coolers:
            print("\nDry fluid cooler: ", dfc)
            print("Name", dfc.reference)
            print("Capacity", dfc.design_heat_rejection)