

import pint
# 'import iesve' is conditionally called within '__get_display_units()'

class UnitsVE:
    """
    Converts and displays values and units used in calculations and reportage.

        Please add tests to scripts/tests/test_units_ve.py, if any changes are made.

        Version 1.0 (Update this when making changes)
    """

    def __init__(self, display_units='auto'):
        """Initializes class.

        Args:
            display_units (str): The value of the quantity. User can pass in get display
                                units iesve.VEProject.get_display_units()
        """

        self.u = pint.UnitRegistry()
        self.Q_ = self.u.Quantity
        self.ctx = self.__init_context()
        self.__define_custom_units()

        units_data = self.__get_units_data()

        if display_units=='auto':
            self.is_display_metric = self.__get_ve_display_units()
        elif display_units=='metric':
            self.is_display_metric = True
        else:
            self.is_display_metric = False
            #  Only accounts for metric or imperial units

        # Initializing dictionaries for lookups
        self.metric_to_ip_conv = {x[1]:x[2] for x in units_data}
        self.name_to_metric_dict = {x[0]:x[1] for x in units_data}
        self.ip_to_metric_conv = {v:k for k,v in self.metric_to_ip_conv.items()}
        self.metric_display = {x[1]:x[3] for x in units_data}
        self.ip_display = {x[2]:x[4] for x in units_data}

        self.__fix_unit_disparities()
        self.all_display = self.metric_display.copy()
        self.all_display.update(self.ip_display) # could use dictionary unpacking in py >3.5

    def __get_units_data(self):
        """Converts a value from one unit to another.
        Args:
        Returns:
            tuple[tuple]: Units name, symbols, and display
        """
        # Note Δ°F is not recognized by pint string comprehension. Omit Δ and pint will infer the delta.
        # Due to logical inconsistency in converting between metric and IP, there is not a procedural conversion of units.
        # For conversions to be used in 'auto' functions they have to be defined within this array.
        degC = self.get_short_units(self.Q_('celsius'))
        degF = self.get_short_units(self.Q_('fahrenheit'))
        if pint.__version__ == '0.7.1':
            ip_uval = self.get_short_units(self.Q_('Btu / ft ** 2 / hr / delta_degF'))
        else:
            ip_uval = 'Btu / ft ** 2 / hr / delta_degF'

        return (
          # ('name',        'metric_pint',          'ip_pint',                  'metric_display',       'ip_display'),
            ('weight',      'kg',                   'lb',               'kg',                   'lb'),

            ('length_sm',   'mm',                   'in',               'mm',                   'in'),
            ('length_md',   'm',                    'ft',               'm',                    'ft'),
            ('length_lrg',  'km',                   'mi',               'km',                   'mi'),

            ('area_sml',    'mm ** 2',              'in ** 2',          'mm\u00B2',             'in\u00B2'),
            ('area_med',    'm ** 2',               'ft ** 2',          'm\u00B2',              'ft\u00B2'),
            ('area_lrg',    'km ** 2',              'mi ** 2',          'km\u00B2',             'mi\u00B2'),

            ('volume_sml',    'mm ** 3',            'in ** 3',          'mm\u00B3',             'in\u00B3'),
            ('volume_med',   'm ** 3',              'ft ** 3',          'm\u00B3',              'ft\u00B3'),

            ('power_sml',     'W',                  'Btu / hr',         'W',                    'Btu/h'),
            ('power_med',    'kW',                  'kBtu / hr',        'kW',                   'kBtu/h'),
            ('power_lrg',    'MW',                  'MBtu / hr',        'MW',                   'MBtu/h'),

            ('energy_sml',    'Wh',                 'Btu',              'Wh',                   'Btu'),
            ('energy_med',   'kWh',                 'kBtu',             'kWh',                  'kBtu'),
            ('energy_lrg',   'MWh',                 'MBtu',             'MWh',                  'MBtu'),

            ('energy_yr_med', 'kWh / a',            'kBtu / a',         'kWh/yr',               'kBtu/yr'),

            ('power_density','W / m ** 2',          'W / ft ** 2',      'W/m\u00B2',            'W/ft\u00B2'),
            ('power_length', 'W / m',               'W / ft',           'W/m',                  'W/ft'),

            ('temp',         degC,                  degF,               '\u00B0C',              '\u00B0F'), # °F  °C
            ('u_val',        'W / K / m ** 2',      ip_uval,            'W/m\u00B2\u00B7K',     'Btu/h\u00B7ft\u00B2\u00B7\u00B0F'), # W/m².K # Btu/h·ft²·°F # delta_degF
            ('airflow',      'l / m ** 2 / s',      'ft / min',         'l/s\u00B7m\u00B2',     'cfm/ft\u00B2'),

            ('cef',          'kgCO2 / kWh',        'lbCO2 / kBtu',     'kgCO2/kWh',            'lbCO2/kBtu'),
            ('energy_intensity_yr', 'kWh / a / m ** 2',    'kBtu / a / ft ** 2',    'kWh/m².year',   'kBtu/ft².year'),
            ('carbon_intensity_yr', 'kgCO2 / a / m ** 2',  'lbCO2 / a / ft ** 2',   'kgCO2/m².year', 'lbCO2/ft².year'),
        )

    def __define_custom_units(self):
        self.u.define('kgCO2 = kg')
        self.u.define('lbCO2 = lb')

    def __init_context(self):
        """Creates a pint context, replacing default Btu with value used in VE.
            0.7.1 default Btu matches VE, newer version of Pint do not.

        Args:
        Returns:
            Pint.Context: The pint context
        """
        ctx = pint.Context('ve')

        if pint.__version__ != '0.7.1': # Context definition arrived in 0.10
            ctx.redefine('BTU = international_british_thermal_unit')
            ctx.redefine('Btu = international_british_thermal_unit')
        return ctx

    def __fix_unit_disparities(self):
        """Resolves disparities between Pint's short unit display and its str comprehension.

        Args: None
        Returns: Void
        """
        if pint.__version__ != '0.7.1':
            self.ip_display[self.get_short_units(self.Q_('Btu / ft ** 2 / hr / delta_degF'))] = self.ip_display.pop('Btu / ft ** 2 / hr / delta_degF')
        else:
            self.u.define('yr = year = a') # Not defined in 0.7.1

    def __get_ve_display_units(self):
        import iesve
        return str(iesve.VEProject.get_current_project().get_display_units()) == 'metric'

    def ve_round(self, value, decimals=None):
        """ Rounds value to chosen decimal places. 0 will return int

        Args:
            value (Number): The number to be rounded
            decimal_places (int, optional): The number of decimal places. Default=None
        Returns:
            Number: Rounded or Unrounded Value
        """
        if decimals is None:
            return value
        elif decimals == 0:
            return int(round(value, 0))
        else:
            return round(value, decimals)

    def convert_quantity(self, pint_obj, to_unit):
        """Converts a quantity from one quantity another quantity.

        Args:
            pint_obj (Pint.Quantity): The value of the quantity.
            to_unit (str): The unit to convert to.
        Returns:
            Pint.Quantity: The converted Quantity
        """
        return pint_obj.to(to_unit, self.ctx)

    def convert_to_quantity(self, value, from_unit, to_unit):
        """Converts a value from one unit to another as quantity.

        Args:
            value (Number): The value of the quantity.
            from_unit (str): The current unit.
            to_unit (str): The unit to convert to.
        Returns:
            Pint.Quantity: The converted Quantity
        """
        return self.convert_quantity(self.Q_(value, from_unit), to_unit)

    def convert(self, value, from_unit, to_unit, decimals=None):
        """Converts a value from one unit to another.

        Args:
            value (Number): The value of the quantity.
            from_unit (str): The current unit.
            to_unit (str): The unit to convert to.
            decimal_places (int, optional): The number of decimal places. Default=None
        Returns:
            Number: The converted value
        """
        return self.ve_round(self.convert_to_quantity(value, from_unit, to_unit).magnitude, decimals)

    def get_conversion_factor(self, from_unit, to_unit):
        """Calculates conversion factor between compatible units

        Args:
            from_unit (str): The current unit
            to_unit (str): The unit to convert to
        Returns:
            Number: The conversion factor.
        """
        return self.convert_to_quantity(1, from_unit, to_unit).magnitude

    def convert_quantity_auto(self, value, from_unit):
        """Auto converts a value from one unit to default units.

        Args:
            value (Number): The value of the quantity.
            from_unit (str): The current unit.
            to_unit (str): The unit to convert to.
        Returns:
            Pint.Quantity: The converted value
        """
        if self.is_display_metric:
            return self.Q_(value, from_unit)
        else:
            quantity = self.Q_(value, from_unit)
            units = self.metric_to_ip_conv[self.get_short_units(quantity)]
            return self.convert_quantity(quantity, units)

    def convert_auto(self, value, from_unit, decimals=None):
        """Converts a value from metric to imperial if the display units require it.

        Args:
            value (Number): The value of the quantity.
            from_unit (str): The current unit.
            decimal_places (int, optional): The number of decimal places. Default=None
        Returns:
            Number: The value converted value if imperial display, or value untouched
                    if metric.
        """
        value = self.convert_quantity_auto(value, from_unit).magnitude
        return self.ve_round(value, decimals)

    def convert_auto_str(self, value, from_unit, decimals=0):
        """Converts a value from metric to imperial if the display units require it.

        Args:
            value (Number): The value of the quantity.
            from_unit (str): The current unit.
            decimal_places (int, optional): The number of decimal places. Default=0

        Returns:
            str: The value converted value if imperial display, or value untouched
                    if metric.
        """
        value = self.convert_quantity_auto(value, from_unit).magnitude
        return "{:,.{}f}".format(value, decimals)

    def convert_pretty(self, value, from_unit, to_unit, decimal_places=0):
        """Converts a value from one unit to another and displays pretty string.

        Args:
            value (Number): The value of the quantity
            from_unit (str): The current unit
            to_unit (str): The unit to convert to
            decimal_places (int, optional): The number of decimal places. Default=0
        Returns:
            str: Pretty formatted string with units.
        """
        return self.pint_ve_pretty(self.convert_to_quantity(value, from_unit, to_unit), decimal_places)

    def convert_pretty_auto(self, value, from_unit, decimal_places=0):
        """Auto Converts a value from one unit to another and displays pretty string.
            Conversion requires it to be defined in array.

        Args:
            value (Number): The value of the quantity
            from_unit (str): The current unit
            decimal_places (int): The amount of decimal places
        Returns:
            str: Pretty formatted string with units.
        """
        return self.pint_ve_pretty(self.convert_quantity_auto(value, from_unit), decimal_places)

    def pretty_auto_units(self, from_unit):
        """ Auto display of units to another and displays pretty string.
            Conversion requires it to be defined in array.

        Args:
            from_unit (str): The current unit
        Returns:
            str: Pretty formatted string of units.
        """
        return self.pint_ve_pretty_units(self.convert_quantity_auto(1, from_unit))

    def pint_ve_pretty(self, pint_obj, decimal_places=0):
        """Creates pretty formatted string of value and units for Pint Quantity.

        Args:
            pint_obj (Pint.Quantity): Pint Quantity.
            decimal_places (Number): Number of decimal places
        Returns:
            str: Formatted string of value and units.
        """
        f_str = '{:.'+ str(decimal_places) + 'f} {}'
        units = self.pint_ve_pretty_units(pint_obj)
        return f_str.format(pint_obj.magnitude, units)

    def pint_ve_pretty_units(self, pint_obj):
        """Creates pretty formatted string of only units for Pint Quantity.

        Args:
            pint_obj (Pint.Quantity): Pint Quantity
        Returns:
            str: Formatted string of units only.
        """
        return self.all_display.get('{:~}'.format(pint_obj.units), '{:~P}'.format(pint_obj.units))

    def convert_auto_named(self, value, from_unit_name, decimals=None):
        """Auto Converts a value from one named unit to another and displays pretty string.
            Conversion requires it to be defined in array.

        Args:
            value (Number): The value of the quantity.
            from_unit (str): The unit name in table
            decimal_places (int, optional): The number of decimal places. Default=None
        Returns:
            str: Pretty formatted string of units.
        """
        return self.convert_auto(value, self.name_to_metric_dict[from_unit_name], decimals)

    def convert_pretty_auto_named(self, value, from_unit_name, decimal_places=0):
        """Auto Converts a value from one named unit to another and displays pretty string.
            Conversion requires it to be defined in array.

        Args:
            from_unit (str): The unit name in table
            decimal_places (int): The amount of decimal places
        Returns:
            str: Pretty formatted string of units.
        """
        return self.convert_pretty_auto(value, self.name_to_metric_dict[from_unit_name], decimal_places)

    def pretty_auto_units_named(self, from_unit_name):
        """ Auto display of units to another and displays pretty string.
            Conversion requires it to be defined in array.

        Args:
            from_unit (str): The unit name in table
        Returns:
            str: Pretty formatted string of units.
        """
        return self.pretty_auto_units(self.name_to_metric_dict[from_unit_name])

    def fixed_convert(self, value, from_unit_metric, from_unit_IP, to_unit, decimals=None):
        """Converts a value to a unit from either metric or imperial depending on display

        Args:
            from_unit_metric (str): The current unit if metric display
            from_unit_IP (str): The current unit if ip display
            to_unit (str): The unit to convert to.
            decimal_places (int, optional): The number of decimal places. Default=None

        Returns:
            Number: The value converted value
        """
        from_unit = from_unit_metric if self.is_display_metric else from_unit_IP
        return self.convert(value, from_unit, to_unit, decimals)

    def get_short_units(self, pint_obj):
        """Prints short repr of unit, for signatures of units.

        Args:
            pint_obj (Pint.Quantity): Pint Quantity
        Returns:
            str: Formatted string of units only.
        """
        return '{:~}'.format(pint_obj.units)






