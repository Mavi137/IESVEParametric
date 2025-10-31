import iesve
import numpy as np
import xlsxwriter
import os
import time
import math
import datetime
from tkinter import filedialog, Frame, BOTH, Label, W, Button, Entry, E, IntVar, Checkbutton, Tk


def main():
    ve_folder = iesve.get_application_folder()
    vista_results_reader = iesve.ResultsReader()
    project = iesve.VEProject.get_current_project()
    generate_window(vista_results_reader, project, ve_folder)


class xlsxFormats():
    """Defines the formats for data to be printed to excel"""
    def __init__(self, workbook):
        self.table_title = self.table_title(workbook)
        self.table_main = self.table_main(workbook)
        self.table_total = self.table_total(workbook)
        self.project_data_left = self.project_data_left(workbook)
        self.project_data_right = self.project_data_right(workbook)
        self.highlight_fail = self.highlight_fail(workbook)
        self.highlight_pass = self.highlight_pass(workbook)
        self.instructions_italics = self.instructions_italics(workbook)
        self.instructions_bold = self.instructions_bold(workbook)
        self.hyperlink = self.hyperlink(workbook)
        self.grey_background = self.grey_background(workbook)
        self.white_background = self.white_background(workbook)

    def table_title(self, workbook):
        format = workbook.add_format({'num_format': '0.0', 'color': 'white', 'bg_color': '#305C67', 'size': 18, 'text_wrap': True, 'border': True, 'align': 'centre', 'valign': 'vcenter'})
        return format

    def table_main(self, workbook):
        format = workbook.add_format({'num_format': '0.0', 'color': 'black', 'bg_color': 'white', 'size': 11, 'text_wrap': True, 'border': True, 'align': 'centre', 'valign': 'vcenter'})
        return format

    def table_total(self, workbook):
        format = workbook.add_format(
            {'bold': True, 'color': 'white', 'bg_color': '#448595', 'size': 11, 'text_wrap': True, 'border': True, 'align': 'centre', 'valign': 'vcenter'})
        return format

    def project_data_left(self, workbook):
        format = workbook.add_format({'color': 'white', 'bg_color': '#448595', 'bold': True, })
        return format

    def project_data_right(self, workbook):
        format = workbook.add_format({'color': 'white', 'bg_color': '#448595', 'bold': True, 'align': 'right' })
        return format

    def highlight_fail(self, workbook):
        format = workbook.add_format({'underline': True, 'color': 'white', 'num_format': '0.0', 'bold': True, 'bg_color': 'red', 'border': True, 'align': 'centre', 'valign': 'vcenter'})
        return format

    def highlight_pass(self, workbook):
        format = workbook.add_format({'underline': True, 'color': 'white', 'num_format': '0.0', 'bold': True, 'bg_color': 'green', 'border': True, 'align': 'centre', 'valign': 'vcenter'})
        return format

    def instructions_italics(self, workbook):
        format = workbook.add_format({'bg_color': '#DAE1E8', 'italic': True, 'size': 9})
        return format

    def instructions_bold(self, workbook):
        format = workbook.add_format({'bg_color': '#DAE1E8', 'bold': True, 'size': 9})
        return format

    def hyperlink(self, workbook):
        format = workbook.add_format({'bg_color': '#DAE1E8', 'underline': True, 'size': 9, 'color': 'blue'})
        return format

    def grey_background(self, workbook):
        format = workbook.add_format({'bg_color': '#DAE1E8'})
        return format

    def white_background(self, workbook):
        format = workbook.add_format({'color':'white', 'bg_color': 'white'})
        return format


def full_leed_unmet_load_hours_check(heating_threshold: float, cooling_threshold: float, simulation_name):
    global global_heating_threshold
    global_heating_threshold = heating_threshold
    global global_cooling_threshold
    global_cooling_threshold = cooling_threshold
    global book
    global summary

    book = xlsxwriter.Workbook(global_project_folder + '\\' + global_save_file_name + '.xlsx')

    if global_proposed_exists:
        proposed_worksheet = 'Proposed'
        proposed = book.add_worksheet(proposed_worksheet)
        p_aps_file = 'p_' + simulation_name + '.aps'

    if global_baseline000_exists:
        baseline000_worksheet = "Baseline_000_deg"
        baseline000 = book.add_worksheet(baseline000_worksheet)
        b000_aps_file = 'b[000]_' + simulation_name + '.aps'

    if global_baseline090_exists:
        baseline090_worksheet = "Baseline_090_deg"
        baseline090 = book.add_worksheet(baseline090_worksheet)
        b090_aps_file = 'b[090]_' + simulation_name + '.aps'

    if global_baseline180_exists:
        baseline180_worksheet = "Baseline_180_deg"
        baseline180 = book.add_worksheet(baseline180_worksheet)
        b180_aps_file = 'b[180]_' + simulation_name + '.aps'

    if global_baseline270_exists:
        baseline270_worksheet = "Baseline_270_deg"
        baseline270 = book.add_worksheet(baseline270_worksheet)
        b270_aps_file = 'b[270]_' + simulation_name + '.aps'

    if global_proposed_exists:
        unmet_load_hours_calculations(p_aps_file,proposed, proposed_worksheet)

    if global_baseline000_exists:
        unmet_load_hours_calculations(b000_aps_file, baseline000, baseline000_worksheet)

    if global_baseline090_exists:
        unmet_load_hours_calculations(b090_aps_file, baseline090, baseline090_worksheet)

    if global_baseline180_exists:
        unmet_load_hours_calculations(b180_aps_file, baseline180, baseline180_worksheet)

    if global_baseline270_exists:
        unmet_load_hours_calculations(b270_aps_file, baseline270, baseline270_worksheet)

    book.close()
    os.startfile(global_project_folder + '\\' + global_save_file_name + '.xlsx')


def unmet_load_hours_calculations(aps_file,
                                  worksheet,
                                  worksheet_name):
    """
    performs heating and cooling unmet load hours calculation for all rooms in the building
    :param aps_file: contains results from VE simulation
    :param worksheet: worksheet
    :param worksheet_name: worksheet name
    """
    def cooling_unmet_load_hours_check(np_room_temp: np.ndarray, np_cooling_set_point: np.ndarray, np_plant_profile, cooling_threshold: float):
        np_cooling_unmet_load_hour = np.zeros((1, 8760))

        daytime_cooling_set_point = np_cooling_set_point.min()
        night_setback_cooling_set_point = np_cooling_set_point.max()

        # adjust cooling set point profile to eliminate morning startup time
        adjusted_cooling_set_point = []
        for i in np_plant_profile:
            if i == 0:
                adjusted_cooling_set_point.append(night_setback_cooling_set_point)
            elif i >= 1:
                adjusted_cooling_set_point.append(daytime_cooling_set_point)

        np_adjusted_cooling_set_point = np.asarray(adjusted_cooling_set_point)

        np_cooling_unmet_load_hour = ((np_room_temp - cooling_threshold) >= np_adjusted_cooling_set_point).astype(int)

        return np_cooling_unmet_load_hour

    def heating_unmet_load_hours_check(np_room_temp: np.ndarray, np_heating_set_point: np.ndarray, np_plant_profile, heating_threshold: float):
        np_heating_unmet_load_hour = np.zeros((1,8760))

        daytime_heating_set_point = np_heating_set_point.max()
        night_setback_heating_set_point = np_heating_set_point.min()

        # adjust heating set point profile to eliminate morning startup time
        adjusted_heating_set_point = []

        for i in np_plant_profile:
            if i == 0:
                adjusted_heating_set_point.append(night_setback_heating_set_point)
            elif i >= 1:
                adjusted_heating_set_point.append(daytime_heating_set_point)

        np_adjusted_heating_set_point = np.asarray(adjusted_heating_set_point)

        np_heating_unmet_load_hour = ((np_room_temp + heating_threshold) <= np_adjusted_heating_set_point).astype(int)

        return np_heating_unmet_load_hour

    # create formats object to use when print to the excel sheet
    formats = xlsxFormats(book)

    # constants
    unmet_load_hours_limit = 300

    global_vista_results_reader.open_aps_data(aps_file)
    rooms = global_vista_results_reader.get_room_list()

    heating_unmet_load_problem_rooms = []
    cooling_unmet_load_problem_rooms = []

    # generates the arrays that will contain the unmet load hours data for every room in the building
    np_simultaneous_heating_umlh = np.zeros((1, 8760))
    np_simultaneous_cooling_umlh = np.zeros((1, 8760))
    np_simultaneous_heating_umlh_2 = np.zeros((1, 8760))
    np_simultaneous_cooling_umlh_2 = np.zeros((1, 8760))
    np_simultaneous_heating_umlh_3 = np.zeros((1, 8760))
    np_simultaneous_cooling_umlh_3 = np.zeros((1, 8760))

    # y variable is a cell reference used for printing to the excel sheet
    y = 10
    x_heating = 0
    x_cooling = x_heating + 8

    # y variable used for the titles to the table
    titles_y = y - 1

    # y variable used a cell reference to start printing the data for the problem rooms into the excel sheet
    problem_rooms_y = len(rooms) + y + 3

    # information to be printed
    number_of_rooms = len(rooms)
    number_of_problem_rooms = 0

    # make whole workbook white
    sheet_main_x = 15
    while sheet_main_x < 45:
        sheet_main_y = 0
        while sheet_main_y < len(rooms) + y + 2:
            worksheet.write(sheet_main_y, sheet_main_x, '', formats.white_background)
            sheet_main_y += 1
        sheet_main_x += 1

    # make top part of worksheet grey
    sheet_top_y = 0
    while sheet_top_y < 15:
        sheet_top_x = 0
        while sheet_top_x < 8:
            worksheet.write(sheet_top_x, sheet_top_y, '', formats.grey_background)
            sheet_top_x += 1
        sheet_top_y += 1

    # set background color under total row
    blank_line = 0
    while blank_line < 15:
        worksheet.write(y + number_of_rooms + 1, blank_line, '', formats.grey_background)
        worksheet.write(y + number_of_rooms + 2, blank_line, '', formats.grey_background)
        blank_line += 1

    while blank_line < 45:
        worksheet.write(y + number_of_rooms + 2, blank_line, '', formats.white_background)
        blank_line += 1

    #------------------------------------------------------------------------------------------------------------------
    # Main for loop that iterates through the list of rooms
    #------------------------------------------------------------------------------------------------------------------
    for room_number, room in enumerate(rooms):
        # unpack the tuples of room data that is returned from the ResultsReader function. the variables 'a' and 'b' and not used here but had to be assigned to something
        name, room_id, _, _ = room

        if room_number%10 == 0 and room_number + 10 < number_of_rooms:
            print('Calculating Rooms: ' + str(room_number + 1) + ' - ' + str(room_number + 10) + ' of ' + str(number_of_rooms) + ' in ' + worksheet_name)
        elif room_number%10 == 0 and room_number + 10 >= number_of_rooms:
            print('Calculating Rooms: ' + str(room_number + 1) + ' - ' + str(number_of_rooms) + ' of ' + str(number_of_rooms) + ' in ' + worksheet_name)

        def get_vista_room_results(aps_var: str, vista_var: str):
            results = global_vista_results_reader.get_room_results(room_id, aps_var, vista_var, 'z', 1, 365)

            if results is None:
                raise ValueError("Invalid Room Results.")

            return results

        # get variables from aps file that are required for unmet load hours check
        np_room_temp = get_vista_room_results('Room air temperature', 'Air temperature')
        np_heating_set_point = get_vista_room_results('Heating set point', 'Heating set point')
        np_cooling_set_point = get_vista_room_results('Cooling set point', 'Cooling set point')
        np_plant_profile = get_vista_room_results('Plant profile', 'Plant profile')

        # heating unmet load hours
        heating_unmet_load_hour = heating_unmet_load_hours_check(np_room_temp, np_heating_set_point, np_plant_profile, global_heating_threshold)
        heating_unmet_load_hour_2 = heating_unmet_load_hours_check(np_room_temp, np_heating_set_point, np_plant_profile, global_heating_threshold + 1)
        heating_unmet_load_hour_3 = heating_unmet_load_hours_check(np_room_temp, np_heating_set_point, np_plant_profile, global_heating_threshold + 2)

        # cooling unmet load hours
        cooling_unmet_load_hour = cooling_unmet_load_hours_check(np_room_temp, np_cooling_set_point, np_plant_profile, global_cooling_threshold)
        cooling_unmet_load_hour_2 = cooling_unmet_load_hours_check(np_room_temp, np_cooling_set_point, np_plant_profile, global_cooling_threshold + 1)
        cooling_unmet_load_hour_3 = cooling_unmet_load_hours_check(np_room_temp, np_cooling_set_point, np_plant_profile, global_cooling_threshold + 2)

        # adds heating unmet load hours array for each room to another array so that the simultaneous unmet load hours can be calculated
        np_simultaneous_heating_umlh += heating_unmet_load_hour
        np_simultaneous_heating_umlh_2 += heating_unmet_load_hour_2
        np_simultaneous_heating_umlh_3 += heating_unmet_load_hour_3

        # adds cooling unmet load hours array for each room to another array so that the simultaneous unmet load hours can be calculated
        np_simultaneous_cooling_umlh += cooling_unmet_load_hour
        np_simultaneous_cooling_umlh_2 += cooling_unmet_load_hour_2
        np_simultaneous_cooling_umlh_3 += cooling_unmet_load_hour_3

        occupied_max_temp = np_room_temp * np_plant_profile

        max_temp = occupied_max_temp.max()

        # calculated the minimum temperature during occupied times
        occupied_min_temp = np_room_temp * np_plant_profile
        min_temp_list = []
        for item in occupied_min_temp:
            if item == 0:
                min_temp_list.append(100)
            else:
                min_temp_list.append(item)

        np_min_temp_array = np.zeros((1, 8760))
        np_min_temp_array = np.asarray(min_temp_list)
        min_temp = np_min_temp_array.min()

        # get the index of the row where this max occurs
        min_temp_index = np_min_temp_array.argmin()
        # get the number of the day the max occurs by dividing by 24 and rounding the result down to the nearest integer
        min_temp_day_number = math.floor(min_temp_index / 24)
        # get the temperature and cooling setpoint values for each hour of the day that the peak occurs
        min_day_air_temp = np_room_temp[24 * min_temp_day_number:24 * min_temp_day_number + 24]
        min_day_heating_setpoint = np_heating_set_point[24 * min_temp_day_number:24 * min_temp_day_number + 24]
        min_day_plant_profile = np_plant_profile[24 * min_temp_day_number:24 * min_temp_day_number + 24]
        # convert the day number to a date to be used in the excel sheet
        min_date = datetime.datetime(2000, 1, 1) + datetime.timedelta(min_temp_day_number + 1)
        min_date = min_date.strftime('%d %b')

        # get the index of the row where this max occurs
        max_temp_index = (np_room_temp * np_plant_profile).argmax()

        # get the number of the day the max occurs by dividing by 24 and rounding the result down to the nearest integer
        max_temp_day_number = math.floor(max_temp_index / 24)

        # get the temperature and cooling setpoint values for each hour of the day that the peak occurs
        max_day_air_temp = np_room_temp[24 * max_temp_day_number:24 * max_temp_day_number + 24]
        max_day_cooling_setpoint = np_cooling_set_point[24 * max_temp_day_number:24 * max_temp_day_number + 24]
        max_day_plant_profile = np_plant_profile[24 * max_temp_day_number:24 * max_temp_day_number + 24]
        max_date = datetime.datetime(2000, 1, 1) + datetime.timedelta(max_temp_day_number + 1)
        max_date = max_date.strftime('%d %b')

        # combines all of the data required for each room into a single list so it can be printed to the excel sheet
        heating_unmet_loads_data = [name, min_date, min_temp,
                                    min_day_heating_setpoint.max(),
                                    heating_unmet_load_hour.sum(),
                                    heating_unmet_load_hour_2.sum(),
                                    heating_unmet_load_hour_3.sum()]
        cooling_unmet_loads_data = [name, max_date, max_temp,
                                    max_day_cooling_setpoint.min(),
                                    cooling_unmet_load_hour.sum(),
                                    cooling_unmet_load_hour_2.sum(),
                                    cooling_unmet_load_hour_3.sum()]

        # prints the unmet load hours data for each room to the excel sheet
        worksheet.write_row(y, x_heating, heating_unmet_loads_data, formats.table_main)
        worksheet.write_row(y, x_cooling, cooling_unmet_loads_data, formats.table_main)

        # used to create the hyperlink formulae to jump to the graphs
        hyperlink = '=HYPERLINK("[' + global_save_file_name + '.xlsx]' + worksheet_name + '!H' + str(problem_rooms_y) + '","'

        x_peak_data = 15

        # chart properties
        chart_size = {'x_scale': 1.691, 'y_scale': 0.9}
        chart_area_format = {'border':{'none': False}, 'gradient': {'colors': ['#DAE1E8', '#448595']}}
        chart_plot_format = {'border':{'none': False}, 'gradient': {'colors': ['#DAE1E8', '#448595']}}

        # -------------------------------------------------------------------------------------------------------------
        # highlight the problem rooms in color and print graphs for peak heating day
        # -------------------------------------------------------------------------------------------------------------

        if heating_unmet_load_hour.sum() >= unmet_load_hours_limit:
            heating_unmet_load_problem_rooms.append(name)

            # make empty cells white beside graphs
            sheet_main_x = 15
            while sheet_main_x < 45:
                sheet_main_y = problem_rooms_y
                while sheet_main_y < problem_rooms_y + 16:
                    # excludes cells that contain the information for the graphs
                    if sheet_main_y == problem_rooms_y + 0 or sheet_main_y == problem_rooms_y + 1 or sheet_main_y == problem_rooms_y + 2:
                        sheet_main_y += 1
                    else:
                        worksheet.write(sheet_main_y, sheet_main_x, '', formats.white_background)
                        sheet_main_y += 1
                sheet_main_x += 1

            # creates hyperlink to graphs and highlights problem rooms in yellow
            worksheet.write_formula(y, x_heating, hyperlink + name + '")', formats.highlight_fail)
            worksheet.write_formula(y, x_heating+1, hyperlink + str(min_date) + '")', formats.highlight_fail)
            worksheet.write_formula(y, x_heating+2, hyperlink + str(round(min_temp, 1)) + '")', formats.highlight_fail)
            worksheet.write_formula(y, x_heating+3, hyperlink + str(round(min_day_heating_setpoint.max(), 1)) + '")', formats.highlight_fail)
            worksheet.write_formula(y, x_heating+4, hyperlink + str(heating_unmet_load_hour.sum()) + '")', formats.highlight_fail)

            # writes peak day data to be used in the graphs
            worksheet.write(problem_rooms_y, x_peak_data, 'Air Temperature', formats.white_background)
            worksheet.write_row(problem_rooms_y, x_peak_data+1, min_day_air_temp, formats.white_background)
            worksheet.write(problem_rooms_y+1, x_peak_data, 'Heating Setpoint', formats.white_background)
            worksheet.write_row(problem_rooms_y+1, x_peak_data+1, min_day_heating_setpoint, formats.white_background)
            worksheet.write(problem_rooms_y+2, x_peak_data, 'Plant Profile', formats.white_background)
            worksheet.write_row(problem_rooms_y+2, x_peak_data+1, min_day_plant_profile, formats.white_background)
            # writes blank cells after the data for graphs
            worksheet.write_row(problem_rooms_y + 0, x_peak_data + 25, ['', '', '', '', ''], formats.white_background)
            worksheet.write_row(problem_rooms_y + 1, x_peak_data + 25, ['', '', '', '', ''], formats.white_background)
            worksheet.write_row(problem_rooms_y + 2, x_peak_data + 25, ['', '', '', '', ''], formats.white_background)

            chart = book.add_chart({'type': 'line', 'height': '10'})

            # print title for graph in merged cells
            worksheet.merge_range('A' + str(problem_rooms_y) + ':G' + str(problem_rooms_y), 'Peak Day for Heating (' + str(min_date)+ ') - ' + name, formats.table_title)

            # insert chart after defining data and properties
            if chart:
                chart.add_series({'name': "='" + worksheet_name + "'!$P$" + str(problem_rooms_y + 1), 'values': "='" + worksheet_name + "'!$Q$" + str(problem_rooms_y + 1) + ":$AN$" + str(problem_rooms_y + 1)})
                chart.add_series({'name': "='" + worksheet_name + "'!$P$" + str(problem_rooms_y + 2), 'values': "='" + worksheet_name + "'!$Q$" + str(problem_rooms_y + 2) + ":$AN$" + str(problem_rooms_y + 2)})
                chart.add_series({'y2_axis': True, 'name': "='" + worksheet_name + "'!$P$" + str(problem_rooms_y + 3), 'values': "='" + worksheet_name + "'!$Q$" + str(problem_rooms_y + 3) + ":$AN$" + str(problem_rooms_y+3)})

                heating_graph_min_temp = round(min(min(max_day_air_temp), min(min_day_heating_setpoint)) - 5, - 1)
                heating_graph_max_temp = round(max(max(max_day_air_temp), max(min_day_heating_setpoint)) + 5, - 1)

                chart.set_y_axis({'name': 'Temperature (\u2070C)', 'min': heating_graph_min_temp, 'max': heating_graph_max_temp})
                chart.set_y2_axis({'name': 'Plant Profile', 'min': '0','max': '1'})
                chart.set_chartarea(chart_area_format)
                chart.set_plotarea(chart_plot_format)
                worksheet.insert_chart(problem_rooms_y, x_heating, chart, chart_size)

        # get max temp during conditioned time by multiplying by plant profile
        max_temp = (np_room_temp * np_plant_profile).max()

        # -------------------------------------------------------------------------------------------------------------
        # highlight the problem rooms in color and print graphs for peak cooling day
        # -------------------------------------------------------------------------------------------------------------
        if cooling_unmet_load_hour.sum() >= unmet_load_hours_limit:
            cooling_unmet_load_problem_rooms.append(name)

            # make empty cells white beside graphs
            sheet_main_x = 15
            while sheet_main_x < 45:
                sheet_main_y = problem_rooms_y
                while sheet_main_y < problem_rooms_y + 16:
                        # excludes cells that contain the information for the graphs
                    if sheet_main_y == problem_rooms_y + 5 or sheet_main_y == problem_rooms_y + 6 or sheet_main_y == problem_rooms_y + 7:
                        sheet_main_y += 1
                    elif heating_unmet_load_hour.sum() >= unmet_load_hours_limit and sheet_main_y == problem_rooms_y + 0:
                        sheet_main_y += 1
                    elif heating_unmet_load_hour.sum() >= unmet_load_hours_limit and sheet_main_y == problem_rooms_y + 1:
                        sheet_main_y += 1
                    elif heating_unmet_load_hour.sum() >= unmet_load_hours_limit and sheet_main_y == problem_rooms_y + 2:
                        sheet_main_y += 1
                    else:
                        worksheet.write(sheet_main_y, sheet_main_x, '', formats.white_background)
                        sheet_main_y += 1
                sheet_main_x += 1

            # creates hyperlink to graphs and highlights problem rooms in yellow
            worksheet.write_formula(y, x_cooling, hyperlink + name + '")', formats.highlight_fail)
            worksheet.write_formula(y, x_cooling+1, hyperlink + str(max_date) + '")', formats.highlight_fail)
            worksheet.write_formula(y, x_cooling+2, hyperlink + str(round(max_temp, 1)) + '")', formats.highlight_fail)
            worksheet.write_formula(y, x_cooling+3, hyperlink + str(round(max_day_cooling_setpoint.min(), 1)) + '")', formats.highlight_fail)
            worksheet.write_formula(y, x_cooling+4, hyperlink + str(cooling_unmet_load_hour.sum()) + '")', formats.highlight_fail)

            # writes peak day data to be used in the graphs
            worksheet.write(problem_rooms_y + 5, x_peak_data, 'Air Temperature', formats.white_background)
            worksheet.write_row(problem_rooms_y + 5, x_peak_data+1, max_day_air_temp, formats.white_background)
            worksheet.write_row(problem_rooms_y + 5, x_peak_data+24,['', '', '', '', ''], formats.white_background)
            worksheet.write(problem_rooms_y + 6, x_peak_data, 'Cooling Setpoint', formats.white_background)
            worksheet.write_row(problem_rooms_y + 6, x_peak_data+1, max_day_cooling_setpoint, formats.white_background)
            worksheet.write(problem_rooms_y + 7, x_peak_data, 'Plant Profile', formats.white_background)
            worksheet.write_row(problem_rooms_y + 7, x_peak_data+1, max_day_plant_profile, formats.white_background)

            # writes blank cells after the data for graphs
            worksheet.write_row(problem_rooms_y + 5, x_peak_data + 25, ['', '', '', '', ''], formats.white_background)
            worksheet.write_row(problem_rooms_y + 6, x_peak_data + 25, ['', '', '', '', ''], formats.white_background)
            worksheet.write_row(problem_rooms_y + 7, x_peak_data + 25, ['', '', '', '', ''], formats.white_background)

            chart = book.add_chart({'type': 'line', 'height': '10'})

            # print title for graph in merged cells
            worksheet.merge_range('I' + str(problem_rooms_y) + ':O' + str(problem_rooms_y), 'Peak Day for Cooling (' + str(max_date) + ') - ' + name, formats.table_title)

            # insert chart after defining data and properties
            if chart:
                chart.add_series({'name': "='" + worksheet_name + "'!$P$"+str(problem_rooms_y+6), 'values': "='" + worksheet_name + "'!$Q$" + str(problem_rooms_y+6) + ":$AN$" + str(problem_rooms_y+6)})
                chart.add_series({'name': "='" + worksheet_name + "'!$P$"+str(problem_rooms_y+7), 'values': "='" + worksheet_name + "'!$Q$" + str(problem_rooms_y+7) + ":$AN$" + str(problem_rooms_y+7)})
                chart.add_series({'y2_axis': True, 'name': "='" + worksheet_name + "'!$P$"+str(problem_rooms_y+8), 'values': "='" + worksheet_name + "'!$Q$" + str(problem_rooms_y+8) + ":$AN$" + str(problem_rooms_y+8)})

                cooling_graph_min_temp = round(min(min(max_day_air_temp), min(max_day_cooling_setpoint)) - 5, - 1)
                cooling_graph_max_temp = round(max(max(max_day_air_temp), max(max_day_cooling_setpoint)) + 5, - 1)

                chart.set_y_axis({'name': 'Temperature (\u2070C)', 'min': cooling_graph_min_temp, 'max': cooling_graph_max_temp})
                chart.set_y2_axis({'name': 'Plant Profile', 'min': '0', 'max': '1'})
                chart.set_chartarea(chart_area_format)
                chart.set_plotarea(chart_plot_format)
                worksheet.insert_chart(problem_rooms_y, x_cooling, chart, chart_size)

        # -------------------------------------------------------------------------------------------------------------
        # if unmet load hours data has been printed to excel for this room then increment the y co-ordinate by 16 so that the next room data will be printed correctly
        # -------------------------------------------------------------------------------------------------------------

        if heating_unmet_load_hour.sum() >= unmet_load_hours_limit or cooling_unmet_load_hour.sum() >= unmet_load_hours_limit:

            # merge cells between graphs for hyperlink
            worksheet.merge_range('H' + str(problem_rooms_y) + ':H' + str(problem_rooms_y+13), '', formats.grey_background)

            # write grey cells
            grey_y = problem_rooms_y
            while grey_y < problem_rooms_y + 16:
                grey_x = 0
                while grey_x < 15:
                    worksheet.write(grey_y, grey_x, '', formats.grey_background)
                    grey_x += 1
                grey_y += 1

            problem_rooms_y += 16
            number_of_problem_rooms += 1

        # set background color of cell in between the two tables
        worksheet.write(y, 7, '', formats.grey_background)

        # y variable is a cell reference used for printing to the excel sheet
        y += 1

    # set rows below graph to white
    bottom_y = problem_rooms_y
    while bottom_y < problem_rooms_y + 50:
        bottom_x = 0
        while bottom_x < 45:
            worksheet.write(bottom_y, bottom_x, '', formats.white_background)
            bottom_x += 1
        bottom_y += 1

    # set background color of cell in between the two tables
    worksheet.write(y, 7, '', formats.grey_background)

    # generates an array which shows '1' for each hour when the load is not met in any room in the building

    np_simultaneous_heating_umlh[np_simultaneous_heating_umlh > 0] = 1
    np_simultaneous_heating_umlh_2[np_simultaneous_heating_umlh_2 > 0] = 1
    np_simultaneous_heating_umlh_3[np_simultaneous_heating_umlh_3 > 0] = 1

    np_simultaneous_cooling_umlh[np_simultaneous_cooling_umlh > 0] = 1
    np_simultaneous_cooling_umlh_2[np_simultaneous_cooling_umlh_2 > 0] = 1
    np_simultaneous_cooling_umlh_3[np_simultaneous_cooling_umlh_3 > 0] = 1

    # sums the array generated in the previous step to calculate the total simultaneous unmet load hours
    total_heating_umlh = np_simultaneous_heating_umlh.sum()
    total_heating_umlh_2 = np_simultaneous_heating_umlh_2.sum()
    total_heating_umlh_3 = np_simultaneous_heating_umlh_3.sum()
    total_cooling_umlh = np_simultaneous_cooling_umlh.sum()
    total_cooling_umlh_2 = np_simultaneous_cooling_umlh_2.sum()
    total_cooling_umlh_3 = np_simultaneous_cooling_umlh_3.sum()

    # combines the total unmet load hours for each threshold calculation into a single list so it can be printed to the excel sheet
    total_heating_unmet_load_hours_list = ['Total', '', '', '', total_heating_umlh, total_heating_umlh_2, total_heating_umlh_3]
    total_cooling_unmet_load_hours_list = ['Total', '', '', '', total_cooling_umlh, total_cooling_umlh_2, total_cooling_umlh_3]

    # prints unmet load hours totals to the excel sheet
    worksheet.write_row(y, x_heating, total_heating_unmet_load_hours_list, formats.table_total)
    worksheet.write_row(y, x_cooling, total_cooling_unmet_load_hours_list, formats.table_total)

    # prints titles to the excel sheet
    worksheet.merge_range('A' + str(titles_y) + ':G' + str(titles_y), 'Heating Unmet Load Hours', formats.table_title)
    worksheet.merge_range('I' + str(titles_y) + ':O' + str(titles_y), 'Cooling Unmet Load Hours', formats.table_title)

    # set background color of cell in between the two tables
    worksheet.write(titles_y, 7, '', formats.grey_background)
    worksheet.write(titles_y - 1, 7, '', formats.grey_background)

    titles_heating = ['Room Name', 'Min Temp Date', 'Min Temp During Operating Hours (\u2070C)', 'Heating Setpoint During Operating Hours (\u2070C)', '', '', '']
    titles_cooling = ['Room Name', 'Max Temp Date', 'Max Temp During Operating Hours (\u2070C)', 'Cooling Setpoint During Operating Hours (\u2070C)', '', '', '']

    worksheet.write_row(titles_y, x_heating, titles_heating, formats.table_total)
    worksheet.write_row(titles_y, x_cooling, titles_cooling, formats.table_total)

    worksheet.write('E' + str(titles_y + 1), 'Threshold ' + str(global_heating_threshold) + ' \u2070C', formats.table_total)
    worksheet.write('F' + str(titles_y + 1), 'Threshold ' + str(global_heating_threshold+1) + ' \u2070C', formats.table_total)
    worksheet.write('G' + str(titles_y + 1), 'Threshold ' + str(global_heating_threshold+2) + ' \u2070C', formats.table_total)

    worksheet.write('M' + str(titles_y + 1), 'Threshold ' + str(global_cooling_threshold) + ' \u2070C', formats.table_total)
    worksheet.write('N' + str(titles_y + 1), 'Threshold ' + str(global_cooling_threshold+1) + ' \u2070C', formats.table_total)
    worksheet.write('O' + str(titles_y + 1), 'Threshold ' + str(global_cooling_threshold+2) + ' \u2070C', formats.table_total)

    # print project info at the top of sheet

    building = worksheet_name.split('_')
    building = building[0]
    date_created = time.ctime(os.path.getctime(global_project_data.path + 'Vista\\' + aps_file))

    project_info = [global_project_data.name, global_project_data.path, aps_file, 'Simulated on: ' + date_created]
    worksheet.write_column('C2', project_info, formats.project_data_left)
    worksheet.write_column('D2', ['', '', '', ''], formats.project_data_left)
    worksheet.write_column('E2', ['', '', '', ''], formats.project_data_left)
    worksheet.write_column('F2', ['', '', '', ''], formats.project_data_left)
    worksheet.write_column('G2', ['', '', '', ''], formats.project_data_left)

    project_info = [building, str(number_of_rooms) + ' Zones In The Model', str(number_of_rooms) + ' Zones Analysed', str(number_of_problem_rooms) + ' Problem Rooms']
    worksheet.write_column('I2', project_info, formats.project_data_left)
    worksheet.write_column('J2', ['', '', '', ''], formats.project_data_left)

    # edits columns widths where needed
    worksheet.set_column('A:A', 25)
    worksheet.set_column('I:I', 25)
    worksheet.set_column('C:D', 20)
    worksheet.set_column('E:G', 12)
    worksheet.set_column('K:L', 20)
    worksheet.set_column('M:O', 12)
    worksheet.set_column('H:H', 1)
    worksheet.set_column('B:B', 10)
    worksheet.set_column('J:J', 10)
    worksheet.set_row(8, 35)

    worksheet.freeze_panes(titles_y + 1, 0)

    # get installation location of the VE and get logo image for excel sheet
    ve_install_folder = global_ve_install_folder.split("\\")
    ve_install_folder = ("\\\\").join(ve_install_folder)
    worksheet.insert_image('A2', 'IESlogo.png', {'x_offset': 5, 'y_offset': 0})

    # write instructions and hyperlinks at top of sheet
    worksheet.write('A7', 'Room with greater than 300 unmet load hours are highlighted below. Click on the highlighted rooms to see a graph of the peak day', formats.instructions_italics)
    worksheet.write_url('A8', 'http://www.iesve.com/support/faq/pdf/unmet-load-hours.pdf', formats.hyperlink, 'click here for guidance and addressing unmet load hours')

    worksheet.write_formula('O8', '=HYPERLINK("[' + global_save_file_name + '.xlsx]' + worksheet_name + '!A' + str(titles_y + 2) + '", "Back to the Top")', formats.hyperlink)

    print(worksheet_name + ' Unmet Load Hours Calculation Complete')
    print('Heating Unmet Load Hours = ' + str(total_heating_umlh))
    print('Cooling Unmet Load Hours = ' + str(total_cooling_umlh))
    print('---------------------------------------------------------------------')
    print('---------------------------------------------------------------------')


# -------------------------------------------------------------------------------------------------------------
# generates the UI window using tkinter
# -------------------------------------------------------------------------------------------------------------
def generate_window(vista_results_reader: iesve.ResultsReader, project, ve_folder):
    # set global variables
    global global_project_data
    global_project_data = project

    global global_project_folder
    global_project_folder = global_project_data.path
    print(global_project_folder)

    global global_vista_results_reader
    global_vista_results_reader = vista_results_reader
    global global_ve_folder
    global_ve_folder = ve_folder
    global global_ve_install_folder
    global_ve_install_folder = ve_folder

    class Window(Frame):
        def __init__(self, master):
            Frame.__init__(self, master)

            self.master: Tk = master

            self.init_window()

        # Creation of init_window
        def init_window(self):
            # changing the title of our master widget
            self.master.title("Unmet Load Hours Check")

            # allowing the widget to take the full space of the root window
            self.pack(fill=BOTH, expand=1)

            label_1 = Label(self, text='Select the Results File From Vista Folder')
            label_1.grid(row=0, sticky=W)

            # creating a button instance
            get_aps_file_name_Button = Button(self, text="Browse", command=self.get_aps_file_name)

            # placing the button on my window
            get_aps_file_name_Button.grid(row=1, sticky=W)

            heating_label = Label(self, text='Set Heating Threshold for Unmet Load Hours:')
            heating_label.grid(row=2, sticky=W)

            global heating_entry_box
            heating_entry_box = Entry(self)
            heating_entry_box.insert(0, str(1))
            heating_entry_box.grid(row=2, column=2, sticky=E)

            cooling_label = Label(self, text='Set Cooling Threshold for Unmet Load Hours:')
            cooling_label.grid(row=3, sticky=W)

            global cooling_entry_box
            cooling_entry_box = Entry(self)
            cooling_entry_box.insert(0, str(1))
            cooling_entry_box.grid(row=3, column=2, sticky=E)

            save_file_label_1 = Label(self, text='Excel sheet will be saved in the Project Folder')
            save_file_label_1.grid(row=17, sticky=W)

            save_file_label_2 = Label(self, text='Name the Results File:')
            save_file_label_2.grid(row=18, sticky=W)

            global save_file_entry_box
            save_file_entry_box = Entry(self)
            save_file_entry_box.insert(0,'VE_Results')
            save_file_entry_box.grid(row=19, sticky=W)

            # creating a button instance
            run_calc_Button = Button(self, text="Calculate Unmet Load Hours", command=self.run_calc)

            # placing the button on my window
            run_calc_Button.grid(row=20, sticky=W)
            notes_label_1 = Label(self, text='Notes:')
            notes_label_2 = Label(self, text='Please note that this script only analyses unmet load hours during occupied times')
            notes_label_3 = Label(self, text='It does not take into account unoccupied times. It therefore should not be used as')
            notes_label_4 = Label(self, text='a replacement for the main unmet load hours check performed by the software. It ')
            notes_label_5 =  Label(self, text='is only intended to be used as a tool to help troubleshoot a model.')

            notes_label_1.grid(row=21, sticky=W)
            notes_label_2.grid(row=22, sticky=W)
            notes_label_3.grid(row=23, sticky=W)
            notes_label_4.grid(row=24, sticky=W)
            notes_label_5.grid(row=25, sticky=W)

            self.proposed_chk_var = IntVar()
            self.proposed_chk_var.set(0)

            self.baseline000_chk_var = IntVar()
            self.baseline000_chk_var.set(0)

            self.baseline090_chk_var = IntVar()
            self.baseline090_chk_var.set(0)

            self.baseline180_chk_var = IntVar()
            self.baseline180_chk_var.set(0)

            self.baseline270_chk_var = IntVar()
            self.baseline270_chk_var.set(0)

            self.simulation_name = ""

        def get_aps_file_name(self):
            sim_name = filedialog.askopenfilename()

            # get file name from file path
            sim_name = sim_name.split('/')
            sim_name = sim_name[-1]

            # remove .aps from file name
            sim_name = sim_name.split('.')
            self.simulation_name = sim_name[0]

            # remove prefix p_ or b[000]_ from the file name
            if self.simulation_name.startswith('p_') or self.simulation_name.startswith('b[000]_') or self.simulation_name.startswith('b[090]_') or \
            self.simulation_name.startswith('b[180]_') or self.simulation_name.startswith('b[270]_'):
                self.simulation_name = self.simulation_name.split('_', 1)
                self.simulation_name = self.simulation_name[1]

            print('Simulation Name: ' + self.simulation_name)

            # checks to see if the results files exist. If they exist, it creates a checkbox for them
            if os.path.isfile(global_project_data.path + 'Vista\\p_'+self.simulation_name+'.aps'):
                proposed_chk = Checkbutton(self, text='p_'+self.simulation_name+'.aps', variable=self.proposed_chk_var, onvalue=1, offvalue=0)
                proposed_chk.grid(row=10, sticky=W)

            if os.path.isfile(global_project_data.path + 'Vista\\b[000]_' + self.simulation_name + '.aps'):
                baseline000_chk = Checkbutton(self, text='b[000]_' + self.simulation_name + '.aps', variable=self.baseline000_chk_var, onvalue=1, offvalue=0)
                baseline000_chk.grid(row=11, sticky=W)

            if os.path.isfile(global_project_data.path + 'Vista\\b[090]_' + self.simulation_name + '.aps'):
                baseline090_chk = Checkbutton(self, text='b[090]_' + self.simulation_name+ '.aps', variable=self.baseline090_chk_var, onvalue=1, offvalue=0)
                baseline090_chk.grid(row=12, sticky=W)

            if os.path.isfile(global_project_data.path + 'Vista\\b[180]_' + self.simulation_name + '.aps'):
                baseline180_chk = Checkbutton(self, text='b[180]_' + self.simulation_name + '.aps', variable=self.baseline180_chk_var, onvalue=1, offvalue=0)
                baseline180_chk.grid(row=13, sticky=W)

            if os.path.isfile(global_project_data.path + 'Vista\\b[270]_' + self.simulation_name + '.aps'):
                baseline270_chk = Checkbutton(self, text='b[270]_' + self.simulation_name + '.aps', variable=self.baseline270_chk_var, onvalue=1, offvalue=0)
                baseline270_chk.grid(row=14, sticky=W)

        def run_calc(self):
            global global_save_file_name
            global_save_file_name = save_file_entry_box.get()

            # determines which results files the user wants to run the calc for
            global global_proposed_exists
            global global_baseline000_exists
            global global_baseline090_exists
            global global_baseline180_exists
            global global_baseline270_exists

            global_proposed_exists = False
            global_baseline000_exists = False
            global_baseline090_exists = False
            global_baseline180_exists = False
            global_baseline270_exists = False

            if self.proposed_chk_var.get() == 0:
                global_proposed_exists = False
            else:
                global_proposed_exists = True

            if self.baseline000_chk_var.get() == 0:
                global_baseline000_exists = False
            else:
                global_baseline000_exists = True

            if self.baseline090_chk_var.get() == 0:
                global_baseline090_exists = False
            else:
                global_baseline090_exists = True

            if self.baseline180_chk_var.get() == 0:
                global_baseline180_exists = False
            else:
                global_baseline180_exists = True

            if self.baseline270_chk_var.get() == 0:
                global_baseline270_exists = False
            else:
                global_baseline270_exists = True

            # gets threshold temperatures
            heating_threshold = float(heating_entry_box.get())
            cooling_threshold = float(cooling_entry_box.get())

            full_leed_unmet_load_hours_check(heating_threshold, cooling_threshold, self.simulation_name)

    root = Tk()

    def no_op():
        pass

    root.after(1, no_op)
    Window(root)
    root.mainloop()


if __name__  == '__main__':
    main()