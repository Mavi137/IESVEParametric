"""
===========================
Uncertainty histogram chart
===========================

Module description
------------------
Creates stats & charting from an uncertainty analysis.
The uncertainty analysis comes from user scenario testing.
The uncertainty analysis data is input from a single csv file generated from parametric_uncertainty.py

The csv contains the scenario run #, model changes and multiple output metrics.

Define the output metric to be included in the uncertainty analysis.

"""

import pandas as pd
import plotly.express as px
import tkinter as tk
from tkinter.filedialog import askopenfilename

def uncertainty(df, var):
     """ Creates a histogram for uncertainty analysis

     Args:
          df (pandas df) : list of scenarios, assignments & results
          var (str) : column label required for plot
     """

     # Determine summary stats
     stats = df[var].describe()
     stats = [round(num, 0) for num in stats]

     # Create chart
     # CSS colors https://www.w3schools.com/cssref/css_colors.asp
     # Try cadetblue, cornflowerblue, darkgrey, darkseagreen, orangered, skyblue, yellowgreen
     fig = px.histogram(df, x=var, nbins=50, title='Uncertainty analysis', opacity=0.5,
     color_discrete_sequence=['skyblue'], marginal='box', width=750, height=750)

     # Set options
     fig.update_layout(font=dict(size=12, family='Arial', color='gray'))
     fig.update_layout(title={'y':0.9,'x':0.5,'xanchor': 'center','yanchor': 'top'})

     # Helper function to add multiple annotations to figure
     def add_multiple_annotations(fig, entries, x, y_top, spacing):
          y_current = y_top
          for entry in entries:
               fig.add_annotation(text=entry,xref="paper", yref="paper", x=x, y=y_current, showarrow=False)
               y_current -= spacing

     # Add annotations
     fig.add_annotation(text='Range of overall variation',xref="paper", yref="paper", x=0.5, y=1.0, showarrow=False)

     # Add annotations to figures
     entries = [
          'Summary Stats',
          f'N: {stats[0]}',
          f'Mean: {stats[1]}',
          f'Std. dev: {stats[2]}',
          f'Min val: {stats[3]}',
          f'Q1: {stats[4]}',
          f'Median: {stats[5]}',
          f'Q2: {stats[6]}',
          f'Max. val: {stats[7]}']
     add_multiple_annotations(fig, entries, x=1, y_top=0.83, spacing=0.04)
     fig.show()

# Main loop
if __name__ == "__main__":

     # Ask user for csv file
     root = tk.Tk()
     simulations_output_name = askopenfilename(title='Choose CSV file', filetypes=[("csv file(*.csv)","*.csv")])
     root.destroy() # Removes Tkinter dialog popup window

     # Load the csv file in to a dataframe
     df = pd.read_csv(simulations_output_name)

     # Plot uncertainty histogram chart
     uncertainty(df, 'Boilers_MWh')