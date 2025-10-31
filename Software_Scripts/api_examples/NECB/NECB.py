""""
This sample shows how to get and set NECB project details
"""

import iesve # the VE api
import pprint
pp = pprint.PrettyPrinter(indent=4)

ies_necb = iesve.NECB()

ies_necb.set_site_permit_software({'address_1': 'IES',
    'address_2': '834 Inman Village Parkway NE, Suite 240',
    'city': 'Atlanta',
    'permit_date': '1/3/2018',
    'permit_no': '1',
    'program_1': 'VE',
    'program_2': 'Virtual Environment',
    'state': 'Georgia',
    'title': 'Dr',
    'zip_code': '30307'})

ies_necb.set_owner_agent({'address_1': '834 Inman Village Parkway NE',
    'address_2': 'Suite 240',
    'city': 'Atlanta',
    'company': 'Integrated Environmental Solutions',
    'email': 'consulting@iesve.com',
    'first_name': 'John',
    'last_name': 'Doe',
    'phone_number': '+1 (404) 806 2018',
    'state': 'Georgia',
    'zip_code': '30307'})

ies_necb.set_designer_contractor({'address_1': '834 Inman Village Parkway NE',
    'address_2': 'Suite 240',
    'city': 'Atlanta',
    'company': 'Integrated Environmental Solutions',
    'email': 'consulting@iesve.com',
    'first_name': 'Jane',
    'last_name': 'Doe',
    'phone_number': '+1 (404) 806 2018',
    'state': 'Georgia',
    'zip_code': '30307'})

print("Site / Permit / Software:\n")
pp.pprint(ies_necb.get_site_permit_software())
print("\nOwner / Agent:\n")
pp.pprint(ies_necb.get_owner_agent())
print("\nDesigner / Contractor:\n")
pp.pprint(ies_necb.get_designer_contractor())
