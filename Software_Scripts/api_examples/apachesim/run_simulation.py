""""
This sample shows how to run Apache simulations 
with control over various settings

"""

import iesve        # the VE api
import pprint
import time

sim = iesve.ApacheSim()
pp = pprint.PrettyPrinter()

# Get and print the current options
opt = sim.get_options()
pp.pprint(opt)

# Set batch_operation to True to queue up simulations with Tasks scheduler (Beta).
# Note: when using Task Scheduler, the simulation job is queued and script
# execution continues immediately.  This means that result files cannot be 
# automatically post-processed, as you don't know when they will be completed
# With batch_operation set to False, simulation will block further script
# execution, and only continue once the simulation is complete.
batch_operation = False

# If you want to invoke the Apache Simulations options dialog (to run manually)
# uncomment the lines below.  Script will halt until the dialog is closed
# if sim.show_simulation_dialog() == False:
#     print("Simulation was not run from dialog (user cancelled?)")

# Run a simulation with basic settings:
sim.reset_options()
sim.set_options({'results_filename': 'defaults.aps'})
result = sim.run_simulation(batch_operation)
print('Simulation 1 run success: {}'.format(result))

# Give apache time to release its resources before starting next sim...
time.sleep(2)

# Run a simulation with some custom settings
# Timesteps for simulation can be the following values:
#   0=1 minute, 1=2 minutes, 2=6, 3=10, 4=30 minutes
# Reporting interval can be the following values:
#   0=6 minutes, 1=10 minutes, 2=30, 3=60 minutes
# Note that you are not allowed to set incompatible 
# simulation and reporting combinations!
# Doing so will cause an exception to be thrown
# Note that setting Suncast and Radiance to True will 
# only auto-run suncast when using batch operation
# When using the blocking run, suncast and radiance
# will not be automatically run when set to True, but
# if their data files are available (shd and ill files)
# they will be used in simulation.
sim.reset_options()
sim.set_options(results_filename='detailed.aps', suncast=True, radiance=True)
sim.set_options({'detailed_rooms': ['RM000000']})
sim.set_options({'simulation_timestep': iesve.time_step.ten_minutes, 'reporting_interval': iesve.reporting_interval.thirty_minutes})
result = sim.run_simulation(batch_operation)
print('Simulation 2 run success: {}'.format(result))

# Give apache time to release its resources before starting next sim...
time.sleep(2)

# Run a simulation for December only:
sim.set_options({'results_filename': 'december.aps', 'start_day': 1, 'start_month': 12})
result = sim.run_simulation(batch_operation)
print('Simulation 3 run success: {}'.format(result))

# Some error conditions - all of these will cause an exception to be thrown,
# which will stop the script from running:
# sim.set_options({'are': 'adf', 'start_day': 'abc', 'start_month': 12})
# sim.set_options({'start_day': 'abc', 'start_month': 12 })
# sim.set_options({'start_month': 18 })
# sim.set_options({'detailed_rooms': ['room1', 'room2']})
# sim.set_options({'simulation_timestep': 4, 'reporting_interval': 1})
