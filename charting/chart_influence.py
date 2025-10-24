"""
===================
Influence bar chart
===================

Module description
------------------
Creates influence regression charting from any number of single parameter numeric
sensitivity analyses generated from parametric_sensitivity.py. Only the x axis is
standardized (the y axis is a common scale/unit) so this shows the influence that the
input parameter range has to the target metric.

Each csv contains the scenario run #, model changes and multiple output metrics.

Define the output metrics to be included in the sensitivity regression analysis.

Notes:

Only accepts numeric based model changes (needed for regression).

If a csv file output metric is constant, for example in the case of simulating PV area
and setting 'Heating_kWh/m2' to chart you will get an error 'ValueError: zero-size
array ...' this is because a regression analysis is not possible and you need to chart
a dependent output variable, for example 'CE_kgCO2/m2'.

"""

import numpy as np
from scipy import stats
import pandas as pd
import plotly.express as px
import tkinter as tk
import tkinter.filedialog as fd
import statsmodels.formula.api as smf
from pathlib import Path

def sensitivity(df: pd.DataFrame, target):
     """ Creates a bar chart of beta values

     Args:
          df (pandas df) : list of analysis and beta values
          target (str) : output metric
     """

     # Create chart
     # Try other colorscale options: https://plotly.com/python/builtin-colorscales/
     title = 'Parameter influence (' + target + ')'
     fig = px.bar(  df,
                    y='beta',
                    color_discrete_sequence=['skyblue']*len(df),
                    width=750,
                    height=750,
                    title=title)

     # Or for sequential colors
     #fig = px.bar(df, y='beta', color=df['beta'],
     #color_continuous_scale=px.colors.sequential.Viridis,
     #width=750, height=750, title=title, text_auto=True)

     # Set options
     fig.update_layout(font={'size':12, 'family':'Arial', 'color':'gray'})
     fig.update_layout(title={'y':0.9,'x':0.5,'xanchor': 'center','yanchor': 'top'})
     fig.update_xaxes(title_text=' ', tickangle=90)
     fig.update_yaxes(title_text='Beta')
     fig.update_traces(textfont_size=8, textangle=0, textposition="outside")
     fig.update(layout_coloraxis_showscale=False)

     # Add annotations
     fig.add_annotation(text='Variables ordered in decreasing quanta',font={'size':6},
     xref="paper", yref="paper", x=0.5, y=1.0, showarrow=False)

     fig.show()

# Main loop
if __name__ == "__main__":

     ### Set the target metric to analyse and chart
     # Examples:
    # 'Gas_MWh',
    # 'Elec_MWh',
    # 'Gas_kWh/m2',
    # 'Elec_kWh/m2'
    # 'Boilers_MWh',
    # 'Chillers_MWh',
    # 'Boilers_kWh/m2',
    # 'Chillers_kWh/m2'
    # 'CE_kgCO2/m2',
    # 'UK_BER_kgCO2/m2',
    # 'EUI_kWh/m2'
    # 'Ta_max_degC',
    # 'Boiler_max_kW',
    # 'Chiller_max_kW'
     target = 'EUI_kWh/m2'

     # Ask the user for csv files
     root = tk.Tk()
     files = fd.askopenfilenames(title='Choose CSV files', filetypes=[("csv file(*.csv)","*.csv")])
     root.destroy() # Removes Tkinter dialog popup window

     csv_list = list(files)

     if len(csv_list) == 0:
          quit()

     # Create an empty df for the regression results
     results = {}
     #results = pd.DataFrame(columns=['analysis', 'beta'])

     # Process each csv file
     for csv_file in csv_list:
          # Get the name of the sensitivity analysis
          analysis_name = Path(csv_file).stem

          # Load the csv file in to a dataframe
          df = pd.read_csv(csv_file)
          # Reduce the df1 to the required columns
          df = df[[analysis_name, target]]
          # Rename the columns to be suitable for statsmodels
          df.rename(columns={analysis_name: 'x', target: 'y'}, inplace=True)

          # Regression analysis
          # https://www.analyticsvidhya.com/blog/2021/03/standardized-vs-unstandardized-regression-coefficient/
          # https://stackoverflow.com/questions/50842397/how-to-get-standardised-beta-coefficients-for-multiple-linear-regression-using

          # Standardize the data using a z score
          df['xz']= stats.zscore(df['x'])
          #df_z = df.select_dtypes(include=[np.number]).dropna().apply(stats.zscore)

          # Carry out regression analysis
          model = smf.ols('y ~ xz', data=df)
          result = model.fit()

          # Access the results; optionally print all results, get beta value
          # https://medium.com/swlh/interpreting-linear-regression-through-statsmodels-summary-4796d359035a
          #print(result.summary())
          beta = result.params

          # Add beta value to results dict
          results[analysis_name] = beta[1]

     # Make a df with the results for charting
     plot_data = pd.DataFrame.from_dict(results, orient='index',columns=['beta'])

     # Sort the df rows by value; key parameter sorts by absolute value
     plot_data = plot_data.sort_values(by=['beta'], ascending=False, key=abs)
     print(plot_data)

     # Round the values to 2 DP and chart
     sensitivity(plot_data.round(2), target)