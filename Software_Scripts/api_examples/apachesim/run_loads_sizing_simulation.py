""""
This sample shows how to run Loads and Sizing simulations
"""

import iesve        # the VE api

sim = iesve.ApacheSim()
sim.set_hvac_network('proposed.asp') # Change this to the name of your HVAC network
sim.run_loads_sizing()
