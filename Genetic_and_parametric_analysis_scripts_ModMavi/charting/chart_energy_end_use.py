"""
========================
Energy end use bar chart
========================

Module description
------------------
Creates energy end use stacked bar charting for a specific set of output variables
generated from a single csv file from either parametric_sensitivity.py or
parametric_uncertainty.py

Each csv contains the scenario run #, model changes and multiple output metrics; the
csv should contain all or some of the specific outputs for energy end-use contained
in the end_uses dict.

Notes:

The script will adjust to accommodate the available specific outputs for energy
end-use that are in the csv file
The script will not chart variables not in the specific output list (above)
The csv can contain more outputs than in the specific output list (above)
Depending on the number of runs adjust fig = px.bar(...., width=2000, ...) to get
a readable chart

"""

import pandas as pd
import plotly.express as px
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename


def stacked_bar(df):
     """ Creates a stacked bar chart of energy end uses

     Args:
          df (pandas df) : list of analysis and output values
     """

     # Define all energy end-uses and associated colors for the chart in a dict
     # Note 'Wind_PV_kWh/m2' is negative signed
     # https://www.w3schools.com/cssref/css_colors.asp
     end_uses = {
               'Interior_lighting_kWh/m2': 'Gold',
               'Exterior_lighting_kWh/m2': 'GoldenRod',
               'Space_heating_(gas)_kWh/m2': 'FireBrick',
               'Space_heating_(elec)_kWh/m2': 'IndianRed',
               'Space_cooling_kWh/m2': 'DeepSkyBlue',
               'Pumps_kWh/m2': 'SeaGreen',
               'Fans_interior_kWh/m2': 'MediumSeaGreen',
               'DHW_heating_kWh/m2': 'DarkOrange',
               'Receptacle_equipment_kWh/m2': 'MediumSlateBlue',
               'Elevators_escalators_kWh/m2': 'Crimson',
               'Data_center_equipment_kWh/m2': 'DarkSlateBlue',
               'Cooking_(gas)_kWh/m2': 'DarkBlue',
               'Cooking_(elec)_kWh/m2': 'Blue',
               'Refrigeration_kWh/m2': 'RoyalBlue',
               'Wind_PV_kWh/m2': 'YellowGreen'
               }

     # Drop any end uses if not a df column name
     # You cannot iterate over what you change so use a list comprehension to make a new dict
     end_uses2 = {k:v for (k,v) in end_uses.items() if k in df.columns}

     # Check we have something to chart or show a message
     if len(end_uses2)==0:
          messagebox.showwarning('Error', 'There is no energy end use data in the selected csv file')
          quit()

     # Create chart
     # df is in wide data format
     title = 'Energy end use'
     fig = px.bar(df, x=df['run'], y=list(end_uses2.keys()), color_discrete_map=end_uses2,
               width=2000, height=750, title=title, barmode = 'relative')

     # Set options
     fig.update_layout(legend={'title_text':''})     # legend at side
     #fig.update_layout(legend=dict(title_text='',orientation="h"))    # legend at bottom
     fig.update_layout(font={'size':12, 'family':'Arial', 'color':'gray'})
     fig.update_layout(title={'y':0.9,'x':0.5,'xanchor': 'center','yanchor': 'bottom'})
     fig.update_xaxes(title_text='Run', tickangle=90, tickvals=df['run'],ticktext=df['run'])
     fig.update_yaxes(title_text='Annual consumption (kWh/m2)')
     fig.update_traces(textfont_size=8, textangle=0, textposition="outside")
     fig.update(layout_coloraxis_showscale=False)

     fig.show()

# Main loop
if __name__ == "__main__":

     # Ask user for csv file
     root = tk.Tk()
     simulations_output_name = askopenfilename(title='Choose CSV file', filetypes=[("csv file(*.csv)","*.csv")])
     root.destroy() # Removes Tkinter dialog popup window

     # Load the csv file in to a dataframe
     df = pd.read_csv(simulations_output_name)

     # Plot stacked bar chart
     stacked_bar(df)
