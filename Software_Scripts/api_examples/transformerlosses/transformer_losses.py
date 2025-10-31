""""
This sample demonstrates how to access the custom bpf data.
"""

import iesve

def main_script():

    transformer_losses = iesve.TransformerLosses()
    print("Transformer Losses Methods:")
    print("    get_efficiency():        ", transformer_losses.get_efficiency())
    print("    get_adjustment_factor(): ", transformer_losses.get_adjustment_factor())
    print("    is_set():                ", transformer_losses.is_set())

    # Methods can be chained on constructor if access to only one variable is required.
    print("    direct access is_set:    ", iesve.TransformerLosses().is_set())


if __name__ == "__main__":
    main_script()