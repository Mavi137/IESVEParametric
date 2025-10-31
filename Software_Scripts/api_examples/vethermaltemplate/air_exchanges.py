import iesve

def main():
    proj = iesve.VEProject.get_current_project()

    def print_ax(ax: iesve.AirExchange):
        print()
        print(ax)
        print(f"name: {ax.name}")
        print(f"air_change_unit: {ax.air_change_unit}")
        print(f"exchange_type: {ax.exchange_type}")
        print(f"adjacent_condition: {ax.adjacent_condition}")
        print(f"variation_profile_id: {ax.variation_profile_id}")
        print(f"max_flow: {ax.max_flow}")
        print(f"offset_temperature: {ax.offset_temperature}")
        print(f"temperature_profile_id: {ax.temperature_profile_id}")

    ax = proj.create_air_exchange(iesve.AirExchange_type.infiltration)
    print_ax(ax)

    ax.name = "New Air Exchange"
    ax.air_change_unit = iesve.AirChange_unit.l_per_s
    ax.exchange_type = iesve.AirExchange_type.mechanical_ventilation
    ax.adjacent_condition = iesve.AdjacentCondition_type.external_air_and_offset_temp
    ax.variation_profile_id = "OFF" # This ID is not validated so could be set to invalid ID.
    ax.max_flow = 0
    ax.offset_temperature = -50
    ax.temperature_profile_id = "OFF" # This ID is not validated so could be set to invalid ID.

    print_ax(ax)
    ax_dict = ax.get()
    print(ax_dict)
    ax_dict['type_val'] = iesve.AirExchange_type.natural_ventilation
    ax_dict['type_str'] = "type_val will not set"
    ax_dict['variation_profile'] = "OFF" # This ID is not validated so could be set to invalid ID.
    ax_dict['name'] = "name dict set"
    ax_dict['max_flow'] = 20000
    ax_dict['units_val'] = iesve.AirChange_unit.l_per_s_per_person
    ax_dict['units_str'] = "units_str will not set"
    ax_dict['adjacent_condition_val'] = iesve.AdjacentCondition_type.from_adjacent_room
    ax_dict['adjacent_condition_string'] = "will not set"
    ax_dict['offset_temperature'] = 50
    ax_dict['temperature_profile'] = "OFF"
    ax.set(ax_dict)

    print(ax.get())

    # Modification of room air exchanges
    for body in proj.models[0].get_bodies(False):
        room_data = body.get_room_data()

        def print_rax(rax: iesve.RoomAirExchange, msg:str=""):
            print()
            print(msg)
            print(rax)
            print(f"exchange type: {rax.exchange_type}")
            print(f"air_change_rate_from_template: {rax.air_change_rate_from_template}")
            print(f"max_flow: {rax.max_flow}")
            print(f"air_change_unit: {rax.air_change_unit}")
            print(f"air_change_rate_from_template: {rax.air_change_rate_from_template}")
            print(f"variation_profile_id: {rax.variation_profile_id}")
            print(f"variation_profile_id_from_template: {rax.variation_profile_id_from_template}")
            print(f"adjacent_condition: {rax.adjacent_condition}")
            print(f"adjacent_condition_from_template: {rax.adjacent_condition_from_template}")
            print(f"offset_temperature: {rax.offset_temperature}")
            print(f"offset_temperature_from_template: {rax.offset_temperature_from_template}")
            print(f"temperature_profile_id: {rax.temperature_profile_id}")
            print(f"temperature_profile_id_from_template: {rax.temperature_profile_id_from_template}")

        for rax in room_data.get_air_exchanges():
            print_rax(rax, "===Before===")

            # will change corresponding template uses to false.
            rax.air_change_unit = iesve.AirChange_unit.l_per_s_per_m2
            rax.max_flow = 0
            rax.variation_profile_id = "OFF" # This ID is not validated so could be set to invalid ID.
            rax.adjacent_condition = iesve.AdjacentCondition_type.external_air_and_offset_temp
            rax.offset_temperature = -50
            rax.temperature_profile_id = "OFF" # This ID is not validated so could be set to invalid ID.
            print_rax(rax, "===After Edit===")

            # below will reset corresponding value to template's value
            rax.air_change_rate_from_template = True
            rax.variation_profile_id_from_template = True
            rax.adjacent_condition_from_template = True
            rax.offset_temperature_from_template = True
            rax.temperature_profile_id_from_template = True
            print_rax(rax, "===After Default Set===")

            rax_dict = rax.get()

            print("===Setting Using Dictionary===")
            print(rax_dict)
            rax_dict['type_val'] = iesve.AirExchange_type.natural_ventilation # ignored
            rax_dict['type_str'] = "type_val will not set"

            rax_dict['variation_profile'] = "OFF" # This ID is not validated so could be set to invalid ID.
            rax_dict['variation_profile_from_template'] = False

            rax_dict['name'] = "name dict will set"

            rax_dict['max_flow'] = 50
            rax_dict['units_val'] = iesve.AirChange_unit.l_per_s_per_m2
            rax_dict['units_strs'] = "units_str will not set"
            rax_dict['max_flow_from_template'] = False

            rax_dict['adjacent_condition_val'] = iesve.AdjacentCondition_type.from_adjacent_room
            rax_dict['adjacent_condition_string'] = "will not set"
            rax_dict['adjacent_condition_val_from_template'] = False

            rax_dict['offset_temperature'] = 50
            rax_dict['offset_temperature_from_template'] = False

            rax_dict['temperature_profile'] = "OFF" # This ID is not validated so could be set to invalid ID.
            rax_dict['temperature_profile_from_template'] = False

            rax.set(rax_dict)
            rax_dict = rax.get()
            print(rax_dict)
            rax_dict['max_flow_from_template'] = True
            rax_dict['variation_profile_from_template'] = True
            rax_dict['offset_temperature_from_template'] = True
            rax_dict['adjacent_condition_val_from_template'] = True
            rax_dict['temperature_profile_from_template'] = True
            rax.set(rax_dict)
            print(rax.get())


            break

        break
    return

if __name__== "__main__":
    main()