"""
===========================
Range of outcomes box chart
===========================

Module description
------------------
Creates a range of outcomes chart from an uncertainty analysis. The uncertainty analysis
data is input from a single csv file generated from parametric_uncertainty.py.

The csv contains the scenario run #, model changes and multiple output metrics.

Define the output metrics (typically gas & elec) to be included in the range of outcomes
chart.

"""

import pandas as pd
import plotly.express as px
import tkinter as tk
from tkinter.filedialog import askopenfilename

def outcomes(df, var):
     """ Creates a boxplot of possible range for one or more analysis metrics

     Args:
          df (pandas df) : list of scenarios, assignments & results
          var (list of str) : column labels required for the box plot
     """

     # Create chart
     # https://plotly.github.io/plotly.py-docs/generated/plotly.express.box.html
     # CSS colors https://www.w3schools.com/cssref/css_colors.asp
     # Try cadetblue, cornflowerblue, darkgrey, darkseagreen, orangered, skyblue, yellowgreen
     # Try points = False or 'all'
     # Try notched = True or False
     fig = px.box(df, y=var, color_discrete_sequence=['skyblue'], width=375, height=750,
                    title='Range of possible outcomes', notched=False, points='all')

     # Set options
     fig.update_layout(font={'size':12, 'family': 'Arial', 'color': 'gray'})
     fig.update_layout(title={'y':0.9,'x':0.5,'xanchor': 'center','yanchor': 'top'})
     fig.update_layout(xaxis_title=' ', yaxis_title='Annual kWh/yr')

     # Optional set quartile method to linear, inclusive, exclusive
     #fig.update_traces(quartilemethod='linear, jitter=0, col=1)

     # Add annotations
     fig.add_annotation(text='Worst', font={'size':6}, xref="paper", yref="paper",
     x=0.5, y=1.0, showarrow=False)
     fig.add_annotation(text='Best', font={'size':6}, xref="paper", yref="paper",
     x=0.5, y=0.0, showarrow=False)

     fig.show()

# Main loop
if __name__ == "__main__":

     # Ask user for csv file
     root = tk.Tk()
     simulations_output_name = askopenfilename(title='Choose CSV file', filetypes=[("csv file(*.csv)","*.csv")])
     root.destroy() # Removes Tkinter dialog popup window

     # Load the csv file in to a dataframe
     df = pd.read_csv(simulations_output_name)

     # Plot scenario possible outcomes
     outcomes(df, ['Elec_kWh/m2', 'Gas_kWh/m2'])