import iesve
import tkinter as tk
from tkinter import messagebox
import xlsxwriter
import os
import math
import datetime

def generate_window(project, ve_folder, results_reader, room_groups):
    class Window(tk.Frame):
        def __init__(self, master):
            tk.Frame.__init__(self, master)

            self.project = project
            self.project_folder = project.path
            self.ve_folder = ve_folder
            self.save_file_name = 'Heat_Balance_Results'
            self.results_reader = results_reader
            self.room_groups = room_groups
            self.master: tk.Tk = master
            self.init_window()

        # Creation of init_window
        def init_window(self):
            self.master.title("Heat Balance Results")
            self.master.columnconfigure(0, weight=1)
            self.master.rowconfigure(0, weight=1)
            self.master.grid()

            instructions_label = tk.Label(self, justify='left', text='Click the button below to create a new grouping scheme in your model.\nManually add the rooms you wish to be analysed to the group "Analyse Sensible Heat Balance"')
            instructions_label.grid(row=0, sticky='w')
            tk.Button(self, text="Create Grouping Scheme", command=self.create_grouping).grid(row=2, sticky=tk.W)
            tk.Label(self, text=' ').grid(row=3, sticky=tk.W)

            tk.Label(self, text=' ').grid(row=4, sticky=tk.W)
            tk.Label(self, text='Select a Vista Results File (.aps)').grid(row=5, sticky=tk.W)

            print(self.project_folder)
            path = self.project_folder + 'Vista'

            files = os.listdir(path)

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
            self.listbox.grid(row=6, sticky='nsew')
            tk.Label(self, text=' ').grid(row=7, sticky=tk.W)

            tk.Label(self, text='Sensible Heat Balance Results will be added to an Excel sheet that will be saved into the main project folder').grid(row=8, sticky=tk.W)
            tk.Label(self, text='Name the Excel file below:').grid(row=9, sticky=tk.W)
            self.save_file_entry_box = tk.Entry(self)
            self.save_file_entry_box.insert(0, self.save_file_name)
            self.save_file_entry_box.grid(row=10, sticky='ew')
            tk.Label(self, text=' ').grid(row=11, sticky=tk.W)

            # creating a button instance
            tk.Button(self, text="Run Calculation", command=self.run_calc).grid(row=12, sticky=tk.W)

            self.columnconfigure(0, weight=1)
            self.rowconfigure(6, weight=1)
            self.grid(row=0, column=0, sticky='nsew')


        def create_grouping(self):
            schemes = self.room_groups.get_grouping_schemes()
            new_grouping_scheme_needed = True
            for scheme in schemes:
                if scheme['name'] == 'Sensible Heat Balance Analysis':
                    new_grouping_scheme_needed = False

            if new_grouping_scheme_needed:
                scheme_index = self.room_groups.create_grouping_scheme('Sensible Heat Balance Analysis')
                room_groups.create_room_group(scheme_index, "Analyse Sensible Heat Balance Results")
                room_groups.create_room_group(scheme_index, "Do Not Analyse")

                messagebox.showinfo("Grouping scheme", "Manually select the rooms you wish to be analysed and add them to the group \'Analyse Sensible Heat Balance Results\'")
            else:
                messagebox.showinfo("Grouping scheme already exists", "Grouping scheme already exists")


        def run_calc(self):
            """create the excel workbook, runs the mains calculation functions and writes data to the excel sheet
            """
            schemes = self.room_groups.get_grouping_schemes()
            scheme_handle = False
            for scheme in schemes:
                if scheme['name'] == 'Sensible Heat Balance Analysis':
                    scheme_handle = scheme['handle']

            if scheme_handle == False:
                messagebox.showinfo("Grouping scheme", "Create grouping scheme and assign rooms before running calculation")
                return

            heat_balance_group = self.room_groups.get_room_groups(scheme_handle)
            rooms_to_be_analysed = []
            for group in heat_balance_group:
                if group['name'] == 'Analyse Sensible Heat Balance Results':
                    rooms_to_be_analysed = group['rooms']

            if not rooms_to_be_analysed:
                messagebox.showerror("Assign rooms to groups", "You must manually add some rooms to the room group \'Analyse Sensible Heat Balance Results\'")
                return

            aps_file_name = self.listbox.get(tk.ACTIVE)
            if not aps_file_name:
                messagebox.showinfo("APS error", "No APS file selected. Please select an APS file.")
                return

            self.save_file_name = self.save_file_entry_box.get()
            print('Excel File name = \t\t' + self.save_file_name)

            # create excel workbook
            workbook = xlsxwriter.Workbook(self.project_folder + '\\' + self.save_file_name + '.xlsx')
            # create excel work sheet
            sheet1 = workbook.add_worksheet('sheet1')
            # insert image to worksheet
            sheet1.insert_image('A2', self.ve_folder + 'Templates\\workflow\\IESlogo.png', {'x_offset': 5, 'y_offset': 0})

            # run main calculation functions

            results_reader_file = results_reader.open(aps_file_name)

            def get_heat_balance_data(results_reader_file, rooms_to_be_analysed, aps_file):

                rooms = results_reader_file.get_room_list()

                # declare list that will contain the heat balance data for each variable for the peak day
                heat_balance_data = []

                # declare list that will contain the column headings for each variable that is applicable to each room
                column_headings = []

                for room_number, room in enumerate(rooms):
                    # unpack the tuples of room data that is returned from the ResultsReader function. the variables 'a' and 'b' and not used here but had to be assigned to something
                    _, room_id, _, _ = room

                    # prints progress information to the console for the user
                    if room_number % 10 == 0 and room_number + 10 < len(rooms):
                        print('Calculating Rooms: ' + str(room_number + 1) + ' - ' + str(room_number + 10) + ' of ' + str(len(rooms)) + ' in ' + aps_file)
                    elif room_number % 10 == 0 and room_number + 10 >= len(rooms):
                        print('Calculating Rooms: ' + str(room_number + 1) + ' - ' + str(len(rooms)) + ' of ' + str(len(rooms)) + ' in ' + aps_file)

                    if room_id in rooms_to_be_analysed:
                        np_space_cond = results_reader_file.get_room_results(room_id, 'System plant etc. gains', 'Space conditioning sensible', 'z', 1, 365)

                        # get the index of the row where this max cooling load occurs (min space conditioning value)
                        min_space_cond_index = np_space_cond.argmin()
                        # get the number of the day the max cooling load occurs by dividing by 24 and rounding the result down to the nearest integer
                        min_space_cond_day_num = math.floor(min_space_cond_index / 24)

                        end_uses = ['System plant etc. gains',
                                    'Window solar gains',
                                    'Casual gains',
                                    'Conduction from ext elements',
                                    'Conduction from int surfaces',
                                    'Aux mech vent gain',
                                    'Natural vent gain',
                                    'Infiltration gain',
                                    'Cooling vent gain',
                                    'MacroFlo ext vent gain',
                                    'MacroFlo int vent gain']

                        vars = ['Space conditioning sensible',
                                'Solar gain',
                                'Internal gain',
                                'External conduction gain',
                                'Internal conduction gain',
                                'Aux vent gain',
                                'Natural vent gain',
                                'Infiltration gain',
                                'Free cooling vent gain',
                                'MacroFlo ext vent gain',
                                'MacroFlo int vent gain']

                        heading = ['Space Conditioning Sensible (kW)',
                                   'Solar Gains (kW)',
                                   'Internal Gains (kW)',
                                   'External Conduction Gain (kW)',
                                   'Internal Conduction Gain (kW)',
                                   'Aux Vent Gain (kW)',
                                   'Nat Vent Gain (kW)',
                                   'Infiltration Gain (kW)',
                                   'Free Cooling Vent Gain (kW)',
                                   'MacroFlo External Vent Gain (kW)',
                                   'MacroFlo Internal Vent Gain (kW)']

                        room_heat_balance_data = []
                        room_column_headings = []
                        i = 0
                        for end_use in end_uses:
                            if results_reader_file.get_room_results(room_id, end_use, vars[i], 'z', 1, 365) is not None:
                                np_data = results_reader_file.get_room_results(room_id, end_use, vars[i], 'z', 1, 365)/1000
                                np_peak_day_data = np_data[24 * min_space_cond_day_num:24 * min_space_cond_day_num + 24]
                                peak_day_data = np_peak_day_data.tolist()
                                room_heat_balance_data.append(peak_day_data)
                                room_column_headings.append(heading[i])
                                i += 1
                        column_headings.append(room_column_headings)
                        heat_balance_data.append(room_heat_balance_data)
                return (column_headings, heat_balance_data)

            room_labels = []

            rooms = results_reader_file.get_room_list()
            for room in rooms:
                if room[1] in rooms_to_be_analysed:
                    np_space_cond_ = results_reader_file.get_room_results(room[1], 'System plant etc. gains', 'Space conditioning sensible', 'z', 1, 365)

                    # get the index of the row where this max occurs
                    min_space_cond_index = np_space_cond_.argmin()
                    # get the number of the day the max occurs by dividing by 24 and rounding the result down to the nearest integer
                    min_space_cond_day_num = math.floor(min_space_cond_index / 24)

                    peak_date = datetime.datetime(2000, 1, 1) + datetime.timedelta(min_space_cond_day_num + 1)
                    peak_date = peak_date.strftime('%d %b')
                    room_label = room[0] + ' (' + str(peak_date) + ')'
                    room_labels.append(room_label)

            print('Running Calculations')
            (column_headings, heat_balance_data) = get_heat_balance_data(results_reader_file, rooms_to_be_analysed, aps_file_name)

            # write data to excel worksheets
            print('Writing results to Excel Sheet')

            # write column headings

            day_time = ['00:30', '01:30', '02:30', '03:30', '04:30', '05:30', '06:30', '07:30', '08:30', '09:30',
                        '10:30', '11:30', '12:30', '13:30', '14:30', '15:30', '16:30', '17:30', '18:30', '19:30',
                        '20:30', '21:30', '22:30', '23:30']

            # write results data
            y = 11
            for num, room_data in enumerate(heat_balance_data):
                x = 0

                chart = workbook.add_chart({'type': 'line'})

                if chart:
                    chart.add_series({'name': '=sheet1!$B$' + str(y + 1),
                                    'categories':  '=sheet1!$A$' + str(y + 2) + ':$A$' + str(y + 25),
                                    'values': '=sheet1!$B$' + str(y + 2) + ':$B$' + str(y + 25)})
                    chart.add_series({'name': '=sheet1!$C$' + str(y + 1),
                                    'categories':  '=sheet1!$A$' + str(y + 2) + ':$A$' + str(y + 25),
                                    'values': '=sheet1!$C$' + str(y + 2) + ':$C$' + str(y + 25)})
                    chart.add_series({'name': '=sheet1!$D$' + str(y + 1),
                                    'categories':  '=sheet1!$A$' + str(y + 2) + ':$A$' + str(y + 25),
                                    'values': '=sheet1!$D$' + str(y + 2) + ':$D$' + str(y + 25)})
                    chart.add_series({'name': '=sheet1!$E$' + str(y + 1),
                                    'categories':  '=sheet1!$A$' + str(y + 2) + ':$A$' + str(y + 25),
                                    'values': '=sheet1!$E$' + str(y + 2) + ':$E$' + str(y + 25)})
                    chart.add_series({'name': '=sheet1!$F$' + str(y + 1),
                                    'categories':  '=sheet1!$A$' + str(y + 2) + ':$A$' + str(y + 25),
                                    'values': '=sheet1!$F$' + str(y + 2) + ':$F$' + str(y + 25)})
                    chart.add_series({'name': '=sheet1!$G$' + str(y + 1),
                                    'categories':  '=sheet1!$A$' + str(y + 2) + ':$A$' + str(y + 25),
                                    'values': '=sheet1!$G$' + str(y + 2) + ':$G$' + str(y + 25)})
                    chart.add_series({'name': '=sheet1!$H$' + str(y + 1),
                                    'categories':  '=sheet1!$A$' + str(y + 2) + ':$A$' + str(y + 25),
                                    'values': '=sheet1!$H$' + str(y + 2) + ':$H$' + str(y + 25)})
                    chart.add_series({'name': '=sheet1!$I$' + str(y + 1),
                                    'categories':  '=sheet1!$A$' + str(y + 2) + ':$A$' + str(y + 25),
                                    'values': '=sheet1!$I$' + str(y + 2) + ':$I$' + str(y + 25)})
                    chart.add_series({'name': '=sheet1!$J$' + str(y + 1),
                                    'categories':  '=sheet1!$A$' + str(y + 2) + ':$A$' + str(y + 25),
                                    'values': '=sheet1!$J$' + str(y + 2) + ':$J$' + str(y + 25)})
                    chart.add_series({'name': '=sheet1!$K$' + str(y + 1),
                                    'categories':  '=sheet1!$A$' + str(y + 2) + ':$A$' + str(y + 25),
                                    'values': '=sheet1!$K$' + str(y + 2) + ':$K$' + str(y + 25)})
                    chart.add_series({'name': '=sheet1!$L$' + str(y + 1),
                                    'categories':  '=sheet1!$A$' + str(y + 2) + ':$A$' + str(y + 25),
                                    'values': '=sheet1!$L$' + str(y + 2) + ':$L$' + str(y + 25)})

                    sheet1.insert_chart(y, len(column_headings[num])+2, chart, {'x_scale': 1.4, 'y_scale': 1.73})

                sheet1.write(y, x, room_labels[num])
                sheet1.write_row(y, x+1, column_headings[num])
                sheet1.write_column(y+1, x, day_time)
                for variable in room_data:
                    sheet1.write_column(y+1, x+1, variable)
                    x += 1
                y += 26

            # set column widths
            sheet1.set_column('A:L', 17)

            try:
                workbook.close()
            except PermissionError as e:
                print("Couldn't close workbook: ", e)
            os.startfile(self.project_folder + '\\' + self.save_file_name + '.xlsx')
            root.destroy()


    root = tk.Tk()
    Window(root)
    root.mainloop()

if __name__ == '__main__':
    project = iesve.VEProject.get_current_project()
    ve_folder = iesve.get_application_folder()
    results_reader = iesve.ResultsReader
    room_groups = iesve.RoomGroups()

    generate_window(project, ve_folder, results_reader, room_groups)