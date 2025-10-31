"""
=========================
Create ffd input csv file
=========================

Module description
------------------

This script creates an hourly csv file in the correct format in the
current project root folder with default values ready to be edited
by the user.

Notes
-----
1. The script adds a final row for hour 24 for last day of the year.
2. Once created users can copy / paste data into the value column.

"""

import iesve
import os
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from datetime import datetime, timedelta


class FFDCreate(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text="Time step (mins):").grid(row=0, column=0, padx=10, pady=(10, 0), sticky='w')
        self.timestep_box = ttk.Combobox(self, state="readonly", values=['60', '30', '10', '6', '2', '1'])
        self.timestep_box.grid(row=1, column=0, padx=10, pady=5, sticky='ew')
        self.timestep_box.current(0)

        self.type_var = tk.StringVar()
        self.type_var.set("Modulating")
        self.units_var = tk.StringVar()
        self.units_var.set("Metric")

        self.radio_frame = tk.Frame(self)
        self.radio_frame.grid(row=2, column=0, sticky='nsw', columnspan=3)
        self.radio_frame.grid_rowconfigure(0, weight=1)
        self.radio_frame.grid_rowconfigure(1, weight=1)

        ttk.Label(self.radio_frame, text="Type:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        ttk.Label(self.radio_frame, text="Units:").grid(row=0, column=1, padx=10, pady=5, sticky='w')

        self.mod_btn = ttk.Radiobutton(self.radio_frame, text="Modulating", variable=self.type_var, value="Modulating", command=self.handle_click_type)
        self.abs_btn = ttk.Radiobutton(self.radio_frame, text="Absolute", variable=self.type_var, value="Absolute", command=self.handle_click_type)
        self.mod_btn.grid(row=1, column=0, padx=10, pady=(0, 5), sticky='sew')
        self.abs_btn.grid(row=2, column=0, padx=10, pady=(0, 5), sticky='new')

        self.metric_btn = ttk.Radiobutton(self.radio_frame, text="Metric", variable=self.units_var, value="Metric", state='disabled')
        self.ip_btn = ttk.Radiobutton(self.radio_frame, text="IP", variable=self.units_var, value="IP", state='disabled')
        self.metric_btn.grid(row=1, column=1, padx=10, pady=(0, 5), sticky='sew')
        self.ip_btn.grid(row=2, column=1, padx=10, pady=(0, 5), sticky='new')

        ttk.Label(self, text="Filename:").grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self.filename_var = tk.StringVar()
        self.filename_input = ttk.Entry(self, textvariable=self.filename_var)
        self.filename_input.grid(row=4, column=0, padx=10, pady=(0, 5), sticky='nsew')

        self.filename_var.set('ffd_input_data.csv')

        self.btn_frame = tk.Frame(self)
        self.btn_frame.grid(row=5, column=0, sticky='se')

        self.ok_btn = ttk.Button(self.btn_frame, text="OK", command=self.create)
        self.ok_btn.grid(row=0, column=1, padx=(0, 5), pady=(0, 10), sticky='se')

        self.cancel_btn = ttk.Button(self.btn_frame, text="Cancel", command=self.close)
        self.cancel_btn.grid(row=0, column=2, padx=(0, 10), pady=(0, 10), sticky='se')

    def handle_click_type(self):
        profile_type = self.type_var.get()
        if profile_type == 'Modulating':
            self.metric_btn['state'] = 'disabled'
            self.ip_btn['state'] = 'disabled'
        else:
            self.metric_btn['state'] = 'normal'
            self.ip_btn['state'] = 'normal'

    def create(self):
        # if the ffd_data folder doesn't exist, create it
        if not os.path.exists(folder):
            os.mkdir(folder)

        filename = os.path.join(folder, self.filename_var.get())

        if not filename.lower().endswith('.csv'):
            filename += '.csv'

        timestep = int(self.timestep_box.get())
        profile_type = self.type_var.get()
        units_type = self.units_var.get()

        # float if modulating, int if absolute
        value = 0.5 if profile_type == "Modulating" else 10
        data = make_data(timestep, value)

        # make dataframe, encode the profile and units type in the value column, and save
        value_column = 'value|{}'.format(profile_type.lower())
        if profile_type == 'Absolute':
            value_column += '|{}'.format(units_type.lower())

        df = pd.DataFrame(data, columns=['month', 'day', 'hour', 'min', value_column])
        df.to_csv(filename, encoding='utf-8', index=False)

        messagebox.showinfo("CSV file created", "The CSV file has been saved to {}".format(filename), parent=self)
        self.close()

    def close(self):
        self.master.destroy()


def make_data(timestep, value):
    """Creates a nested list containing date fields over a year
    with the given timestep and value.

    Args:
        timestep (int): The timestep in minutes.
        value (Union[int, float]): The default value for the data,
            either int or float.

    Returns:
        list: The nested list of data.
    """
    year = 2018 # arbitrary non-leap year
    cur_date = datetime(year, 1, 1, 0, 0, 0)
    next_year = datetime(year + 1, 1, 1, 0, 0, 0)
    offset = timedelta(minutes=timestep)
    data = []
    while cur_date < next_year:
        data.append([cur_date.month, cur_date.day, cur_date.hour, cur_date.minute, value])
        cur_date += offset
    # Create the final row at the end of the year
    data.append([12, 31, 24, 0, value])
    return data


if __name__ == "__main__":
    # Get the current VE project
    project = iesve.VEProject.get_current_project()
    folder = os.path.join(project.path, 'ffd_data')

    root = tk.Tk()
    root.minsize(250, 231)
    root.title("Create FFD .csv")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    dialog = FFDCreate(root)
    dialog.grid(row=0, column=0, sticky='nsew')

    root.deiconify()  # restore if minimized
    root.lift()  # make the window active

    root.mainloop()