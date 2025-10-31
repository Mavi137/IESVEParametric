""""
This sample sets room internal gains data
"""

import iesve    # the VE api
import pprint
   
project = iesve.VEProject.get_current_project()

for model in project.models:
    # get all the bodies in the building
    bodies = model.get_bodies(False)
    for body in bodies:
        # skip any bodies that aren't thermal rooms
        if body.type != iesve.VEBody_type.room:
            continue
            
        energy_source_data = iesve.EnergySources.get_all_energy_source_data()[0]
        meter = energy_source_data["meters"][0]
            
        if model.model_type == iesve.VEModels.RealBuilding:
            # the Real building stores generic data
            # so ask for generic room data
            room_data = body.get_room_data(iesve.attribute_type.real_attributes)
            
            data_to_set = { 'allow_profile_saturate': True,
                            'allow_profile_saturate_from_template': False,
                            'ballast': 0.6,
                            'ballast_from_template': False,
                            'dimming_profile': 'ON',
                            'dimming_profile_from_template': False,
                            'diversity_factor': 1.0,
                            'diversity_factor_from_template': False,
                            'energy_meter': meter,
                            'energy_source': iesve.fuel_type.elec,
                            'energy_source_from_template': False,
                            'max_illuminance': 101.0,
                            'installed_power_density': 100.0,
                            'is_ncm_simple_lighting_control': False,
                            'is_non_regulated_load': True,
                            'is_non_regulated_load_from_template': False,
                            'max_latent_gain': 100.0,
                            'max_latent_gain_from_template': False,
                            'max_power_consumption': 100.0,
                            'max_sensible_gain': 100.0,
                            'max_sensible_gain_from_template': False,
                            'occupancy_density': 100.0,
                            'number_of_people': 100,
                            'radiant_fraction': 0.5,
                            'radiant_fraction_from_template': False,
                            'units_val': 0,
                            'units_val_from_template': False,
                            'variation_profile': 'OFF',
                            'variation_profile_from_template': False}
        else:
            # Skip other models for this example
            continue

        internal_gains = room_data.get_internal_gains()
        
        for gain in internal_gains:
            gain.set(data_to_set)
            
        ncm_room_data = body.get_room_data(iesve.attribute_type.ncm_attributes)
        ncm_gains = ncm_room_data.get_internal_gains()
        
        for ncm_gain in ncm_gains:
            # Set for NCM
            if not type(ncm_gain) == iesve.RoomLightingGain:
                continue
            
            ncm_data_to_set = { 'allow_profile_saturate': True,
                                'allow_profile_saturate_from_template': False,
                                'ballast': 0.5,
                                'ballast_from_template': False,
                                'dimming_profile': 'ON',
                                'dimming_profile_from_template': False,
                                'diversity_factor': 1.0,
                                'diversity_factor_from_template': False,
                                'energy_meter': meter,
                                'energy_source': iesve.fuel_type.elec,
                                'energy_source_from_template': False,
                                'lamp_efficacy': 3.1,
                                'lamp_type': iesve.LampType.fluorescent_compact,
                                'light_output_ratio': 1.0,
                                'max_illuminance': 101.0,
                                'installed_power_density': 100.0,
                                'is_ncm_simple_lighting_control': False,
                                'is_non_regulated_load': True,
                                'is_non_regulated_load_from_template': False,
                                'max_latent_gain': 100.0,
                                'max_latent_gain_from_template': False,
                                'max_power_consumption': 100.0,
                                'max_sensible_gain': 100.0,
                                'max_sensible_gain_from_template': False,
                                'occupancy_density': 100.0,
                                'number_of_people': 100,
                                'radiant_fraction': 0.5,
                                'radiant_fraction_from_template': False,
                                'units_val': 3,
                                'units_val_from_template': False,
                                'variation_profile': 'OFF',
                                'variation_profile_from_template': False}
                                
            ncm_gain.set(ncm_data_to_set)