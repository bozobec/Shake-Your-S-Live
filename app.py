# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import dash
import sqlite3
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dataAPI
import main
import dash_bootstrap_components as dbc
from dash import html
import datetime
import time
import math

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
# ---------------------------------------------------------------------------
# Data Definition & Initialization
r_squared_selected = 0.0
carrying_capacity_container = 0
time_plateau_container = 0.0
current_valuation_container = 0.0
arpu_needed_container = 0.0
user_value_container = 0.0
valuation_Snapchat = 119.85 * pow(10, 9)
valuation_Spotify = 47.3 * pow(10, 9)
valuation_Twitter = 51.74 * pow(10, 9)
valuation_Linkedin = 29.5 * pow(10, 9)
valuation_Netflix = 282.36 * pow(10, 9)
valuation_Tesla = 1000 * pow(10, 9)
valuation_Teladoc = 23.1 * pow(10, 9)

# Values for the dropdown (all different companies in the DB)
labels = dataAPI.get_airtable_labels()


# Function returning the correct valuation, as an MVP solution before integrating it to the DB
def valuation_related(company_label):
    if company_label == "Spotify":
        valuation = valuation_Spotify
    elif company_label == "Snapchat":
        valuation = valuation_Snapchat
    elif company_label == "Twitter":
        valuation = valuation_Twitter
    elif company_label == "Linkedin":
        valuation = valuation_Linkedin
    elif company_label == "Netflix":
        valuation = valuation_Netflix
    elif company_label == "Tesla":
        valuation = valuation_Tesla
    elif company_label == "Teladoc":
        valuation = valuation_Teladoc
    return valuation

# ------------------------------------------------------------------------------------------------------------
# Components definition

# Navbar


navbar = dbc.NavbarSimple(
    brand="Shake Your S",
    brand_href="#",
    color="primary",
    dark=True,
    fluid=True,
)

# Dropdown - Taking data from "Labels"
dropdown = dcc.Dropdown(id='dropdown', options=[{'label': i, 'value': i} for i in labels])

# Tooltips
tooltip_plateau = dbc.Tooltip("This number highlights the maximum amount of users that can be reached with the current growth",
                       target="tooltip-plateau-target",)
# Sliders
slider = html.Div(children=[dcc.RangeSlider(id="range-slider-data-ignored1", min=0, step=1,
                                                               marks={},
                                                               value=[0]),
                            html.Div(id="max-label")])
# slider_profitability = html.Div(children=[dcc.RangeSlider(id="range-slider-profitability", min=20, max=50, step=5,
                                                               # marks={20: '20% Profitability', 50: '50% Profitability'},
                                                               # value=[20])])
# Table summarising insights
row1 = html.Tr([html.Td(["Users ", html.Span("plateau: ", id="tooltip-plateau-target", style={"textDecoration": "underline", "cursor": "pointer"},)], style={"width": "380px"}),
                        html.Td(id='carrying-capacity', children=carrying_capacity_container, style={"color": '#54c4f4'}), tooltip_plateau], style={"margin-bottom": "0px"})
row2 = html.Tr([html.Td("Plateau reached in: "), html.Td(id='time-plateau', children=time_plateau_container, style={"color": '#54c4f4'})])
# row3 = html.Tr([html.Td("Current valuation: "), html.Td(id='current-valuation', children=current_valuation_container)])
# row4 = html.Tr([html.Td("Yearly profit per user to justify the current valuation: "),
# html.Td(id='arpu-needed', children=arpu_needed_container, style={"color": '#54c4f4'})])
row5 = html.Tr([html.Td("R Squared: "), html.Td(id='rsquared-container', children=r_squared_selected, style={"color": '#54c4f4'})])
# row6 = html.Tr([html.Td("Current user value: "), html.Td(id='uservalue-container', children=user_value_container)])

# Left card consolidating all the rows defined above
left_card = dbc.Card(id="left-card", children=[
                    dbc.CardBody(
                        [
                            # R squared text and value displayed
                            html.Span([
                                html.H6("Prediction data"),
                                dbc.Table(html.Tbody(row1), style={"margin-bottom": "0px"}),
                                html.Div(slider, style={"height": "10px", "margin-bottom": "20px"}),
                                # dbc.Table(html.Tbody(row4), style={"margin-bottom": "0px"}),
                                # html.Div(slider_profitability, style={"height": "10px", "margin-bottom": "40px"}),
                                dbc.Table(html.Tbody([row2, row5])),
                            ]),
                        ])
                ], style={'display': 'none'}),
right_card = dbc.Card(id="right-card", children=[
                        html.Div(id='graph-container1', children=[dcc.Graph(id='main-graph1',
                                                                            config={'displayModeBar': False})])
                      ], style={'display': 'none'})

bottom_card = dbc.Card(id="bottom-card", children=[
                        html.Div(id='graph-container2', children=[dcc.Graph(id='main-graph2',
                                                                            config={'displayModeBar': False})])
                      ], style={'display': 'none'})

# Graph layout

# Build main graph
layout_main_graph = go.Layout(
    # title="User Evolution",
    plot_bgcolor="White",
    legend=dict(
        # Adjust click behavior
        itemclick="toggleothers",
        itemdoubleclick="toggle",
    ),
    xaxis=dict(
        title="Timeline",
        linecolor="Grey",
    ),
    yaxis=dict(
        title="Users",
        linecolor="Grey",
        gridwidth=1,
        gridcolor='#e3e1e1',
    ),
    showlegend=False,
    font=dict(
        family="Open Sans",
        size=16,
        color="Black"
    ),
)

# Build second graph
layout_second_graph = go.Layout(
    # title="User Evolution",
    plot_bgcolor="White",
    legend=dict(
        # Adjust click behavior
        itemclick="toggleothers",
        itemdoubleclick="toggle",
    ),
    xaxis=dict(
        title="Users",
        linecolor="Grey",
    ),
    yaxis=dict(
        title="Discrete Growth Rate",
        linecolor="Grey",
        gridwidth=1,
        gridcolor='#e3e1e1',
    ),
    showlegend=False,
    font=dict(
        family="Open Sans",
        size=16,
        color="Black"
    ),
)


# ----------------------------------------------------------------------------------
# App Layout
app.layout = html.Div(children=[
    #navbar,
    # Title
    dbc.Row(dbc.Col(html.H1(id='main-title', children='Growth estimation'), width={"size": 6, "offset": 1}), style={"margin-top": "40px"}),
    # Subtitle
    # dbc.Row(dbc.Col(html.Div(children="Have fun estimating the user growth of companies"),
                    # width={"size": 6, "offset": 1})),
    # Dropdown
    dbc.Row(dbc.Col(html.Div(dropdown), width={"size": 2, "offset": 1})),
    # Title - You are seeing the evolution of X company
    dbc.Row(dbc.Col(html.H2(id='title', children=[]), width={"size": 6, "offset": 1}), style={"margin-top": "40px"}),
    # --------------------------------------------------------
    # Bloc with buttons and graph
    dbc.Row([
        # 1st column with buttons
        dbc.Col(right_card, width={"size": 6, "offset": 1}),
        # 2nd column with graph
        dbc.Col(left_card, width={"size": 4}),
    ], style={"margin-top": "20px"}),
    # Bottom graph
    dbc.Row(dbc.Col(bottom_card, width={"size": 6, "offset": 1}), style={"margin-top": "2px"}),
    # Storing the key dataframe with all parameters
    dcc.Store(id='intermediate-value'),
    dcc.Store(id='users-data')
])


# ----------------------------------------------------------------------------------
# Callback behaviours and interaction

@app.callback(
    Output(component_id='intermediate-value', component_property='data'), #prints the dataframe
    Output(component_id='users-data', component_property='data'),
    Output(component_id='range-slider-data-ignored1', component_property='value'), # Reset slider value to zero
    # Output(component_id='uservalue-container', component_property='children'),
    Input(component_id='dropdown', component_property='value'),  # Take dropdown value
    )

# Here analysis is made to load the different scenarios (low & high) when a dropdown value is selected
def load_data(dropdown_value):
    #Initializing random data when dropdown is None
    if dropdown_value is None:
        dates = [48, 49, 50, 51, 52, 53, 54, 55]
        users = [1, 2, 3, 5, 7, 10, 14, 20]
    else:
        # The data is loaded from airtable
        df = dataAPI.get_airtable_data(dropdown_value)
        # The dates in a panda serie of format YYYY-MM-DD are transformed to a decimal yearly array
        dates = np.array(main.date_formatting(df["Date"]))
        # Users are taken from the database and multiply by a million
        users = np.array(df["Users"]).astype(float) * 1000000
    # All parameters are calculated by ignoring data 1 by 1
    df_full = main.parameters_dataframe(dates, users)
    if dropdown_value is None: #Exception for when dropdown is not selected yet, initializing df
        df = df_full
    current_valuation = 100
    user_value = current_valuation / users[-1]
    user_value_displayed = '{:.1f} $'.format(user_value)
    return df_full.to_json(date_format='iso', orient='split'), df.to_json(date_format='iso', orient='split'), \
        [0]

@app.callback([
    Output(component_id='title', component_property='children'),  # Title

    Output(component_id='left-card', component_property='style'),  # Show left card
    Output(component_id='right-card', component_property='style'),  # Show graph card
    Output(component_id='bottom-card', component_property='style'),  # Show graph card
    Output(component_id='main-graph1', component_property='figure'),  # Update graph 1
    Output(component_id='main-graph2', component_property='figure'),  # Update graph 2
    Output(component_id='carrying-capacity', component_property='children'),  # Update the carrying capacity
    Output(component_id='rsquared-container', component_property='children'),  # Update regression
    Output(component_id='time-plateau', component_property='children'),  # Update the time when the plateau is reached
    # Output(component_id='current-valuation', component_property='children'),  # Update the current valuation
    # Output(component_id='arpu-needed', component_property='children'),  # Update ARPU needed
    Output(component_id='range-slider-data-ignored1', component_property='marks'),  # Amount of steps for the slider, matching the number of parameters calculated
    ],  # Maximum value of the slider, of length of parameters array

    [
    Input(component_id='users-data', component_property='data'),  # Take dropdown value
    Input(component_id='intermediate-value', component_property='data'), # Read data of the parameters calculated earlier
    Input(component_id='range-slider-data-ignored1', component_property='value'),  # Take user slider value
    # Input(component_id='range-slider-profitability', component_property='value')
              ])
def graph_update(jsonified_users_data, jsonified_cleaned_data, data_slider):
    # --------- Data Loading
    # Data prepared earlier is fetched here
    df = pd.read_json(jsonified_users_data, orient='split')  # Users data
    company_name = df.index[1]
    print(company_name)
    print(type(company_name))
    # Way of dynamically adapting the title --> company_name should be used as a variable
    title_figure = "The growth evolution is shown"
    dates = np.array(main.date_formatting(df["Date"]))
    users = np.array(df["Users"]).astype(float)*1000000
    df_full = pd.read_json(jsonified_cleaned_data, orient='split')
    df_sorted = main.parameters_dataframe_cleaning(df_full, users)
    df_sorted_array = np.array(df_sorted)
    # If selecting three main scenarios
    '''
    df_scenarios = main.growth_scenarios_summary(df_sorted)
    df_scenarios_array = np.array(df_scenarios)
    k_scenarios = np.array(df_scenarios['K'])
    r_scenarios = np.array(df_scenarios['r'])
    p0_scenarios = np.array(df_scenarios['p0'])'''

    # If selecting all possible scenarios
    df_scenarios = df_sorted
    df_scenarios_array = np.array(df_scenarios)
    k_scenarios = np.array(df_scenarios['K'])
    r_scenarios = np.array(df_scenarios['r'])
    p0_scenarios = np.array(df_scenarios['p0'])
    # ignored_data_scenarios = np.array((df_scenarios['d_ignored']))

    # Creating the slider's marks
    max_value = len(df_sorted) - 1
    marks = {
        0: {'label': 'Min', 'style': {'color': '#77b0b1'}},
        max_value: {'label': 'Max', 'style': {'color': '#f50'}}
    }
    # steps_slider = 3 #actual slider shown - only 3 scenarios instead of 10
    row_selected = int(data_slider[0])
    # Parameters calculation
    print ("Scenario selected")
    print (data_slider[0])
    print (df_scenarios)
    k = df_scenarios_array[row_selected, 1]
    r = df_scenarios_array[row_selected, 2]
    p0 = df_scenarios_array[row_selected, 3]
    r_squared_showed = np.round(df_sorted_array[row_selected, 4], 3)
    number_ignored_data = int(df_scenarios_array[row_selected, 0])
    print(type(number_ignored_data))
    print(number_ignored_data)
    # Build Main Chart
    fig_main = go.Figure(layout=layout_main_graph)
    # Ignored Data - Shows bars that are ignored
    # fig.add_trace(go.Bar(name="Ignored Data", x=dates[0:number_deleted_data]+1970, y=users[0:number_deleted_data],
                         # marker_color="Grey"))
    # Add S-curve - S-Curve the user can play with
    x = np.linspace(dates[0], dates[-1]*2-dates[0], num=50)
    fig_main.add_trace(go.Scatter(name="Predicted S Curve", x=x+1970, y=main.logisticfunction(k, r, p0, x), mode="lines", line=dict(color='#54c4f4')))
    # Add 3 scenarios
    x0 = np.linspace(dates[-1] + 0.25, dates[-1]*2-dates[0], num=10)  # Creates a future timeline the size of the data
    # Low growth scenario
    fig_main.add_trace(go.Scatter(name="Predicted S Curve", x=x0 + 1970,
                             y=main.logisticfunction(k_scenarios[0], r_scenarios[0], p0_scenarios[0], x0), mode='lines',
                             line=dict(color='LightGrey', width=2, dash='dash')))
    #fig.add_trace(go.Line(name="Predicted S Curve", x=x + 1970,
                             #y=main.logisticfunction(k_scenarios[1], r_scenarios[1], p0_scenarios[1], x), mode="lines"))
    # High growth scenario, if existant
    if len(df_scenarios_array) > 1:
        fig_main.add_trace(go.Scatter(name="Predicted S Curve", x=x0 + 1970,
                             y=main.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1], x0), mode='lines',
                             line=dict(color='Grey', width=2, dash='dash')))
    x1 = np.linspace(dates[-1] + 0.25, dates[-1] + 10, num=10)
    # Add predicted bars
    fig_main.add_trace(go.Bar(name="Predicted S Curve", x=x1+1970, y=main.logisticfunction(k, r, p0, x1),
                         marker_color='White', marker_line_color='Black'))
    # Highlight points considered for the approximation
    fig_main.add_trace(go.Bar(name="Data used for the approximation", x=dates+1970, y=users,
                         marker_color="Black"))

    # Build second chart containing the discrete growth rates
    fig_second = go.Figure(layout=layout_second_graph)
    fig_second.add_trace(
        go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
                   y=main.discrete_growth_rate(users, dates+1970), mode="markers",line=dict(color='#54c4f4')))
    # Add trace of the regression
    fig_second.add_trace(
        go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
                   y=-r/k*main.discrete_user_interval(users)+r, mode="lines", line=dict(color='#54c4f4')))
    # Changes the color of the scatters ignored
    if number_ignored_data > 0:
        fig_second.add_trace(
            go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users[0:number_ignored_data]),
                       y=main.discrete_growth_rate(users[0:number_ignored_data], dates[0:number_ignored_data] + 1970),
                       mode="markers", line=dict(color='#808080')))

    # Carrying capacity to be printed
    k_printed = int(np.rint(k)/pow(10, 6))
    k_printed = "{:,} M".format(k_printed)
    print(k_printed)
    # PLATEAU: Time when the plateau is reached, assuming the plateau is "reached" when p(t)=95%*K
    print(k, r, p0)
    t_plateau = main.time_to_population(k, r, p0, 0.95*k) + 1970
    print(t_plateau)
    print(type(t_plateau))
    month_plateau = math.ceil((t_plateau - int(t_plateau))*12)
    year_plateau = int(np.round(t_plateau, 0))
    date_plateau = datetime.date(year_plateau, month_plateau, 1)
    date_plateau_displayed = date_plateau.strftime("%b, %Y")
    t_plateau_displayed = 'Year {:.1f}'.format(t_plateau)

    # Printing a summary of the data displayed
    print("All Scenarios")
    print(df_full)
    print("Final Scenarios taken into account")
    print(df_scenarios)



    return title_figure, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}, fig_main, fig_second, k_printed, r_squared_showed, \
           date_plateau_displayed, marks




if __name__ == '__main__':
    app.run_server(debug=True)