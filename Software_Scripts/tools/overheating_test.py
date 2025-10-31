"""
================
Overheating test
================

Module description
------------------

Tests for occupied overheating for 25 & 28 degC thresholds.
Outputs to xlsx.
Metric only.

Notes
-----
Create model and run Apache sim.
Creates grouping scheme.

"""

import iesve
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import xlsxwriter
import os

def generate_window(project, ve_folder, results_reader, room_groups):

    # 65031
    path = project.path + 'Vista'
    files = None
    try:
        files = os.listdir(path)
    except FileNotFoundError:
        print("Path does not exist!")
        exit()
    except:
        print("Unexpected error occurred")
        exit()

    class Window(tk.Frame):
        def __init__(self, master: tk.Tk):
            tk.Frame.__init__(self, master)
            self.master = master
            self.master.title("Overheating Results")
            self.master.iconbitmap('ies_icon.ico')

            self.project = project
            self.project_folder = project.path
            self.ve_folder = ve_folder
            self.save_file_name = 'Overheating_Results'
            self.results_reader = results_reader
            self.room_groups = room_groups

            self.master.attributes('-topmost', True)

            self.init_window()

        def init_window(self):
            # add grid to window; set column weights
            self.grid(row=0, column=0, sticky='ns')
            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=1)

            # add text and grouping button
            instructions_label1 = ttk.Label(self, text='Click to create a new grouping scheme in your model:')
            instructions_label1.grid(row=1, sticky=tk.W, pady=0, padx=10)
            instructions_label2 = ttk.Label(self, text='You must manually add the rooms you wish to be analysed to the group "Analyse Overheating Results"')
            instructions_label2.grid(row=2, sticky=tk.W, pady=(0, 31), padx=10)

            ttk.Button(self, text="Create Grouping Scheme", command=self.create_grouping).grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)

            # get current project aps file list
            ttk.Label(self, text='Select a Vista Results File (.aps)').grid(row=4, sticky=tk.W, pady=0, padx=10)

            aps_files = []

            for file in files:
                file = file.split('.')
                if file[-1] == 'aps':
                    file = ('.').join(file)
                    aps_files.append(file)

            self.listbox = tk.Listbox(self)
            for file in aps_files:
                self.listbox.insert(tk.END, file)

            self.listbox.select_set(0)
            self.listbox.grid(row=6, sticky='nsew', columnspan=2, pady=(0, 31), padx=10)

            ttk.Label(self, text='Overheating Results will be added to an xls file in the main project folder with the name:').grid(row=8, pady=5, padx=10, sticky=tk.W)
            self.save_file_entry_box = ttk.Entry(self)
            self.save_file_entry_box.insert(0, self.save_file_name)
            self.save_file_entry_box.grid(row=10, sticky='ew', columnspan=2, pady=(5, 26), padx=10)

            self.calc_btn = ttk.Button(self, text="Run Calculation", command=self.run_calc, width=22)
            self.calc_btn.grid(row=12, column=0, sticky='e', pady=5)
            self.cancel_btn = ttk.Button(self, text="Cancel", command=self.close)
            self.cancel_btn.grid(row=12, column=1, sticky='we', padx=10, pady=10, ipadx=5)

            self.columnconfigure(0, weight=1)
            self.rowconfigure(6, weight=1)
            self.grid(row=0, column=0, sticky='nsew')

        def close(self):
            self.master.destroy()

        def create_grouping(self):
            """
            Tests to see if the grouping scheme already exists. If it does not exist, it creates it.
            If it does exist a confirmation popup message is displayed to the user.

            Parameters
            ----------
            None

            Returns
            -------
            None

            """
            schemes = self.room_groups.get_grouping_schemes()
            new_grouping_scheme_needed = True
            for scheme in schemes:
                if scheme['name'] == 'Overheating Analysis':
                    new_grouping_scheme_needed = False

            if new_grouping_scheme_needed:
                scheme_index = self.room_groups.create_grouping_scheme('Overheating Analysis')
                room_groups.create_room_group(scheme_index, "Analyse Overheating Results")
                room_groups.create_room_group(scheme_index, "Do Not Analyse")

                messagebox.showinfo("Grouping scheme", "Manually select the rooms you wish to be analysed and add them to the group \'Analyse Overheating\'")
            else:
                messagebox.showinfo("Grouping scheme already exists", "Grouping scheme already exists")


        def run_calc(self):
            """
            Create the excel workbook, runs the mains calculation functions and writes data to the excel sheet.

            Parameters
            ----------
            None

            Returns
            -------
            None

            """
            schemes = self.room_groups.get_grouping_schemes()
            scheme_handle = False
            for scheme in schemes:
                if scheme['name'] == 'Overheating Analysis':
                    scheme_handle = scheme['handle']

            if scheme_handle == False:
                messagebox.showinfo("Grouping scheme", "Create grouping scheme and assign rooms before running calculation")
                return

            overheating_group = self.room_groups.get_room_groups(scheme_handle)
            rooms_to_be_analysed = []

            for group in overheating_group:
                if group['name'] == 'Analyse Overheating Results':
                    rooms_to_be_analysed = group['rooms']

            # if the grouping scheme is empty, a popup is displayed to the user telling them to put some rooms into the group
            if not rooms_to_be_analysed:
                messagebox.showerror("Room group error", "You must manually add some rooms to the room group \'Analyse Overheating Results\'")
                return

            aps_file_name = self.listbox.get(tk.ACTIVE)
            if not aps_file_name:
                messagebox.showinfo("APS error", "No APS file selected. Please select an APS file.")
                return

            self.save_file_name = self.save_file_entry_box.get()

            # create excel workbook
            workbook = xlsxwriter.Workbook(os.path.join(self.project_folder, self.save_file_name + '.xlsx'))
            # create excel work sheet
            sheet1 = workbook.add_worksheet('sheet1')
            # insert image to worksheet
            sheet1.insert_image('A2', 'IESlogo.png', {'x_offset': 5, 'y_offset': 0})

            # open results file
            results_reader_file = results_reader.open(aps_file_name)

            # run main calculation functions
            def get_overheating_data(results_reader_file, rooms_to_be_analysed, aps_file):
                overheating_data = []
                rooms = results_reader_file.get_room_list()
                # loops through every room in the model
                for room_number, room in enumerate(rooms):
                    # unpack the tuples of room data that is returned from the ResultsReader function. the variables 'a' and
                    #  'b' and not used here but had to be assigned to something
                    name, room_id, a, b = room

                    # prints progress information to the console for the user
                    if room_number % 10 == 0 and room_number + 10 < len(rooms):
                        print('Calculating Rooms: ' + str(room_number + 1) + ' - ' + str(room_number + 10) + ' of ' + str(len(rooms)) + ' in ' + aps_file)
                    elif room_number % 10 == 0 and room_number + 10 >= len(rooms):
                        print('Calculating Rooms: ' + str(room_number + 1) + ' - ' + str(len(rooms)) + ' of ' + str(len(rooms)) + ' in ' + aps_file)

                    # checks if the current room is part of the 'rooms_to_be_analysed' list. Only performs calculations on the rooms that the user placed in the room group
                    if room_id in rooms_to_be_analysed:
                        np_room_temp = results_reader_file.get_room_results(room_id, 'Comfort temperature', 'Dry resultant temperature', 'z')
                        np_occupancy = results_reader_file.get_room_results(room_id, 'Number of people', 'Number of people', 'z')

                        # variables for the range test
                        timesteps_over_28_deg = 0
                        timesteps_over_25_deg = 0
                        occupied_timesteps = 0

                        # convert numpy arrays to python lists
                        room_temp = np_room_temp.tolist()
                        occupancy = np_occupancy.tolist()

                        # counts if rooms are above 25 and 28 deg C per timestep
                        # increments the relevant variable if required
                        for num, temp in enumerate(room_temp):
                            if temp > 28 and occupancy[num] > 0:
                                timesteps_over_28_deg += 1
                                timesteps_over_25_deg += 1
                                occupied_timesteps += 1
                            elif temp > 25 and occupancy[num] > 0:
                                timesteps_over_25_deg += 1
                                occupied_timesteps += 1
                            elif occupancy[num] > 0:
                                occupied_timesteps += 1

                        # adjust the counts depending on the reporting interval
                        # to normalize them to amount of hours
                        results_per_hour = results_reader_file.results_per_day / 24

                        range_test_28_deg = timesteps_over_28_deg / results_per_hour
                        range_test_25_deg = timesteps_over_25_deg / results_per_hour
                        occupied_hours = occupied_timesteps / results_per_hour

                        # calculates the % of hours above the thresholds by dividing by the annual occupied hours
                        # value will vary slightly with different reporting interval
                        if occupied_hours > 0:
                            percent_25_deg = str(round(range_test_25_deg / occupied_hours * 100, 2)) + '%'
                            percent_28_deg = str(round(range_test_28_deg / occupied_hours * 100, 2)) + '%'
                        else:
                            percent_25_deg = '0%'
                            percent_28_deg = '0%'

                        room_overheating_data = [name, range_test_25_deg, percent_25_deg, range_test_28_deg, percent_28_deg]

                        overheating_data.append(room_overheating_data)
                return overheating_data

            print('Running Calculations')
            overheating_data = get_overheating_data(results_reader_file, rooms_to_be_analysed, aps_file_name)

            heading = ['Room Name', 'Hours > 25\u2070C', '% Hours > 25\u2070C', 'Hours > 28\u2070C', '% Hours > 28\u2070C']

            # write data to excel worksheets
            print('Writing results to Excel Sheet')

            # set formatting options
            format_headings = workbook.add_format({'bg_color': '#E6E6E6', 'align' : 'center'})
            format_deg = workbook.add_format({'align' : 'right'})
            format_pct = workbook.add_format({'align' : 'right'})

            # write column headings
            sheet1.write_row(7, 0, heading, format_headings)

            # write results data
            y = 8
            for row in overheating_data:
                sheet1.write(y, 0, row[0])
                sheet1.write(y, 1, row[1], format_deg)
                sheet1.write(y, 2, row[2], format_pct)
                sheet1.write(y, 3, row[3], format_deg)
                sheet1.write(y, 4, row[4], format_pct)
                y += 1

            # set column widths
            sheet1.set_column('A:A', 40)
            sheet1.set_column('B:E', 20)

            try:
                workbook.close()
            except PermissionError as e:
                print("Couldn't close workbook: ", e)
            os.startfile(os.path.join(self.project_folder, self.save_file_name + '.xlsx'))
            root.destroy()

    root = tk.Tk()
    Window(root)
    root.mainloop()

if __name__ == '__main__':
    project = iesve.VEProject.get_current_project()
    print(project.path)
    ve_folder = iesve.get_application_folder()
    results_reader = iesve.ResultsReader
    room_groups = iesve.RoomGroups()

    # generate the tkinter GUI
    generate_window(project, ve_folder, results_reader, room_groups)