""""
This sample demonstrates setting the building orientation
"""

import iesve    # the VE api

geom = iesve.VEGeometry

# Set the building orientation to 90 degrees from north
geom.set_building_orientation(90.0)

print(geom.get_building_orientation())