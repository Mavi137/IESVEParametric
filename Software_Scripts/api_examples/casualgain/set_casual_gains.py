""""
This sample demonstrates setting casual gains data
CAUTION: This script will modify your model data
"""

import iesve   # the VE api

# main code starts here
if __name__ == '__main__':
    # we will get the list of defined internal gain objects
    # in order to do this, we start with the currently loaded VE project
    project = iesve.VEProject.get_current_project()

    # Get list of casual gain objects from the project:
    casual_gains = project.casual_gains()

    # Print details of each of the casual gains:
    i = 0
    for casual_gain in casual_gains:
        if not casual_gain.is_ncm():
            name = "Python Sample Gain " + str(i)
            energy_source_data = iesve.EnergySources.get_all_energy_source_data()[0]
            meter = energy_source_data["meters"][0]
            gains_data = { "name": name,
                           "variation_profile": "ON",
                           "diversity_factor": 1.0,
                           "max_sensible_gain": 1.0,
                           "units_val": 0,
                           "type_val": iesve.CasualGain_type.general_lighting,
                           "radiant_fraction": 1.0,
                           "max_power_consumption": 10.0,
                           "max_latent_gain": 10.0,
                           "energy_source": iesve.fuel_type.elec,
                           "energy_meter": meter,
                           "occupancy_density": 10.0,
                           "number_of_people": 10,
                           "installed_power_density": 10.0,
                           "min_illuminance": 10.0,
                           "max_illuminance": 20.0,
                           "dimming_profile": "ON",
                           "ballast": 1.0,
                           "pc_convective_gain": 100.0,
                           "allow_profile_saturate": True,
                           "is_non_regulated_load": True
                           }
                           
            casual_gain.set(gains_data)
            i = i + 1