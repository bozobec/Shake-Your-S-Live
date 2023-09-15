# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import dash
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
import math

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = 'Growth Estimation'
server = app.server
# ---------------------------------------------------------------------------
# Data Definition & Initialization
r_squared_selected = 0.0
carrying_capacity_container = 0
time_plateau_container = 0.0
current_valuation_container = 0.0
arpu_needed_container = 0.0
user_value_container = 0.0
valuation_Snapchat = 119.85 * pow(10, 9)
valuation_Spotify = 47.2 * pow(10, 9)
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
tooltip_plateau = dbc.Tooltip("This number highlights the maximum amount of users that will be reached with the selected scenario",
                       target="plateau-header",)
# Sliders
slider = html.Div(children=[dcc.RangeSlider(id="range-slider-data-ignored1", min=0, step=1,
                                                               marks={},
                                                               value=[0],
                            tooltip={"placement": "bottom", "always_visible": True},
                                            vertical=True),
                            html.Div(id="max-label")])
slider_history = html.Div(children=[dcc.RangeSlider(id="range-slider-history", min=0, max=10,
                                                               marks={},
                                                               value=[10],
                                                            tooltip={"placement": "bottom", "always_visible": True}),
                            html.Div(id="max-label2")])
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
# row5 = html.Tr([html.Td("R Squared: "), html.Td(id='rsquared-container', children=r_squared_selected, style={"color": '#54c4f4'})])
# row6 = html.Tr([html.Td("Current user value: "), html.Td(id='uservalue-container', children=user_value_container)])

# Left card consolidating all the rows defined above
left_card = dbc.Card(id="left-card", children=[
                    dbc.CardBody(
                        [
                            # R squared text and value displayed
                            html.Span([
                                html.H6("Prediction data"),
                                dbc.Table(html.Tbody(row1), style={"margin-bottom": "0px"}),
                                # html.Div(slider, style={"height": "10px", "margin-bottom": "20px"}),
                                # dbc.Table(html.Tbody(row4), style={"margin-bottom": "0px"}),
                                # html.Div(slider_profitability, style={"height": "10px", "margin-bottom": "40px"}),
                                dbc.Table(html.Tbody([row2])),
                            ]),
                        ])
                ], style={'display': 'none'}),
# Card that contains the main graph with the prediction
right_card = dbc.Card(id="right-card", children=[
                        html.Div(id='graph-container1', children=[dcc.Graph(id='main-graph1',
                                                                            config={'displayModeBar': False})])
                      ], style={'display': 'none'})
# Card that contains the regression
bottom_card = dbc.Card(id="bottom-card", children=[
                        html.Div(id='graph-container2', children=[dcc.Graph(id='main-graph2',
                                                                            config={'displayModeBar': False})])
                      ], style={'display': 'none'})
# Card containing the history slider
top_card = dbc.Card(id="top-card", children=[
                        dbc.CardBody(
                            [
                            html.Span([html.H6("Date of the prediction"),
                            html.Div(slider_history, style={"height": "10px", "margin-bottom": "20px"})])
                            ])
                      ], style={'display': 'none'})

# Card containing the vertical slider for the carrying capacity
vertical_slider_card = dbc.Card(id="vertical-slider", children=[
                        dbc.CardBody(
                            [
                            html.Span([
                            html.H6("Plateau", id="plateau-header"),
                            html.Div(slider)])
                            ])
                      ], style={'display': 'none'})
r_squared_card = dbc.Card(id="r-squared-card", children=[
                        dbc.CardBody(
                            [
                            html.H6(["R", html.Sup(2)], id="r-squared-header"),
                            html.P(id="rsquared-container"),
                            ])
                      ], style={'display': 'none'})

# Alert generated
alert_no_calculation_possible = dbc.Alert(
            "No estimation could be done with the selected dataset. Try another dataset and/or point in time",
            id="alert-fade",
            dismissable=True,
            is_open=False,
            color="info"
        ),

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
        # family="Open Sans",
        #size=16,
        # color="Black"
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
        # family="Open Sans",
        #size=16,
        #color="Black"
    ),
)

loading = dcc.Loading(id="loading-component", children=[html.Div([html.Div(id="loading-output")])], type="circle",),

# ----------------------------------------------------------------------------------
# App Layout
app.layout = dbc.Container(children=[
    # Toast message appearing on top
    dbc.Row(html.Div(alert_no_calculation_possible)),
    # Title row & loading animation
    dbc.Row(dbc.Col([
        html.Div([html.Img(src="/assets/Vector.svg", style={'height': '35px', 'float': 'left'}),
                  html.H1(id='main-title', style={'float': 'left', 'margin-left': '20px'} , children='Growth estimation')]),
        html.Div(loading)], style={'clear': 'both', "margin-top": "40px"},
                    width={"size": 7}), justify="center"),
    # Subtitle
    # dbc.Row(dbc.Col(html.Div(children="Have fun estimating the user growth of companies"),
                    # width={"size": 6, "offset": 1})),
    # Dropdown
    dbc.Row(dbc.Col(html.Div(dropdown), width={"size": 7}), justify="center"),
    # Title - You are seeing the evolution of X company
    dbc.Row(dbc.Col(html.H2(id='title', children=[]), width={"size": 6, "offset": 1}), style={"margin-top": "40px"}),
    # --------------------------------------------------------
    # Slider to go back in time and retrofit
    dbc.Row([
        dbc.Col(top_card, width={"size": 6}),
        dbc.Col(r_squared_card, width={"size": 1}),
    ], justify="center"),
    # Bloc with buttons and graph
    dbc.Row([
        # 1st column with the main graph
        dbc.Col(right_card, width={"size": 6}),
        # 2nd column with the table and the slider
        # dbc.Col(left_card, width={"size": 4}),
        # Column with the vertical slider for carrying capacity
        dbc.Col(vertical_slider_card, width="auto"),
    ], style={"margin-top": "20px"}, justify="center"),
    # Bottom graph
    dbc.Row(dbc.Col(bottom_card, width={"size": 6}), style={"margin-top": "2px"}, justify="center"),
    dbc.Row(left_card),
    # Storing the key dataframe with all parameters
    dcc.Store(id='intermediate-value'),
    dcc.Store(id='users-data')
], fluid=True)


# ----------------------------------------------------------------------------------
# Callback behaviours and interaction

# First Callback defining the side of the history slider, based on what company has been chosen
@app.callback([
    Output(component_id='range-slider-history', component_property='value'),  # Set slider to the last date available
    Output(component_id='range-slider-history', component_property='min'),  # Calculate the min of the history slider
    Output(component_id='range-slider-history', component_property='max'),  # Calculate the max of the history slider
    Output(component_id='range-slider-history', component_property='marks'),
    # Output(component_id='uservalue-container', component_property='children'),
    Input(component_id='dropdown', component_property='value'),])  # Take dropdown value

def set_history_size(dropdown_value):
    print("Fetching the dropdown_value...")
    df = dataAPI.get_airtable_data(dropdown_value)
    # The dates in a panda serie of format YYYY-MM-DD are transformed to a decimal yearly array
    dates = np.array(main.date_formatting(df["Date"]))
    formatted_dates = dates + 1970
    min_history_date = main.date_minimum_history(formatted_dates)
    max_history_date = formatted_dates[-1]
    marks_history = {
        min_history_date: {'label': str(int(min_history_date)), 'style': {'color': '#77b0b1'}},
        max_history_date: {'label': str(int(max_history_date)), 'style': {'color': '#f50'}}
    }
    print("Dropdown value fetched and slider printed successfully")
    return [max_history_date], min_history_date, max_history_date, marks_history
@app.callback(
    Output(component_id='intermediate-value', component_property='data'), #prints the dataframe
    Output(component_id='users-data', component_property='data'),
    Output(component_id='range-slider-data-ignored1', component_property='value'), # Reset slider value to zero
    Output("alert-fade", "is_open"),  # Reset slider value to zero
    Output("loading-component", "loading"),
    # Output(component_id='range-slider-history', component_property='value'), # Set slider to the last date available
    # Output(component_id='uservalue-container', component_property='children'),
    Input(component_id='dropdown', component_property='value'),  # Take dropdown value
    Input(component_id='range-slider-history', component_property='value'),  # Take slider history value
    )

# Analysis to load the different scenarios (low & high) when a dropdown value is selected
def load_data(dropdown_value, history_value):
    print("Starting scenarios calculation")
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

    # Test to be deleted, changing dates & users to use moving average
    print(dates)
    print(users)
    print("CHANGE")
    dates, users = main.moving_average_smoothing(dates, users, 3)
    print(dates)
    print(users)
    history_value_formatted = history_value[0]-1970  # Puts back the historical value to the format for computations
    dates_actual = main.get_earlier_dates(dates, history_value_formatted)
    data_len = len(dates_actual)  # length of the dataset to consider for retrofitting

    # All parameters are calculated by ignoring data 1 by 1, taking the history reference as the end point
    df_full = main.parameters_dataframe(dates[0:data_len], users[0:data_len])  # Dataframe containing all parameters with all data ignored
    df_sorted = main.parameters_dataframe_cleaning(df_full, users[0:data_len])  # Dataframe where inadequate scenarios are eliminated
    if dropdown_value is None:  # Exception for when dropdown is not selected yet, initializing df
        df = df_full
    current_valuation = 100
    if history_value:
        if df_sorted.empty:
            state_alert = True
        else:
            state_alert = False
    print("df_sorted")
    print(df_sorted)

    user_value = current_valuation / users[-1]
    user_value_displayed = '{:.1f} $'.format(user_value)
    formatted_dates = dates + 1970
    min_history_date = main.date_minimum_history(formatted_dates)
    max_history_date = formatted_dates[-1]

    print(min_history_date)
    print(max_history_date)
    print("Scenarios calculation completed")
    return df_sorted.to_json(date_format='iso', orient='split'), df.to_json(date_format='iso', orient='split'), \
        [0], state_alert, True

@app.callback([
    # Output(component_id='title', component_property='children'),  # Title

    Output(component_id='top-card', component_property='style'),  # Show top card with slider
    # Output(component_id='left-card', component_property='style'),  # Show left card
    Output(component_id='right-card', component_property='style'),  # Show graph card
    Output(component_id='bottom-card', component_property='style'),  # Show graph card
    Output(component_id='vertical-slider', component_property='style'),  # Show slider card
    Output(component_id='r-squared-card', component_property='style'),  # Show r-squared card
    Output(component_id='main-graph1', component_property='figure'),  # Update graph 1
    Output(component_id='main-graph2', component_property='figure'),  # Update graph 2
    Output(component_id='carrying-capacity', component_property='children'),  # Update the carrying capacity
    Output(component_id='rsquared-container', component_property='children'),  # Update regression
    Output(component_id='time-plateau', component_property='children'),  # Update the time when the plateau is reached
    Output(component_id='range-slider-data-ignored1', component_property='marks'),  # Amount of steps for the slider, matching the number of parameters calculated
    ],

    [
    Input(component_id='users-data', component_property='data'),  # Take dropdown value
    Input(component_id='intermediate-value', component_property='data'), # Read data of the parameters calculated earlier
    Input(component_id='range-slider-data-ignored1', component_property='value'),  # Take user slider value
    Input(component_id='range-slider-history', component_property='value'),  # Take user slider history value
    # Input(component_id='range-slider-profitability', component_property='value')
              ])
def graph_update(jsonified_users_data, jsonified_cleaned_data, data_slider, history_value):
    # --------- Data Loading
    # Data prepared earlier is fetched here
    df = pd.read_json(jsonified_users_data, orient='split')  # Users+date data
    print(df)
    # Way of dynamically adapting the title --> company_name should be used as a variable
    title_figure = "The growth evolution is shown"
    dates = np.array(main.date_formatting(df["Date"]))
    users = np.array(df["Users"]).astype(float)*1000000
    # To be deleted: changed dates & users to moving average
    dates, users = main.moving_average_smoothing(dates, users, 3)
    # Calculating the length of historical values to be considered in the plots
    history_value_formatted = history_value[0] - 1970  # Puts back the historical value to the format for computations
    dates_actual = main.get_earlier_dates(dates, history_value_formatted)
    data_len = len(dates_actual)  # length of the dataset to consider for retrofitting

    df_sorted = pd.read_json(jsonified_cleaned_data, orient='split')
    df_sorted_array = np.array(df_sorted)

    # If selecting all possible scenarios,  Creation of the arrays of parameters
    df_scenarios = df_sorted
    df_scenarios_array = np.array(df_scenarios)
    k_scenarios = np.array(df_scenarios['K'])
    r_scenarios = np.array(df_scenarios['r'])
    p0_scenarios = np.array(df_scenarios['p0'])
    # ignored_data_scenarios = np.array((df_scenarios['d_ignored']))

    # Creating the slider's marks
    max_value = len(df_sorted) - 1
    print("Length of the slider for ignored data:")
    print(max_value)
    '''
    marks_history = {
        min_history_date: {'label': str(int(min_history_date)), 'style': {'color': '#77b0b1'}},
        max_history_date: {'label': str(int(max_history_date)), 'style': {'color': '#f50'}}
    }'''
    # Formatting of the marks to be created for the slider
    k_min_mark1 = int(np.rint(k_scenarios[0]) / pow(10, 6))
    k_min_mark = "{:,} M".format(k_min_mark1)
    k_max_mark1 = int(np.rint(k_scenarios[-1]) / pow(10, 6))
    k_max_mark = "{:,} M".format(k_max_mark1)
    k_tooltip1 = int(np.rint(k_scenarios[data_slider]) / pow(10, 6))
    k_tooltip = "{:,} M".format(k_tooltip1)
    marks = {
        0: {'label': k_min_mark, 'style': {'color': '#f50', 'position': 'absolute', 'right': '-30px'}},
        max_value: {'label': k_max_mark, 'style': {'color': '#77b0b1', 'right': '-30px'}}
    }
    # Based on the slider's value, the related row of parameters is selected
    row_selected = int(data_slider[0])
    # Parameters definition
    k = df_scenarios_array[row_selected, 1]
    r = df_scenarios_array[row_selected, 2]
    p0 = df_scenarios_array[row_selected, 3]
    r_squared_showed = np.round(df_sorted_array[row_selected, 4], 3)
    number_ignored_data = int(df_scenarios_array[row_selected, 0])
    print("Number of ignored data")
    print(number_ignored_data)

    # Polynomial approximation
    polynum3 = main.polynomial_approximation(dates, users, 3)
    polynum1 = main.polynomial_approximation(dates, users, 1)

    # Build Main Chart
    fig_main = go.Figure(layout=layout_main_graph)
    fig_main.update_xaxes(range=[dates[0]+1970, dates[-1]*2-dates[0]+1970])  # Fixing the size of the X axis with users max + 10%
    fig_main.update_yaxes(range=[0, users[-1]*1.3])  # Fixing the size of the Y axis
    # Add S-curve - S-Curve the user can play with
    x = np.linspace(dates[0], dates[-1]*2-dates[0], num=50)
    fig_main.add_trace(go.Scatter(name="Predicted S Curve", x=x+1970, y=main.logisticfunction(k, r, p0, x), mode="lines", line=dict(color='#54c4f4')))
    # Add 3 scenarios
    x0 = np.linspace(dates_actual[-1] + 0.25, dates_actual[-1]*2-dates_actual[0], num=10)  # Creates a future timeline the size of the data
    # Low growth scenario
    fig_main.add_trace(go.Scatter(name="Predicted S Curve", x=x0 + 1970,
                             y=main.logisticfunction(k_scenarios[0], r_scenarios[0], p0_scenarios[0], x0), mode='lines',
                             line=dict(color='LightGrey', width=2, dash='dash')))
    #fig.add_trace(go.Line(name="Predicted S Curve", x=x + 1970,
                             #y=main.logisticfunction(k_scenarios[1], r_scenarios[1], p0_scenarios[1], x), mode="lines"))
    # High growth scenario, if existent
    if len(df_scenarios_array) > 1:
        fig_main.add_trace(go.Scatter(name="Predicted S Curve", x=x0 + 1970,
                             y=main.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1], x0), mode='lines',
                             line=dict(color='Grey', width=2, dash='dash')))
    x1 = np.linspace(dates[-1] + 0.25, dates[-1] + 10, num=10)
    # Add predicted bars
    # fig_main.add_trace(go.Bar(name="Predicted S Curve", x=x1+1970, y=main.logisticfunction(k, r, p0, x1),
                         # marker_color='White', marker_line_color='Black'))
    # Highlight points considered for the approximation
    fig_main.add_trace(go.Bar(name="Data used for the approximation", x=dates[number_ignored_data:data_len] + 1970,
                              y=users[number_ignored_data:data_len],
                              marker_color="Black"))
    # Highlight points not considered for the approximation
    fig_main.add_trace(go.Bar(name="Data used for the approximation", x=dates[0:number_ignored_data]+1970, y=users[0:number_ignored_data],
                         marker_color="Grey"))
    # Highlight points past the current date
    fig_main.add_trace(go.Bar(name="Data used for the approximation", x=dates[data_len:] + 1970,
                              y=users[data_len:],
                              marker_color='#e6ecf5'))
    # Add vertical line indicating the year of the prediction for retrofitting
    fig_main.add_vline(x=history_value[0], line_width=3, line_dash="dash")

    # Build second chart containing the discrete growth rates
    fig_second = go.Figure(layout=layout_second_graph)
    fig_second.update_xaxes(range=[0, users[-1]*1.1])  # Fixing the size of the X axis with users max + 10%
    fig_second.update_yaxes(range=[0, 1.2]) # Fixing the size of the Y axis
    fig_second.add_trace(
        go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
                   y=main.discrete_growth_rate(users, dates+1970), mode="markers",line=dict(color='#54c4f4')))
    # Add trace of the regression
    fig_second.add_trace(
        go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
                   y=-r/k*main.discrete_user_interval(users)+r, mode="lines", line=dict(color='#54c4f4')))
    # Add trace of the polynomial approximation
    '''
    fig_second.add_trace(
        go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
                   y=np.polyval(polynum3,main.discrete_user_interval(users)), mode="lines", line=dict(color="Red")))
    fig_second.add_trace(
        go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
                   y=np.polyval(polynum1, main.discrete_user_interval(users)), mode="lines", line=dict(color="Green")))
                   '''
    # Changes the color of the scatters ignored
    if number_ignored_data > 0:
        fig_second.add_trace(
            go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users[0:number_ignored_data]),
                       y=main.discrete_growth_rate(users[0:number_ignored_data], dates[0:number_ignored_data] + 1970),
                       mode="markers", line=dict(color='#808080')))
    # Changes the color of the scatters after the date considered
    if data_len < len(dates):
        fig_second.add_trace(
            go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users[data_len:]),
                       y=main.discrete_growth_rate(users[data_len:], dates[data_len:] + 1970),
                       mode="markers", line=dict(color='#e6ecf5')))

    # Carrying capacity to be printed
    k_printed = int(np.rint(k)/pow(10, 6))
    k_printed = "{:,} M".format(k_printed)
    # PLATEAU: Time when the plateau is reached, assuming the plateau is "reached" when p(t)=95%*K
    print(p0)
    if p0 > 2.192572e-11:
        t_plateau = main.time_to_population(k, r, p0, 0.95*k) + 1970
        month_plateau = math.ceil((t_plateau - int(t_plateau))*12)
        year_plateau = int(np.round(t_plateau, 0))
        date_plateau = datetime.date(year_plateau, month_plateau, 1)
        date_plateau_displayed = date_plateau.strftime("%b, %Y")
        t_plateau_displayed = 'Year {:.1f}'.format(t_plateau)
    else:
        date_plateau_displayed = "Plateau could not be calculated"
    print("2. CALLBACK END")
    print(dates)
    print(users)

    # Analysis test to be deleted


    return {'display': 'block'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'},  {'display': 'block'},\
        fig_main, fig_second, k_printed, r_squared_showed, date_plateau_displayed, marks






if __name__ == '__main__':
    app.run_server(debug=True)