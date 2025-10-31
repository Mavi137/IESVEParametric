"""
=========================
Free form profile creator
=========================

Module description
------------------

This script utilises external data in a csv format to create an hourly free-form
profile (ffd) that is added to the project profiles database - see Apache ApPro.

Notes
-----
The script utilises an external csv file that must meet the following requirements:

- column header row .... month, day, hour, min, value
- 8760 data rows plus last day / hour (hour 24) row
- for month, day, hour, min int values
- for value float values

"""

import iesve
import pandas as pd

import os
from tkinter import Tk, messagebox
from tkinter.filedialog import askopenfilenames


def pick_csv_file(file_types, title):
    """
    Opens a file picker in the current project's root folder.

    Args:
        file_types (list of tuples): tuples defining sought file types
        title (str): title for file picking dialog
    Returns:
        str: full path of selected file
    Raises:
        FileNotFoundError: When no file is selected by the user or when the IESVE project folder is not found
    """
    current_project = iesve.VEProject.get_current_project()
    initial_dir = os.path.join(current_project.path, 'ffd_data')

    if not os.path.exists(initial_dir):
        # no ffd_data folder, revert to the project folder instead
        initial_dir = current_project.path

    if not os.path.exists(initial_dir):
        raise FileNotFoundError("No IESVE project folder found.")

    ve_folder = iesve.get_application_folder()
    icon_path = os.path.join(ve_folder, "Scripts", "tools", "ies_icon.ico")

    root = Tk()
    root.wm_attributes('-topmost', 1)
    root.iconbitmap(icon_path)
    root.withdraw()
    options = {}
    options["initialdir"] = initial_dir
    options["filetypes"] = file_types
    options["title"] = title
    options["parent"] = root
    file_name = askopenfilenames(**options)
    root.destroy()

    if not file_name:
        raise FileNotFoundError("No file selected.")

    return file_name


def validate_data(data, profile_type):
    """Performs some validation on the information in the CSV.
    Namely, that each row has 5 columns, and the last element
    in each row is either a number or a str. In addition, ensures
    that modulating profiles have a value between 0 and 1.

    Args:
        data (list): The data to be validated.
        profile_type (str): Whether the profile is modulating or absolute.

    Raises:
        ValueError: If the amount of columns in a row is not 5.
        ValueError: If the last element in a row is not a number or str.

    Returns:
        True: If the validation succeeded.
    """

    for row in data:
        if len(row) != 5:
            raise ValueError("Free-form Profile: unable to set data. Five entry parameters required: month, day, hour, minute, and value or formula.")
        if type(row[4]) not in [int, float, str]:
            raise ValueError("Free-form Profile: unable to set data. Value parameter requires either a numeric type or a string.")
        if type(row[4]) in [int, float] and (0 >= row[4] >= 1) and profile_type == "modulating":
            raise ValueError("Free-form Profile: unable to set data. Modulating profiles require values between 0 and 1.")

    return True


# Get the current VE project
project = iesve.VEProject.get_current_project()

# Import raw data
try:
    data_file_names = pick_csv_file([("CSV files", "*.csv")], "Select a CSV file")
except FileNotFoundError as e:
    messagebox_root = Tk()
    messagebox_root.wm_attributes('-topmost', 1)
    messagebox_root.withdraw()
    messagebox.showerror("Error", str(e) + " Quitting script...", parent=messagebox_root)
    messagebox_root.destroy()
    quit()

for data_file_name in data_file_names:
    # load the csv file into a df
    try:
        data = pd.read_csv(data_file_name)
    except Exception as e:
        messagebox_root = Tk()
        messagebox_root.wm_attributes('-topmost', 1)
        messagebox_root.withdraw()
        messagebox.showerror('Error', "Unable to parse the CSV file. Ensure there are no issues with the file and try again. \n\nDetails:\n{}".format(str(e)), parent=messagebox_root)
        messagebox_root.destroy()
        quit()

    # remove any NaN values from the data
    data.dropna(inplace=True)

    convert_dict = {
        'month': int,
        'day': int,
        'hour': int,
        'min': int,
    }

    # ensure the date columns are ints
    for k, v in convert_dict.items():
        try:
            data[k] = data[k].astype(v)
        except KeyError:
            strErr = "Could not find column with name \"" + str(k) + "\" in the selected CSV. Please ensure the CSV is in the correct format (with month, day, hour, and min columns)."
            messagebox_root = Tk()
            messagebox_root.wm_attributes('-topmost', 1)
            messagebox_root.withdraw()
            messagebox.showerror("CSV Parsing Error", strErr + " The script will terminate now.", parent=messagebox_root)
            messagebox_root.destroy()
            quit()

    # IESVE requires that the month, day, hour, and minute columns for the profile are integers, but the "value" column has to be a float to
    # be able to be set as a modulating (0-1) profile in IES. This step can be skipped if you do not have any float values and are using
    # an absolute profile. This step is required to convert each column in the dataframe to a list individually so that they maintain
    # their data types (integer for first 4 values, float for last)
    data_to_list = list(
        list(x) for x in zip(*(data[x].values.tolist() for x in data.columns))
    )

    # modulating/absolute is encoded in the header of the value column
    # along with whether the units are ip or metric
    # in the form value|modulating or value|absolute|ip.
    # these are both optional, and the order shouldn't matter.
    # however, units only are considered if the profile is absolute
    value_column = data.columns[-1].split('|')

    # in the event that there's nothing encoded there, assume absolute
    # and metric

    profile_type = "absolute"
    profile_units = "metric"

    if len(value_column) > 1:
        for el in value_column[1:]:
            el = el.lower()
            if el in ('absolute', 'modulating'):
                profile_type = el
            if el in ('metric', 'ip'):
                profile_units = el

    # need a bool for the create_profile call, and a ProfileUnits obj for the units
    modulating = profile_type == "modulating"
    units = iesve.ProfileUnits.metric if profile_units == 'metric' else iesve.ProfileUnits.imperial

    try:
        validate_data(data_to_list, profile_type)
    except ValueError as e:
        messagebox_root = Tk()
        messagebox_root.wm_attributes('-topmost', 1)
        messagebox_root.withdraw()
        messagebox.showerror('Error', str(e), parent=messagebox_root)
        messagebox_root.destroy()
        quit()

    # Create ffd in project
    print("Creating free-form profile")

    if data_file_name.endswith('.csv'):
        stem = data_file_name[:-4]
    else:
        stem = data_file_name

    stem = os.path.split(stem)[1]

    # create_profile and its arguments is from the VE Scripts user guide
    free_profile = project.create_profile(
        type="freeform", reference=stem, modulating=modulating, units=units
    )
    free_profile_data = data_to_list  # set data to use for "free profile"

    try:
        # set_data is from the VE Scripts user guide, this is a boolean argument
        free_profile.set_data(free_profile_data)
    except RuntimeError as e:
        # if it failed the checks in validate_data, it shouldn't be able to reach here
        # just in case, catch the exception and pop up an error box without the traceback
        messagebox_root = Tk()
        messagebox_root.wm_attributes('-topmost', 1)
        messagebox_root.withdraw()
        messagebox.showerror('Error', str(e), parent=messagebox_root)
        messagebox_root.destroy()
        quit()

    assert isinstance(free_profile, iesve.FreeFormProfile), "Profile is not free-form"
    free_profile.save_data()  # save_data is from the VE scripts user guide

messagebox_root = Tk()
messagebox_root.wm_attributes('-topmost', 1)
messagebox_root.withdraw()
plural = 's' if len(data_file_names) > 1 else ''
messagebox.showinfo(
    "Profile{0} created".format(plural),
    "Free-form profile{0} added to project. Go to ApPro to if you wish to rename the profile{0}.".format(plural),
    parent=messagebox_root
)
messagebox_root.destroy()
