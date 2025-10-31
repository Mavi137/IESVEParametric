""""
This sample shows how to get and set data for the reference model user edits dialog
"""

import iesve
import pprint
pp = pprint.PrettyPrinter(indent=4)

ref_model_user_edits = iesve.RefModelUserEdits()

# Read
pp.pprint(ref_model_user_edits.get())

# Write
ref_model_user_edits_data = {
    'geometry': 'notes on geometry changes',
    'spaces': 'notes on spaces changes',
    'envelope': 'notes on envelope changes',
    'interior_lighting': 'notes on interior lighting changes',
    'hvac_systems': 'notes on hvac systems changes',
    'service_hot_water': 'notes on service hot water changes',
    'miscellaneous': 'notes on other miscellaneous changes'
    }

ref_model_user_edits.set(ref_model_user_edits_data)