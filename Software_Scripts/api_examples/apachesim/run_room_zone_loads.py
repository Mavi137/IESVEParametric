""""
This sample shows how to run a Room and HVAC Zone loads simulation
"""

import iesve        # the VE api

sim = iesve.ApacheSim()
sim.set_hvac_network('proposed.asp') # Change this to the name of your HVAC network
sim.run_room_zone_loads()
