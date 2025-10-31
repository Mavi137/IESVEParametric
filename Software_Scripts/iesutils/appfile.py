import base64
import csv
import datetime
import json

import numpy as np
import pandas as pd


APP_VERSION = 2


class APPFileError(Exception):
    """Used for any APP-specific errors raised."""
    pass


def parse_header(header):
    """Parses the header line of an APP file.

    Args:
        header (str): The header

    Raises:
        APPFileError: If any of the header fields are missing.

    Returns:
        A 3-tuple containing a list and two dicts.
        names: An ordered list of the parsed variable names.
        variables: A dict containing the variable information (category, units, variable metadata).
        metadata: A dict containing the global metadata, if any. Empty dict if none.
    """
    variables, global_metadata = {}, {}
    encoded_metadata = ''
    has_metadata = False
    var_headers = header.split(',')

    first_header = var_headers[0].split('|')

    if len(first_header) == 4:
        # extract the global metadata from the first header
        has_metadata = True
        encoded_metadata = first_header[3]

    if has_metadata:
        try:
            names, cats, units, var_metadata = list(zip(*[var.split('|') for var in var_headers]))
            cats = [cat.split('>') for cat in cats]
        except ValueError as e:
            raise APPFileError('Length mismatch on header items.') from e

        if not (len(cats) == len(units) == len(names) == len(var_metadata)):
            raise APPFileError('Length mismatch on header items.')
    else:
        try:
            names, cats, units = list(zip(*[var.split('|') for var in var_headers]))
            cats = [cat.split('>') for cat in cats]
        except ValueError as e:
            raise APPFileError('Length mismatch on header items.') from e

        if not (len(cats) == len(units) == len(names)):
            raise APPFileError('Length mismatch on header items.')

    for i, name in enumerate(names):
        if name == 'Date/Time Stamp':
            variables[name] = {'rpd': int(units[i]), 'year': int(cats[i][0]), 'data': []}
        else:
            if has_metadata:
                try:
                    var_meta = json.loads(base64.b64decode(var_metadata[i]).decode('utf8'))
                except Exception as e:
                    raise APPFileError("Invalid variable metadata in header.") from e
                variables[name] = {'unit': units[i], 'category': cats[i], 'metadata': var_meta, 'data': []}
            else:
                variables[name] = {'unit': units[i], 'category': cats[i], 'data': []}

    if encoded_metadata:
        try:
            global_metadata = json.loads(base64.b64decode(encoded_metadata).decode('utf8'))
        except Exception as e:
            raise APPFileError("Invalid global metadata in header.") from e

    if not global_metadata:
        # update to current version
        global_metadata = {"version": APP_VERSION}

    return list(names), variables, global_metadata

DATE_FMT = "%d/%m/%Y %H:%M:%S"

# these are intended to be used like the json methods
def load(fp):
    """Creates an APPFile object from a file handle.

    Args:
        fp (file): The file handle to be loaded.

    Returns:
        APPFile: The APPFile representation of the loaded file.
    """
    return loads(fp.read())

def loads(s):
    """Creates an APPFile object from a newline-delimited string.

    Args:
        s (str): Newline-delimited string representing the APP file.

    Returns:
        APPFile: The APPFile representation of the string.
    """
    lines = s.splitlines()

    header = lines[0]
    names, variables, metadata = parse_header(header)

    reader = csv.DictReader(lines[1:], fieldnames=names)

    for row in reader:
        for el in row:
            if el == 'Date/Time Stamp':
                # parse as datetime
                dt = datetime.datetime.strptime(row[el], DATE_FMT)
                variables[el]['data'].append(dt)
            else:
                # should be a float
                try:
                    val = float(row[el])
                    variables[el]['data'].append(val)
                except ValueError:
                    # something didn't work, fall back to string
                    variables[el]['data'].append(row[el])

    return APPFile(variables, order=names, global_metadata=metadata)

def dump(obj, fp):
    """Writes an APPFile object to a file handle.

    Args:
        obj (APPFile): The APPFile to be written.
        fp (file): The handle of the file to be written.
    """
    fp.write(dumps(obj))

def dumps(obj):
    """Returns the string representation of the APP format from an APPFile.

    Args:
        obj (APPFile): The APPFile to be written.

    Raises:
        APPFileError: If there is missing variable information in the APPFile instance.

    Returns:
        str: A newline-delimited string representing the APP file.
    """
    lines = []

    names, cats, units, var_metadata, data = [], [], [], [], []

    # encode metadata
    j = json.dumps(obj.metadata)
    encoded = base64.b64encode(bytes(j, encoding='utf8'))
    var_metadata.append(encoded.decode('utf8'))

    for key in obj.order:
        names.append(key)

        try:
            if key == 'Date/Time Stamp':
                cats.append([str(obj[key]['year'])])
                units.append(str(obj[key]['rpd']))
                if type(obj[key]['data'][0]) == np.datetime64:
                    data.append([pd.to_datetime(date).strftime(DATE_FMT) for date in obj[key]['data']])
                elif type(obj[key]['data'][0]) == tuple:
                    data.append([pd.to_datetime(date[1]).strftime(DATE_FMT) for date in obj[key]['data']])
                else:
                    data.append([date.strftime(DATE_FMT) for date in obj[key]['data']])
            else:
                cats.append(obj[key]['category'])
                units.append(obj[key]['unit'])
                data.append(obj[key]['data'])

                j = json.dumps(obj[key]['metadata'])
                encoded = base64.b64encode(bytes(j, encoding='utf8'))
                var_metadata.append(encoded.decode('utf8'))
        except KeyError as e:
            raise APPFileError('Missing variable information in {}.'.format(key)) from e

    var_amount = len(names)
    var_headers = ['|'.join([names[i], '>'.join(cats[i]), units[i], var_metadata[i]]) for i in range(var_amount)]

    header = ','.join(var_headers)

    lines.append(header)

    if not all(len(x) == len(data[0]) for x in data):
        raise APPFileError('Data length mismatch.')

    len_data = len(data[0])
    for i in range(len_data):
        lines.append(','.join([str(x[i]) for x in data]))

    return '\n'.join(lines)


class APPFile:
    """Wrapper class for dealing with APP files.

    These are essentially a specific type of CSV file, with particular
    information about the variables in each column encoded in the header
    of the file itself.

    This header takes the format:

    timeinfo,variable1,variable2,...

    -------------------------------------------------------------------------

    The timeinfo field is always the first column in the file. The values
    are the dates and times for the time series data. It is pipe-delimited,
    and takes the following form:

    Date/Time Stamp|year|rpd|metadata

    Where "year" is an integer denoting the year, and "rpd" is an integer
    denoting the amount of results in a single day (in other words,
    the reporting interval of the data).

    The "metadata" field is a base64 encoded JSON blob, used for more
    general-purpose information. It is optional, but wil be created when
    an APP file is created through this API.

    -------------------------------------------------------------------------

    The variable field is similarly pipe-delimited, and takes the following
    form:

    name|category|unit_type|metadata

    Where "name" is the desired display name of the custom variable, "category"
    is the >-delimited hierarchy of the category tree, and "unit_type" is the
    type of unit, as defined in the Unit-types.unt file. The "metadata" field
    is an optional base64 encoded JSON blob, similar to the global one above,
    but for variable-specific information. As above, the field is optional,
    but if there is a global metadata field, then it is assumed the field
    exists for variable columns as well.

    For example, a category field containing "a>b>c" would be rendered as the
    following in the "Categories" selection box in VistaPro:

    a
    └──b
       └──c

    If the category doesn't exist, it will be created. These can be nested
    pretty much indefinitely, though I would advise against it, as you're
    likely to hit some stack limit somewhere else eventually.
    """
    def __init__(self, data, order=None, global_metadata=None):
        """The constructor.

        Args:
            data (dict): A dict of variables, containing the category,
                units, and data.
            order (list[str], optional): A list containing the desired order
                of the variables in the APP file. Defaults to None.
            global_metadata (dict, optional): A dict containing the
                global metadata.

        Raises:
            TypeError: If initialised with anything other than a dict or
                pandas DataFrame.
        """
        if type(data) == pd.DataFrame:
            data = data.to_dict()

        if type(data) != dict:
            raise TypeError("Must be initialised with a dict or DataFrame.")

        self.data = data
        self.order = order if order is not None else list(data.keys())

        # check for empty metadata and populate the version field
        # if it doesn't exist already
        if global_metadata is None:
            global_metadata = {"version": APP_VERSION}
        else:
            if "version" not in global_metadata:
                global_metadata["version"] = APP_VERSION

        self.metadata = global_metadata

        for var_name in self.data.keys():
            var = self.data[var_name]
            if 'metadata' not in var and var_name != "Date/Time Stamp":
                var['metadata'] = {}

        # move date to the start
        if 'Date/Time Stamp' in self.order:
            self.order.pop(self.order.index('Date/Time Stamp'))

        self.order.insert(0, 'Date/Time Stamp')

    @classmethod
    def from_dict(cls, data, global_metadata=None):
        """Creates a new instance from a dict.

        This dict follows a fairly specific format, which is as follows:

        {
            "variable_name": {
                "unit": "Temperature",
                "category": ["Category", "Subcategory 1"],
                "metadata": {},
                "data": [1.0, 2.0, 3.0, ...]
            }
        }

        The data key of each single variable dict is a list of floats containing
        the values to be displayed in Vista. The metadata key here is the
        variable-specific metadata, not to be confused with the optional
        global_metadata argument.

        It's worth noting that the time column is different. The name is always
        "Date/Time Stamp", and instead of "unit" and "category" keys, it instead
        has "year" and "rpd" keys, representing the year and results per day
        respectively.

        Args:
            data (dict): A dict containing the variable information.
            global_metadata (dict, optional): A dict containing the
                global metadata.

        Returns:
            APPFile: An APPFile representing the information in the dict.
        """
        return cls(data, global_metadata=global_metadata)

    @classmethod
    def from_dataframe(cls, df, variables=None, order=None, global_metadata=None):
        """Creates a new instance from a pandas DataFrame.

        In addition to the DataFrame, it also requires a variables dict
        containing the variable information (but without the "data" key),
        and also requires a list containing the desired variable names in
        the correct order.

        If any of these two things are omitted, it attempts to convert
        the DataFrame to CSV, then parse it normally. This would require
        the header format to be already inside the DataFrame column
        names.

        Args:
            df (pandas.DataFrame): The DataFrame containing the data to be
                stored as APP.
            variables (dict, optional): The dict containing variable
                information. Defaults to None.
            order (list, optional): A list of strings with the desired order
                to be represented in the APP file. Defaults to None.
            global_metadata (dict, optional): A dict containing the
                global metadata.

        Returns:
            APPFile: An APPFile representing the information provided.
        """
        if variables is None or order is None:
            return loads(df.to_csv())
        else:
            for var in variables:
                if var == 'Date/Time Stamp':
                    variables[var]['data'] = list(df.index.values)
                else:
                    variables[var]['data'] = list(df[var].values)
            return cls(variables, order=order, global_metadata=global_metadata)

    def return_dataframe_columns(self, variables):
        """Returns a pandas DataFrame containing the index column
        and the variables specified.

        Args:
            variables (list[str]): A list of variables to be obtained.

        Returns:
            pandas.DataFrame: A DataFrame containing the desired variables.
        """
        # remove timestamp, as we're getting it separately
        if "Date/Time Stamp" in variables:
            variables.remove("Date/Time Stamp")

        variable_data = [
            self.data[var]['data'] for var in variables
        ]

        # transpose data, so pandas can deal with it
        variable_data = np.array(variable_data).T
        index_data = np.array(self.data["Date/Time Stamp"]['data']).T

        df = pd.DataFrame(variable_data, columns=variables, index=index_data)

        return df

    def __getitem__(self, key):
        """Allows key indexing to fall through and use the instance's data
        dict.

        Args:
            key (str): The key to be accessed.

        Returns:
            dict: A dict containing the variable information and data for
                the given key.
        """
        try:
            return self.data[key]
        except KeyError:
            raise

    def __setitem__(self, *_):
        # the intention is to pass the completed dict on initialisation,
        # so leaving this deliberately unimplemented for now
        raise NotImplementedError
