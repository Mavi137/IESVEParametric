"""
=========================
Parallel coordinate chart
=========================

Module description
------------------
Creates a parallel coordinate chart from a csv file generated from parametric_uncertainty.py

The csv contains the scenario run #, model changes and multiple output metrics. The csv
can be edited e.g. deleting any output metric columns that are not wanted before running
this charting script.

The script will remove any columns defined in the cols_delete list (see main loop
section); by default this is set-up for the energy end-use variables.

The script will remove any unused columns (all values = 0) and automatically generates
axes labels, the axes (dimensions) and  the Parcoords dimensions list using a list
comprehension. This script can be run from any suitable IDE (as iesve is not required).

Notes
-----
Delete any rows if desired
Delete any output metric columns in the csv if desired
Revise colorscale for different colour ranges if desired
Adjust tickvals > step value to better suit data if desired (0.5 seems reasonable)
Add a title (see title var in script) if desired
Refer to Plotly Parcoords chart help pages for usage, in summary:
- There is an icon top right for saving the chart as a png
- Drag one or more bars along an axis to create filter regions (a crosshair appears);
  you can add filters to all axes including the 'run' axis so you can:
  - track-back from outputs to see what runs are the source
  - track-forward from runs to see what the outputs are
  - filter input axes to narrow down runs that  meet input constraints
  - filter output axes to show runs that meet a desired threshold
  - Once filter bars exist drag the ends of the bar to adjust the range
  - Drag the axis names left or right to rearrange the order of the axes
"""

import math
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import tkinter as tk
from tkinter.filedialog import askopenfilename

def para_coord(df, simulations_output_name, cols_delete):
     """ Creates a parallel coordinate diagram
         Utilizes the Plotly lib

     Args:
          df (pandas df) : list of scenarios, assignments & results
          simulations_output_name (str) : csv filename
          cols_delete (list) : list of strings (cols to delete)
     """

     # Find all columns in cols_delete and remove
     df.drop(df.filter(cols_delete), axis=1, inplace=True)

     # Find columns which with all values = 0 and delete
     null_cols = df.eq(0).all(axis=0)
     for col, is_zeroes in null_cols.items():
          if is_zeroes:
               df.drop([col], axis=1, inplace=True)

     # Take a copy of the df
     df2 = df.copy()

     # To plot this type of diagram we must map string columns to a numeric category
     # Map string columns and delete the source string columns
     for column in df2:
          if pd.api.types.is_string_dtype(df2[column]):
               # get source column index
               postion = df2.columns.get_loc(column)
               temp_name = column + '1'
               # insert new column after source column (otherwise it is added to the end)
               df2.insert(postion, temp_name, pd.Categorical(df2[column], ordered=True).codes)
               # delete old column
               df2.drop(column, axis=1, inplace=True)
               # rename new column back to the source column name
               df2.rename(columns={temp_name:column}, inplace=True)

     # Get a list of columns
     cols2 = list(df2)

     # Create the parameters needed for the plot axes in a dict
     # ... {key : [tickvals[], ticktext[], column label, column values]}
     dim = {}
     for col in cols2:
          if pd.api.types.is_numeric_dtype(df[col]):
               # Numeric based
               start = math.floor(df2[col].min())
               stop = math.ceil(df2[col].max())
               # adjust step divisor to change scaling / label divisions
               step = round((stop-start)/50)
               if step < 1:
                    step = 0.5     # try 0.5, 0.25, but not 0.1
               # np.arange stop value is not included so add step
               tickvals = np.arange(start, stop+step, step)
               ticktext = [str(x) for x in tickvals]
               # add to dim dict
               dim[col] = [tickvals, ticktext, col, df2[col]]
          elif pd.api.types.is_string_dtype(df[col]):
               # String / category based
               tickvals = list(range(df2[col].min(), df2[col].max()+1, 1))
               ticktext = pd.Categorical(df[col], ordered=True).categories.tolist()
               # add to dim dict
               dim[col] = [tickvals, ticktext, col, df2[col]]
          else:
               print('Error: in plot parameter creation')
               break

     # Create the parallel coordinate diagram
     # Try other colorscale options: https://plotly.com/python/builtin-colorscales/
     # px.colors.sequential.Jet
     # px.colors.sequential.Viridis
     # px.colors.diverging.RdYlBu
     # px.colors.diverging.Tealrose

     parcoords_data = {
          'line': {
               'color':df['run'],
               'showscale':False,
               'colorscale':px.colors.sequential.Jet,
               'colorbar': {'thickness':20, 'tick0':0 , 'dtick':5, 'title':'Run #'}
          },
          'dimensions': [{'tickvals': dim[col][0], 'ticktext': dim[col][1],
                    'label': dim[col][2], 'values': dim[col][3]} for col in cols2]
     }

     fig = go.Figure(data=
          go.Parcoords(parcoords_data)
     )
     # Set options
     title = f'Parametric simulations ({simulations_output_name})'
     fig.update_layout(font={'size':8, 'family':'Arial', 'color':'gray'})
     fig.update_layout(title_text=title,
               title={'y':0.98, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})

     fig.show()

# Main loop
if __name__ == "__main__":

     # Ask user for csv file
     root = tk.Tk()
     simulations_output_name = askopenfilename(title='Choose CSV file', filetypes=[("csv file(*.csv)","*.csv")])
     root.destroy() # Removes Tkinter dialog popup window

     # Load the csv file in to a dataframe
     df = pd.read_csv(simulations_output_name)

     # Define a list of columns to be ignored in the chart
     cols_delete = [
               'Interior_lighting_kWh/m2',
               'Exterior_lighting_kWh/m2',
               'Space_heating_(gas)_kWh/m2',
               'Space_heating_(elec)_kWh/m2',
               'Space_cooling_kWh/m2',
               'Pumps_kWh/m2',
               'Fans_interior_kWh/m2',
               'DHW_heating_kWh/m2',
               'Receptacle_equipment_kWh/m2',
               'Elevators_escalators_kWh/m2',
               'Data_center_equipment_kWh/m2',
               'Cooking_(gas)_kWh/m2',
               'Cooking_(elec)_kWh/m2',
               'Refrigeration_kWh/m2',
               'Wind_PV_kWh/m2'
               ]

     # Plot parallel coordinates diagram
     para_coord(df, simulations_output_name, cols_delete)