# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import dash
import dash_mantine_components as dmc
from dash import dcc
from dash import callback
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dataAPI
import main
import dash_bootstrap_components as dbc
from dash import html
#import datetime
from datetime import datetime, timedelta
import math
from plotly.subplots import make_subplots
from dash_iconify import DashIconify
import time
from dash.exceptions import PreventUpdate


pd.set_option('display.max_columns', None)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = 'GROOWT'
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
# labels = dataAPI.get_airtable_labels() # OLD METHOD
labels = dataAPI.get_airtable_labels_new()


# Constants for the calculation
YEAR_OFFSET = 1970  # The year "zero" for all the calculations
MIN_DATE_INDEX = 4  # Defines the minimum year below which no date can be picked in the datepicker

# ------------------------------------------------------------------------------------------------------------
# Components definition
# Dropdown - Taking data from "Labels"
dropdown_items = []
for i in labels:
    dropdown_items.append(dbc.DropdownMenuItem(i))
dropdown = dcc.Dropdown(id='dropdown', options=[{'label': i, 'value': i} for i in labels])
dropdown2 = dbc.DropdownMenu(id='dropdown2', label="Select dataset", children=dropdown_items)
dropdown3 = dbc.DropdownMenu(id='dropdown3', label="Select dataset", children=[dbc.DropdownMenuItem(i) for i in labels])
dropdown4 = dbc.DropdownMenu(id='dropdown4', label="Select dataset", children=[dbc.DropdownMenuItem(i) for i in labels])
dropdown5 = dcc.Dropdown(id='dropdown5', placeholder="awdsfsdfsadf", options=[{'label': i, 'value': i} for i in labels])
#company_test = "testtest"
#labels_new.append({"value": company_test, "label": f" {company_test}", "disabled": True})

dropdown6 = html.Div(
    [
        dmc.Select(
            # label="Select framework",
            placeholder="Dataset...",
            id="dataset-selection",
            data=labels,
            style={"marginBottom": 10},
            styles={"disabled": {
                "root": {
                "fontWeight": 800
                    }
                }
            },
            dropdownPosition="bottom",
            searchable=True,
            selectOnBlur=True,
            transition="pop",
            transitionDuration=200,
        )
    ]
)



# OffCanvas (side panel that opens to give more information)
offcanvas = html.Div(
    [
        dbc.Button("About", id="open-offcanvas", n_clicks=0),
        dbc.Offcanvas([
            dmc.Container(children=[
                dmc.Text(
                    "GROOWT is a powerful and user-friendly resource designed to help you analyze and predict the future "
                    "trajectory of selected datasets. With this tool, you can gain valuable insights into the growth "
                    "patterns of your chosen dataset, allowing you to make informed decisions and projections.", size="sm"),
                dmc.Space(h=15),
                dmc.Text("GROOWT's key features include:", size="sm"),
                dmc.Space(h=10),
                dmc.List([
                    dmc.ListItem([dmc.Text("Dataset Selection", weight=700),"Easily choose the dataset you want to analyze from the dropdown menu. "
                    "The tool supports a wide range of datasets, enabling you to select the one that suits your needs."]),
                    dmc.ListItem([dmc.Text("Historical Data Visualization", weight=700),"Visualize the historical data of your selected dataset, providing "
                    "a clear overview of its past performance and growth trends. This visualization helps you understand "
                    "how the dataset has evolved over time."]),
                    dmc.ListItem([dmc.Text("Predictive Analysis", weight=700),"Leverage the advanced predictive capabilities of GROOWT to forecast the "
                    "future growth of your dataset."]),
                    dmc.ListItem([dmc.Text("Customization Options", weight=700),"Tailor your analysis by adjusting parameters ""and variables to fine-tune your "
                    "predictions. The tool offers flexibility in adapting the analysis to your specific requirements."]),
                    dmc.ListItem([dmc.Text("Decision Support", weight=700)," Use the insights generated by the Growth Estimation Tool to inform your "
                    "decision-making processes. Whether you're a data analyst, business strategist, or simply curious "
                    "about the dataset's future, this tool provides the information you need to plan and strategize "
                    "effectively."]),
                ], size="sm", listStyleType="decimal"),
                dmc.Space(h=15),
                dmc.Text("With the GROOWT, you can explore the potential future outcomes of your dataset, "
                    "helping you make more informed choices and better understand the dynamics of the data"
                    " you're working with. If you're tracking financial metrics, website traffic, or any other "
                    "data-driven variable, this tool empowers you to harness the power of data for better decision-making."
                , size="sm"),
                dmc.Space(h=15),
                dmc.Text("Contact: groowt@proton.me")]
            ),
        ],
            id="offcanvas",
            title="Welcome to GROOWT",
            is_open=False,
        ),
    ]
)

# Navbar

navbar2 = dbc.Navbar(
            dbc.Container([
                    html.A(
                        dbc.Row(
                            [dbc.Col([html.Img(src="/assets/Vector_white.svg", style={'height': '20px'}),
                                dbc.NavbarBrand("GROOWT", style={'margin-left': '10px'})
                                     ], className="align-items-center d-flex"),
                            ]
                        ), href="https://fathomless-scrubland-44017-2a7f83d10555.herokuapp.com/"
                    ),
                    ],
            fluid=True), color="primary", dark=True)

navbar = dbc.Navbar(
    dbc.Container(
        dbc.Row(
            [
                dbc.Col(
                    html.A(
                        dbc.Row([
                            dbc.Col(
                                [
                                    html.Img(src="/assets/Vector_white.svg", style={'height': '25px'}),
                                    dbc.NavbarBrand("GROOWT", style={'margin-left': '20px'}),
                                    #dropdown5,
                                ], className="align-items-center d-flex"
                            ),
                            dbc.Col(
                                [
                                    dbc.NavItem(dbc.NavLink("About", n_clicks=0, href="#")),
                                ], className="align-items-center d-flex",
                            ),
                        ]),
                    )
                ),
            ],
        ),
        fluid=True
    ),
    color="primary",
    dark=True
)

navbar3 = dbc.Navbar(dbc.Nav(
    [
        dbc.NavItem(),
        dbc.NavItem(html.Img(src="/assets/Vector_white.svg", style={'height': '20px'})),
        dbc.NavItem(dbc.NavbarBrand("GROOWT", style={'margin-left': '20px'})),
        #dropdown4,
        #dbc.NavItem(dropdown5),
        dbc.NavItem(offcanvas, style={'height':'20px'}),
    ], fill=True
                    ),

    color="primary",
    dark=True)

navbar6 = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row([
                    dbc.Col(html.Img(src="/assets/Vector_white.svg", height="25px")),
                    dbc.Col(dbc.NavbarBrand("GROOWT", className="ms-2"))
                    ],
                    align="bottom",
                    className="g-0"),

            dbc.Row([
                dbc.Col([
                    dbc.Nav([
                        dbc.NavItem(offcanvas),
                    ],
                        navbar=True
                    )
                ],
                    width={"size": "auto"})
            ],
                align="left"),
            # dbc.Col(dbc.NavbarToggler(id="navbar-toggler", n_clicks=0)),
        ],
        fluid=True
    ),
    color="primary",
    dark=True,
)



# Sliders
slider = html.Div(children=[dcc.RangeSlider(id="range-slider-data-ignored1", min=0, step=1,
                                                               marks={},
                                                               value=[0],
                            tooltip={"placement": "bottom", "always_visible": True},
                                            vertical=True),
                            html.Div(id="max-label")])

# slider_profitability = html.Div(children=[dcc.RangeSlider(id="range-slider-profitability", min=20, max=50, step=5,
                                                               # marks={20: '20% Profitability', 50: '50% Profitability'},
                                                               # value=[20])])
# Table summarising insights
#row1 = html.Tr([html.Td(["Users ", html.Span("plateau: ", id="tooltip-plateau-target", style={"textDecoration": "underline", "cursor": "pointer"},)], style={"width": "380px"}),
                       # html.Td(id='carrying-capacity', children=carrying_capacity_container, style={"color": '#54c4f4'})], style={"margin-bottom": "0px"})
# row3 = html.Tr([html.Td("Current valuation: "), html.Td(id='current-valuation', children=current_valuation_container)])
# row4 = html.Tr([html.Td("Yearly profit per user to justify the current valuation: "),
# html.Td(id='arpu-needed', children=arpu_needed_container, style={"color": '#54c4f4'})])
# row5 = html.Tr([html.Td("R Squared: "), html.Td(id='rsquared-container', children=r_squared_selected, style={"color": '#54c4f4'})])
# row6 = html.Tr([html.Td("Current user value: "), html.Td(id='uservalue-container', children=user_value_container)])


# Card that contains the regression
bottom_card = dbc.Card(id="bottom-card", children=[
                        html.Div(id='graph-container2', children=[dcc.Graph(id='main-graph2',
                                                                            config={'displayModeBar': False})])
                      ], style={'display': 'none'})
# Card that contains the evolution of R square and RMSD
bottom_bottom_card = dbc.Card(id="bottom-bottom-card", children=[
                        html.Div(id='graph-container3', children=[dcc.Graph(id='main-graph3',
                                                                            config={'displayModeBar': False})])
                      ], style={'display': 'none'})
# Card containing the history slider
top_card = dbc.Card(id="top-card", children=[
                        dbc.CardBody(
                            [
                            html.Span([html.H6("Date of the prediction"),
                            ])
                            ])
                      ], style={'display': 'none', "height": 1})



# Mantine Components

# Prediction line slider

slider_k = dmc.Slider(
            id="range-slider-k",
            min=0,
            step=1,
            value=0,
            size="sm",
            disabled=True,
            showLabelOnHover=False,
            color="#4dabf7",
            )

# Profit margin slider

slider_profit_margin = dmc.Slider(
            id="range-profit-margin",
            min=1,
            max=50,
            value=20,
            size="sm",
            disabled=False,
            showLabelOnHover=False,
            precision=2,
            step=0.1,
            )

# Discount rate slider

slider_discount_rate = dmc.Slider(
            id="range-discount-rate",
            min=2,
            max=20,
            value=5,
            step=0.1,
            marks=[
                {"value": 2, "label": "2%"},
                {"value": 10, "label": "10%"},
                {"value": 20, "label": "20%"},
            ],
            size="sm",
            disabled=False,
            showLabelOnHover=False,
            precision=2,
            )

# ARPU growth slider

slider_arpu_growth = dmc.Slider(
            id="range-arpu-growth",
            min=0,
            max=10,
            value=2,
            step=0.1,
            color="red",
            marks=[
                {"value": 0, "label": "0%"},
                {"value": 5, "label": "5%"},
                {"value": 10, "label": "10%"},
            ],
            size="sm",
            disabled=False,
            showLabelOnHover=False,
            precision=2,
            )

# Date picker

datepicker = html.Div(
                [
                    dmc.DatePicker(
                        id="date-picker",
                        #minDate=date(2020, 8, 5),
                        #inputFormat="MMMM,YY",
                        dropdownType="modal",
                        clearable=False,
                    ),
                ]
            )

# Scenarios in the accordion
# -------
# Growth
growth_message = dmc.Alert(
    children=dmc.Text(""),
    id="growth-message",
    title="",
    color="gray"),

# Plateau
plateau_message = dmc.Alert(
    children=dmc.Text(""),
    id="plateau-message",
    title="",
    color="gray"),

# Valuation
valuation_message = dmc.Alert(
    children=dmc.Text(""),
    id="valuation-message",
    title="",
    color="gray"),

# Correlation
correlation_message = dmc.Alert(
    children=dmc.Text(""),
    id="correlation-message",
    title="",
    color="gray"),

# Accordion
accordion = dmc.AccordionMultiple(
    value="customization",
    variant="separated",
    radius="xl",
    children=[
        dmc.AccordionItem(
            [
                dmc.AccordionControl(
                    "Growth",
                    id="accordion-growth",
                    disabled=True,
                    icon=DashIconify(icon="uit:chart-growth", width=20)
                ),
                dmc.AccordionPanel(
                    growth_message
                ),
            ],
            value="customization",
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl(
                    "Plateau",
                    id="accordion-plateau",
                    disabled=True,
                    icon=DashIconify(icon="radix-icons:pin-top", width=20)
                                     ),
                dmc.AccordionPanel(
                    plateau_message
                ),
            ],
            value="customization",
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl(
                    "Valuation",
                    id="accordion-valuation",
                    disabled=True,
                    icon=DashIconify(icon="radix-icons:rocket", width=20)
                                     ),
                dmc.AccordionPanel(
                    valuation_message
                ),
            ],
            value="customization",
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl(
                    "Correlation",
                    id="accordion-correlation",
                    disabled=True,
                    icon=DashIconify(icon="uit:chart-growth", width=20)
                ),
                dmc.AccordionPanel(
                    correlation_message
                ),
            ],
            value="customization",
        ),
    ],
)

# Graph message
graph_message = dmc.Alert(
    children=dmc.Text("About the graph"),
    id="graph-message",
    title="About the prediction line",
    color="blue",
    hide="True",
    withCloseButton="True"),


# Scenario picker
data_scenarios = ["Most Probable Scenario", "Custom"]

scenarios_picker = dmc.Stack(
    [dmc.SegmentedControl(
        data=data_scenarios,
        radius=20,
        id="scenarios-picker")],
)

# Main plot definition
main_plot = go.Figure()
hovertemplate_maingraph = "%{text}"

# Definition of the different traces
# Main bars
main_plot.add_trace(go.Bar(name="dataset-bars", x=[], y=[],
                          marker_color='Black', hoverinfo='none'))
# Continuous legend for the historical data set
main_plot.add_trace(go.Scatter(name="dataset-line", x=[],
                              y=[], mode='lines', opacity=1,
                              marker_color="Black", showlegend=False, hovertemplate=hovertemplate_maingraph))

# Ignored bars (ignored data for scenario)
main_plot.add_trace(go.Bar(name="ignored-bars", x=[], y=[],
                          marker_color='Grey', hoverinfo='none'))
# Future bars (if past the date picked by the user)
main_plot.add_trace(go.Bar(name="future-bars", x=[], y=[],
                          marker_color='Grey', hoverinfo='none'))
# Prediction line
main_plot.add_trace(go.Scatter(name="prediction-line", x=[], y=[],
                              mode="lines", line=dict(color='#4dabf7', width=2), opacity=0.8,
                              hovertemplate=hovertemplate_maingraph))
# Vertical line for current date
main_plot.add_vline(name="current-date", line_width=1, line_dash="dot",
                   opacity=0.5, x=2023, annotation_text="   Forecast")

# Card where dataset is selected and analysis shown

selector_card = dmc.Card(
    children=[
        dmc.Group(
            [
                dmc.Title("Dataset", order=5),
            ],
            position="apart",
            mt="md",
            mb="xs",
        ),
        dmc.Text(
            "Select a dataset to visualize its historical data and utilize the prediction tool "
            "to forecast its future growth.",
            size="xs",
            color="dimmed",
        ),
        dmc.Space(h=10),
        dropdown6,
        dmc.Group(
                            [
                                dmc.Title("Analysis", order=5),
                            ],
                            position="apart",
                            mt="md",
                            mb="xs",
                ),
        accordion,
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
    # style={"width": 350},
)


functionalities_card = dmc.Card(
    children=[
        dmc.Group(
            [
                dmc.Title("Functionalities", order=5),
            ],
            position="apart",
            mt="md",
            mb="xs",
        ),
        dmc.Text(
            "See where data is heading and move the predicted growth (blue) easily. "
            "For companies, figure out if their worth makes sense right now.",
            size="xs",
            color="dimmed",
        ),
        dmc.Space(h=10),
        dmc.Space(h=10),
        # Plateau slider
        html.Div(
            children=[
                dmc.Group([
                    dmc.Text(
                        "Prediction Line",
                        size="sm",
                        weight=700,
                        ),
                    dmc.Tooltip(
                        DashIconify(icon="feather:info", width=15),
                        label="Select 'Custom' to move the blue curve and see how well it fits the dataset. "
                              "The star indicates GROOWT's best prediction",
                        transition="slide-down",
                        transitionDuration=300,
                        multiline=True,
                    ),
                    dmc.RingProgress(
                        id="r2-ring-progress",
                        size=24,
                        thickness=4,
                        roundCaps=True,
                        sections=[
                            {"value": 0, "color": "LightGrey"},
                            ]
                        ),
                ],
                    spacing=5),

                dmc.Space(h=10),
                dmc.Container(scenarios_picker),
            ]),
        dmc.Space(h=10),
        html.Div(slider_k, style={"marginLeft":15, "marginRight": 15}),
        dmc.Space(h=40),

        # Profit margin
        html.Div(
            style={'display': 'none'},
            id="profit-margin",
            children=[

                dmc.Group(
                    style={'display': 'flex'},
                    children=[
                        dmc.Text(
                            "Profit margin",
                            size="sm",
                            weight=700,
                            ),
                        dmc.Tooltip(
                            DashIconify(icon="feather:info", width=15),
                            label="Adjust the profit margin using the slider to observe the impact on the company's "
                                  "annual average revenue per user. Decreasing the profit margin will increase "
                                  "the amount of revenue required to justify the current market cap.",
                            transition="slide-down",
                            transitionDuration=300,
                            multiline=True,
                        ),
                    ]),
                dmc.Space(h=10),
                dmc.Container(slider_profit_margin),
                dmc.Space(h=25),
                dmc.Text(
                    "Latest annual profit margin: 45%",
                    id="profit-margin-container",
                    size="sm",
                    color="dimmed",
                    ),
        ]),
        dmc.Space(h=20),

# Discount Rate
        html.Div(
            style={'display': 'none'},
            id="discount-rate",
            children=[

                dmc.Group(
                    style={'display': 'flex'},
                    children=[
                        dmc.Text(
                            "Discount Rate",
                            size="sm",
                            weight=700,
                        ),
                        dmc.Tooltip(
                            DashIconify(icon="feather:info", width=15),
                            label="Adjust the discount rate with the slider to match the risks in the company and its "
                                  "industry. Kroll research shows that, on average, the discount rate for consumer "
                                  "staples companies was 8.4% in June 2023, and for information technology companies, "
                                  "it was 11.4%. Raising the rate raises future uncertainty and requires a "
                                  "higher average revenue per user.",
                            transition="slide-down",
                            transitionDuration=300,
                            multiline=True,
                        ),
                    ]),
                dmc.Space(h=10),
                dmc.Container(slider_discount_rate),
                dmc.Space(h=40),
            ]),

# ARPU Growth
        html.Div(
            style={'display': 'none'},
            id="arpu-growth",
            children=[

                dmc.Group(
                    style={'display': 'flex'},
                    children=[
                        dmc.Text(
                            "Revenue (ARPU) Yearly Growth",
                            size="sm",
                            weight=700,
                        ),
                        dmc.Tooltip(
                            DashIconify(icon="feather:info", width=15),
                            label="Adjust the yearly growth of the average revenue per user for the next years. This"
                                  "changes the projected arpu and therefore the value of future users",
                            transition="slide-down",
                            transitionDuration=300,
                            multiline=True,
                        ),
                    ]),
                dmc.Space(h=10),
                dmc.Container(slider_arpu_growth),
                dmc.Space(h=40),
            ]),

# ARPU
        html.Div(
            style={'display': 'none'},
            id="arpu-card",
            children=[

                dmc.Group(
                    style={'display': 'flex'},
                    children=[
                        dmc.Text(
                            "Revenue per User needed",
                            size="sm",
                            weight=700,
                        ),
                        dmc.Tooltip(
                            DashIconify(icon="feather:info", width=15),
                            label="Depending on the profit margin & discount rate you choose, the required Average "
                                  "Annual Revenue per user (ARPU) is displayed below to justify the current valuation."
                                  "Comparing this to the actual current ARPU gives you a clear indication of whether the"
                                  " stock is over or undervalued.",
                            transition="slide-down",
                            transitionDuration=300,
                            multiline=True,
                        ),
                        dmc.Text(
                            id="arpu-needed",
                            children="456$",
                            size="sm",
                            color="Black",
                        ),
                    ],),
                dmc.Space(h=10),
            ]),

        # Datepicker
        html.Div(
            children=[
                dmc.Tooltip(
                    dmc.Group([
                        dmc.Text(
                            "Retrospective Growth",
                            size="sm",
                            weight=700,
                            ),
                        DashIconify(icon="feather:info", width=15)
                        ],
                        spacing=5),
                    label="Pick a date in the past to see how well the current state would have been predicted back then",
                    transition="slide-down",
                    transitionDuration=300,
                    multiline=True,
                ),
                dmc.Space(h=10),
                datepicker,
        ]),
    ],
    id="functionalities-card",
    withBorder=True,
    shadow="sm",
    radius="md",
    style={'display': 'none'},
    #style={"height": 500},
)

# Welcome timeline introducing the user to Groowt

welcome_timeline = html.Div([
    dmc.Timeline(
    active=0,
    bulletSize=25,
    lineWidth=2,
    id='welcome-timeline',
    children=[
        dmc.TimelineItem(
            title="Choose Your Dataset",
            bullet=DashIconify(icon="teenyicons:add-solid", width=12),
            #lineVariant="dashed",
            color="dimmed",
            children=[
                dmc.Text(
                    [
                        "Use the dropdown menu on the side to select a dataset. Analyze its growth and get a "
                        "feeling for when the growth is going to end.",
                        dmc.Anchor("", href="#", size="sm"),
                    ],
                    color="dimmed",
                    size="sm",
                ),
            ],
        ),
        dmc.TimelineItem(
            title="Explore Growth and Valuation",
            bullet=DashIconify(icon="teenyicons:adjust-vertical-alt-outline", width=12),
            lineVariant="dashed",
            children=[
                dmc.Text(
                    [
                        "For publicly traded user-based companies, Assess how much a company "
                        "needs to do to justify its current valuation.",
                        dmc.Anchor(
                            "",
                            href="#",
                            size="sm",
                        ),
                    ],
                    color="dimmed",
                    size="sm",
                ),
            ],
        ),
        dmc.TimelineItem(
            title="Join the community",
            bullet=DashIconify(icon="teenyicons:message-plus-outline", width=12),
            lineVariant="dashed",
            children=[
                dmc.Text(
                    [
                        "Have new datasets or feature requests? Contact us",
                        dmc.Anchor(
                            " here!",
                            href="mailto:groowt@proton.me",
                            size="sm",
                        ),
                    ],
                    color="dimmed",
                    size="sm",
                ),
            ],
        ),
    ],
)])

graph_card = dmc.Card(
    children=[
        # Card Title
        dmc.Group(
                    [
                        dmc.Title("Welcome to GROOWT", id="graph-title", order=5),
                    ],
                    position="apart",
                    mt="md",
                    mb="xs",
                ),
        welcome_timeline,
        html.Div([
        dmc.Text(
                    "Select a dataset first",
                    size="xs",
                    color="dimmed",
                    id='graph-subtitle',
                ),
        dmc.Space(h=20),
        html.Div(graph_message),

        # Card Content
        html.Div(id='graph-container1',
                 children=[dcc.Graph(id='main-graph1', config={'displayModeBar': False, 'scrollZoom': True}
                                     )
                           ]
                 ),
        ],
        id='graph-card-content',
        style={'display': 'none'})
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
)



# Hype meter
hype_meter_bootstrap = dbc.Progress(
    children=
        [
            dbc.Progress(value=30, color="#228BE6", bar=True, label="N-O Assets", id="hype-meter-noa"),
            dbc.Progress(value=30, color="#74C0FC", bar=True, label="Customer Equity", id="hype-meter-users"),
            #dbc.Progress(value=20, color="#D1D1D1", bar=True, animated=True, striped=True, id="hype-meter-delta"),
            dbc.Progress(value=20, color="#D1D1D1", bar=True, animated=True, striped=True, label="Hype", id="hype-meter-hype"),
            dbc.Tooltip("Non-Operating Assets: $3.0B", target="hype-meter-noa", id="hype-tooltip-noa", placement="top"),
            dbc.Tooltip("Customer Equity: $3.0B", target="hype-meter-users", id="hype-tooltip-users", placement="top"),
            #dbc.Tooltip("Delta depending on the chosen scenario", target="hype-meter-delta", id="tooltip-equity-text", placement="top"),
            dbc.Tooltip("Hype: $4.0B", target="hype-meter-hype", id="hype-tooltip-hype", placement="top"),
        ],
    style={"height": "30px", "border-radius": "30px"},
)



hype_meter = dmc.Progress(
    size=40,
    radius="xl",
    styles={"label": {"font-size": "15px", "font-weight": 600}},
    #striped=True,
    #animate=True,
    sections=[
        {"value": 50, "color": "#74C0FC", "label": "Users value", "tooltip": "Users value - $5.0B"},
        {"value": 6, "color": "Gray", "tooltip": "Users value delta - $0.6B"},
        {"value": 11, "color": "#228BE6", "label": "NO Assets", "tooltip": "Non-Operating Assets - $1.1B",
         "animate": True, "striped":True},
    ],
)
data = [
        {"value": "Low", "label": "React", "color":"red"},
        {"value": "Medium", "label": "Angular"},
        {"value": "High", "label": "Svelte"},
        {"value": "Huge", "label": "Vue"},
]
hype_meter_indicator = dmc.Badge("Super hyped", variant="outline", color="red", id="hype-meter-indicator")

hype_meter_card = dmc.Card(
    children=[
        dmc.Group(
            [
                dmc.Title("Hype Meter", order=5), hype_meter_indicator,
            ],
            position="apart",
            mt="md",
            mb="xs",
        ),
        #hype_meter,
        dmc.Stack([
                dmc.Text("Market Cap: $10.1B", size="xs", weight=500, align="center", id="hype-market-cap"),
                hype_meter_bootstrap,
            ],
            align="stretch"
        ),
        dmc.Space(h=20),
        dmc.Text(
            id="hype-meter-text",
            children=["Adjust profit margin, discount rate, and ARPU to evaluate the company's hype through its "
                     "three components: Non-Operating Assets, Customer Equity, and Hype.",
                        #dmc.Text("Non-Operating Assets represent additional valuable company assets.", color="#228BE6"),
                        #dmc.Text("Customer Equity signifies current and future customer-generated profit,"
                        #         " calculated with the selected parameters with a discounted cashflow "
                        #         "method", color="#74C0FC"),
                        #dmc.Text("Hype reflects the current overvaluation of the company in terms of market "
                        #         "capitalization versus actual value.", color="dimmed"),
                        ]
                      ,
            size="xs",
            color="Black",
            style={'display':'inline-block'}
        ),
    ],
    id="hype-meter-card",
    style={'display': 'none'},
    withBorder=True,
    shadow="sm",
    radius="md",
)




# Graph layout

# Build main graph
layout_main_graph = go.Layout(
    # title="User Evolution",
    plot_bgcolor="White",
    margin=go.layout.Margin(
        l=0, #left margin
        r=0, #right margin
        b=0, #bottom margin
        t=20, #top margin
    ),
    legend=dict(
        # Adjust click behavior
        itemclick="toggleothers",
        itemdoubleclick="toggle",
        #orientation="h",
        #x=0.5,
        #y=-0.1,
        yanchor="bottom",
        y=0.01,
        xanchor="right",
        x=0.92,
        font=dict(
            #family="Courier",
            size=10,
            #color="black"
        ),
    ),
    xaxis=dict(
        # title="Timeline",
        linecolor="Grey",
        #hoverformat=".0f",
    ),
    yaxis=dict(
        title="Users",
        linecolor="Grey",
        gridwidth=1,
        gridcolor='#e3e1e1',
        # hoverformat='{y/1e6:.0f} M'
    ),
    showlegend=True,
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
# Build third graph
layout_third_graph = go.Layout(
    # title="User Evolution",
    plot_bgcolor="White",
    legend=dict(
        # Adjust click behavior
        itemclick="toggleothers",
        itemdoubleclick="toggle",
    ),
    xaxis=dict(
        title="# of Data ignored",
        linecolor="Grey",
    ),
    yaxis=dict(
        title="R^2",
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

main_plot.update(
            layout=layout_main_graph
        )


#loading = dcc.Loading(id="loading-component", children=[html.Div([html.Div(id="loading-output")])], type="circle",),

# ----------------------------------------------------------------------------------
# App Layout
app.layout = html.Div(style={'backgroundColor': '#F9F9F9'}, children=
    [navbar6,
     dmc.Space(mb=20),  # Margin/space between the navbar and the content
     # Mantine Grid

dmc.Container(fluid=True, children=[
     dmc.Grid([
        #dmc.Col(span=0.5, lg=0), # Empty left column
        dmc.Col(selector_card, span="auto", order=1),
        dmc.Col(dmc.LoadingOverlay(graph_card), span=12, lg=6, orderXs=3, orderSm=3, orderLg=2),
        dmc.Col([hype_meter_card, dmc.Space(h=20), functionalities_card], span=12, lg=3, orderXs=2, orderSm=2, orderLg=3),
        # dmc.Col(span="auto", lg=0), # Empty right column
         ],
        gutter="xl",
         justify="space-around",
         # align="center",
     ),
    ]),

     dbc.Container(children=[
        # Toast message appearing on top
        #dbc.Row(navbar2),
        # dbc.Row(html.Div(dropdown2)),
        # dbc.Row(dbc.Col(navbar2, style={'clear': 'both', "margin-top": "40px"},
                        # width={"size": 7}), justify="center"),
        # Title row & loading animation

        # Subtitle
        # dbc.Row(dbc.Col(html.Div(children="Have fun estimating the user growth of companies"),
                        # width={"size": 6, "offset": 1})),
        # Dropdown
        # dbc.Row(dbc.Col(html.Div(dropdown), width={"size": 7}), justify="center"),
        # HighChart test
        # dbc.Row(main_chart),
        # Title - You are seeing the evolution of X company
        # dbc.Row(dbc.Col(html.H2(id='title', children=[]), width={"size": 6, "offset": 1}), style={"margin-top": "40px"}),
        # --------------------------------------------------------
        # Slider to go back in time and retrofit

        # Bottom graph of the regression
        #hype_meter,
        dbc.Row(dbc.Col(bottom_card, width={"size": 7}), style={"margin-top": "20px"}, justify="center"),
        # Bottom graph of the evolution of r^2
        dbc.Row(dbc.Col(bottom_bottom_card, width={"size": 7}), style={"margin-top": "20px"}, justify="center"),
        # Storing the key dataframe with all parameters
        dcc.Store(id='users-data'),
        dcc.Store(id='users-dates-raw'),  # DF containing the initial users/dates from the API
        dcc.Store(id='users-dates-formatted'),  # DF containing the users & dates in float for computation
        dcc.Store(id='scenarios-sorted'),  # DF containing all the possible growth scenarios
        dcc.Store(id='current-market-cap'),  # Market cap of the company selected, 0 if N/A
        dcc.Store(id='graph-unit'),  # Graph unit (MAU, Population, etc.)
        dcc.Store(id='launch-counter', data={'flag': False}),  # Counter that shows 0 if no dataset has been selected, or 1 otherwise
        dcc.Store(id='revenue-dates'),  # DF Containing the quarterly revenue and the dates
        dcc.Store(id='current-arpu-stored'),  # DF Containing the current ARPU
        dcc.Store(id='total-assets'),  # DF Containing the current total assets of the company
        dcc.Store(id='users-revenue-correlation'),  # R^2 indicating the strength of the correlation between the KPI
                                                    # used and the revenue
    ], fluid=True)])


# ----------------------------------------------------------------------------------
# Callback behaviours and interaction
# Callback to enable the slider if "Custom" is selected

@app.callback([
    Output("range-slider-k", "disabled"),

    Input("scenarios-picker", "value"),
    Input("dataset-selection", "value")
    ])
def enable_slider(scenario_value, data_selection):
    print(scenario_value)
    if scenario_value == "Custom" and data_selection != None:
        return False,
    else:
        return True,

# Callback to change the Graph's title, enable the analysis buttons
@app.callback([
    Output("accordion-growth", "disabled"),
    Output("accordion-plateau", "disabled"),
    Output("accordion-valuation", "disabled"),
    Output("accordion-correlation", "disabled"),

    Input("dataset-selection", "value")
    ],prevent_initial_call=True)
def select_value(value):
    title = value
    subtitle = "Explore "+str(value)+"'s Historical Data (Bars) and Future Growth Projections. Customize " \
                                     "Predictions with the Slider in the 'Functionalities' Section and Adjust " \
                                     "the Forecast Start Date Using the Datepicker."
    return False, False, False, False

# Callback defining the minimum and the maximum date of the datepicker and loading the dataset
@app.callback([
    Output(component_id='date-picker', component_property='minDate'), # Calculate the min of the new history slider
    Output(component_id='date-picker', component_property='maxDate'), # Calculate the min of the new history slider
    Output(component_id='date-picker', component_property='value'), # Resets the date to the last available date of the dataset
    Output(component_id='users-dates-raw', component_property='data'), # Stores the users + dates data
    Output(component_id='users-dates-formatted', component_property='data'), # Stores the users + dates formatted for computation
    Output(component_id='current-market-cap', component_property='data'), # Stores the company market cap
    Output(component_id='graph-unit', component_property='data'), # Stores the graph unit (y axis legend)
    #Output(component_id='main-graph0', component_property='figure'), # Stores the users + dates formatted for computation
    Output("graph-title", "children"),
    Output("graph-subtitle", "children"),
    #Output(component_id='main-plot-container', component_property='figure'), # Stores the users + dates formatted for computation
    Output(component_id='profit-margin', component_property='style'),  # Show/hide depending on company or not
    Output(component_id='discount-rate', component_property='style'),  # Show/hide depending on company or not
    #Output(component_id='arpu-card', component_property='style'),  # Show/hide depending on company or not
    Output(component_id='hype-meter-card', component_property='style'),  # Show/hide depending on company or not
    Output(component_id='arpu-growth', component_property='style'),  # Show/hide depending on company or not
    Output(component_id='profit-margin-container', component_property='children'),  # Change the text below the profit margin slider
    Output(component_id='range-profit-margin', component_property='marks'),  # Adds a mark to the slider if the profit margin > 0
    Output(component_id='range-profit-margin', component_property='value'),  # Sets the value to the current profit margin
    Output(component_id='current-arpu-stored', component_property='data'),  # Stores the current arpu
    Output(component_id='total-assets', component_property='data'),  # Stores the current arpu
    Output(component_id='hype-market-cap', component_property='children'),  # Stores the current arpu
    Output(component_id='users-revenue-correlation', component_property='data'),  # Stores the correlation between
    # the chosen KPI and the revenue

    Input(component_id='dataset-selection', component_property='value')], # Take dropdown value
    #[State('main-plot-container', 'figure')],
    prevent_initial_call=True,
)
def set_history_size(dropdown_value):
    t1 = time.perf_counter(), time.process_time()
    try:
        # Fetch dataset from API
        df = dataAPI.get_airtable_data(dropdown_value)
        key_unit = df.loc[0, 'Unit']
        print("DF", df)

        # Creating the title & subtitle for the graph
        title = dropdown_value + " - " + key_unit
        subtitle = "Explore " + str(dropdown_value) + "'s Historical " + key_unit + " Data (Bars) and Future Growth " \
                                                                                    "Projections. Customize " \
                                             "Predictions with the Slider in the 'Functionalities' Section and Adjust " \
                                             "the Forecast Start Date Using the Datepicker."

        # Transforming it to a dictionary to be stored
        users_dates_dict = df.to_dict(orient='records')
        print("USERDATESDICT", users_dates_dict)

        # Process & format df. The dates in a panda serie of format YYYY-MM-DD are transformed to a decimal yearly array
        dates = np.array(main.date_formatting(df["Date"]))
        dates_formatted = dates + YEAR_OFFSET
        dates_unformatted = np.array(df["Date"])
        users_formatted = np.array(df["Users"]).astype(float) * 1000000

        # Logic to be used when implementing changing the ARPU depending on the date picked
        #date_last_quarter = main.previous_quarter_calculation().strftime("%Y-%m-%d")
        #closest_index = main.find_closest_date(date_last_quarter,dates_unformatted)

        current_users = users_formatted[-1]

        # Check whether it is a public company: Market cap fetching & displaying profit margin,
        # discount rate and arpu for Companies
        symbol_company = df.loc[0, 'Symbol']
        if symbol_company != "N/A":
            current_market_cap = dataAPI.get_marketcap(symbol_company)  # Sets valuation if symbol exists
            hype_market_cap = f"Market Cap: ${current_market_cap/1000:.2f}B" # Formatted text for hype meter
            show_company_functionalities = {'display': 'block'}  # Style component showing the fin. function.
            yearly_revenue, total_assets = dataAPI.get_previous_quarter_revenue(symbol_company) # Getting with API
            filtered_revenue_df = df[df["Revenue"] != 0] # Getting rid of the revenue != 0
            quarterly_revenue = np.array(filtered_revenue_df["Revenue"]) * 1_000_000 # Getting in database
            yearly_revenue_quarters = sum(quarterly_revenue[-4:])
            # Regression between Users and revenue
            users_revenue_regression = main.linear_regression(users_formatted[-len(quarterly_revenue):],
                                                              quarterly_revenue)
            try:
                if yearly_revenue != 0:
                    #current_arpu = yearly_revenue/current_users
                    current_arpu = sum(quarterly_revenue[-4:] / users_formatted[-4:]) # More
                else:
                    current_arpu = yearly_revenue_quarters/current_users
                    printed_current_arpu = f"{current_arpu:.0f} $ (current arpu)"  # formatting
            except ZeroDivisionError:
                printed_current_arpu = "Error: Division by zero. Cannot calculate the current ARPU."
                current_arpu = 0
            except Exception as e:
                printed_current_arpu = f"Error calculating the current ARPU: {str(e)}"
                current_arpu = 0

            # Profit margin text and marks
            current_annual_profit_margin = dataAPI.get_profit_margin(symbol_company)
            marks_profit_margin_slider = []
            print("Company Current ARPU:", current_arpu)
            if current_annual_profit_margin > 1:
                value_profit_margin_slider = float(current_annual_profit_margin)
                marks_profit_margin_slider = [
                    {"value": 2, "label": "2%"},
                    {"value": 10, "label": "10%"},
                    {"value": 20, "label": "20%"},
                    #{"value": value_profit_margin_slider, "label": "⭐"},
                    {"value": 50, "label": "50%"},
                ]
                text_profit_margin = "Latest annual profit margin: " + str(current_annual_profit_margin) + "% 🤩",
                print("Marks", type(marks_profit_margin_slider))
                print(type(current_annual_profit_margin))

            else:
                marks_profit_margin_slider = [
                    {"value": 2, "label": "2%"},
                    {"value": 10, "label": "10%"},
                    {"value": 20, "label": "20%"},
                    {"value": 50, "label": "50%"},
                ]
                value_profit_margin_slider = 5.0
                text_profit_margin = "Latest annual profit margin: " + str(current_annual_profit_margin) + "% 😰",

        else:
            current_market_cap = 0  # Otherwise, market_cap = zero
            current_arpu = 0
            total_assets = 0
            hype_market_cap = ""
            show_company_functionalities = {'display': 'none'}
            users_revenue_regression = 0
            printed_current_arpu = 0
            text_profit_margin =""
            value_profit_margin_slider = 5.0
            marks_profit_margin_slider = [
                {"value": 2, "label": "2%"},
                {"value": 10, "label": "10%"},
                {"value": 20, "label": "20%"},
                {"value": 50, "label": "50%"},
            ]

        print("MARKSFINAL", marks_profit_margin_slider)

        df_formatted = df
        df_formatted["Date"] = dates_formatted

        # Final DF containing dates, users, Units, Symbols & Quarterly revenue
        users_dates_formatted_dict = df_formatted.to_dict(orient='records')

        min_history_datepicker = str(dates_unformatted[MIN_DATE_INDEX])  # Minimum date that can be picked
        max_dataset_date = datetime.strptime(dates_unformatted[-1], "%Y-%m-%d") # Fetching the last date of the dataset
        max_history_datepicker_date = max_dataset_date + timedelta(days=1)  # Adding one day to the max, to include all dates
        max_history_datepicker = max_history_datepicker_date.strftime("%Y-%m-%d")
        date_value_datepicker = max_history_datepicker  # Sets the value of the datepicker as the max date
        current_date = dates_formatted[-1]



        # Graph creation
        fig_main = go.Figure(layout=layout_main_graph)
        hovertemplate_maingraph = "%{text}"
        y_legend_title = key_unit

        # Trial to create the basis of a graph here to only update the lines in another callback, but couldn't manage it
        '''
        # Calculate the desired X-axis range based on the first and last date in the dataset
        x_axis_start = dates_formatted[0]
        x_axis_end = dates_formatted[-1]+((dates_formatted[-1] - dates_formatted[0]) * 0.2)  # We see "20%" in the future

        # Update X-axis range to fix the size
        x_axis_range = [x_axis_start, x_axis_end + (x_axis_end - x_axis_start)]
        # x_axis = [dates[0] + 1970, dates[-1] * 2 - dates[0] + 1970]
        fig_main.update_xaxes(range=x_axis_range)

        # Set y legend
        fig_main.update_layout(
            yaxis=dict(
                title=str(y_legend_title),
            )
        )

        # Definition of the different traces
        # Main bars
        main_plot_bars = go.Bar(name="dataset-bars", x=dates_formatted, y=users_formatted,
                                marker_color='Black', hoverinfo='none')
        existing_main_plot['data'].append(main_plot_bars)

        fig_main.add_trace(go.Bar(name="dataset-bars", x=dates_formatted, y=users_formatted,
                                  marker_color='Black', hoverinfo='none'))
        # Continuous legend for the historical data set
        formatted_y_values = [f"{y / 1e6:.1f} M" if y < 1e9 else f"{y / 1e9:.2f} B" for y in users_formatted]
        fig_main.add_trace(go.Scatter(name="dataset-line", x=dates_formatted,
                                      y=users_formatted, mode='lines', opacity=1,
                                      marker_color="Black", showlegend=False, text=formatted_y_values,
                                      hovertemplate=hovertemplate_maingraph))
        main_plot_dataset = (go.Scatter(name="dataset-line", x=dates_formatted,
                                      y=users_formatted, mode='lines', opacity=1,
                                      marker_color="Black", showlegend=False, text=formatted_y_values,
                                      hovertemplate=hovertemplate_maingraph))
        existing_main_plot['data'].append(main_plot_dataset)

        # Vertical line indicating the date picked
        main_plot_date_picked = go.Scatter(
            x=[current_date, current_date],
            y=[0, users_formatted[-1] * 1.1],  # Adjust the y-values based on your plot range
            mode='lines',
            name='Vertical Line',
            line=dict(color='green', width=1, dash="dot"),
            opacity=0.5,
        )
        existing_main_plot['data'].append(main_plot_date_picked)

        # Ignored bars (ignored data for scenario)
        fig_main.add_trace(go.Bar(name="ignored-bars", x=[], y=[],
                                  marker_color='Grey', hoverinfo='none'))
        # Future bars (if past the date picked by the user)
        fig_main.add_trace(go.Bar(name="future-bars", x=[], y=[],
                                  marker_color='Grey', hoverinfo='none'))
        # Prediction line
        fig_main.add_trace(go.Scatter(name="prediction-line", x=[], y=[],
                                      mode="lines", line=dict(color='#4dabf7', width=2), opacity=0.8,
                                      text=formatted_y_values, hovertemplate=hovertemplate_maingraph))
        # Vertical line for current date
        fig_main.add_vline(name="current-date", x=current_date, line_width=1, line_dash="dot",
                            opacity=0.5, annotation_text="   Forecast")
        '''
        t2 = time.perf_counter(), time.process_time()
        print(f" Calculation of the different sliders")
        print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
        print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
        return min_history_datepicker, max_history_datepicker, date_value_datepicker, users_dates_dict, \
            users_dates_formatted_dict, current_market_cap, y_legend_title, title, subtitle, \
            show_company_functionalities, show_company_functionalities, show_company_functionalities, \
            show_company_functionalities, text_profit_margin, marks_profit_margin_slider, \
            value_profit_margin_slider, current_arpu, total_assets, hype_market_cap, users_revenue_regression
    except Exception as e:
        print(f"Error fetching or processing dataset: {str(e)}")
        return "", "", "", "", "", "", "", "", "",

@app.callback(
    # Output("loading-component", "loading"),
    Output(component_id='range-slider-k', component_property='value'), # Reset slider value to the best value
    Output(component_id="growth-message", component_property="title"),
    Output(component_id="growth-message", component_property="children"),
    Output(component_id="growth-message", component_property="color"),
    Output(component_id="growth-message", component_property="value"),
    Output(component_id="plateau-message", component_property="title"),
    Output(component_id="plateau-message", component_property="children"),
    Output(component_id="plateau-message", component_property="color"),
    Output(component_id="valuation-message", component_property="title"),
    Output(component_id="valuation-message", component_property="children"),
    Output(component_id="valuation-message", component_property="color"),
    Output(component_id="correlation-message", component_property="title"),
    Output(component_id="correlation-message", component_property="children"),
    Output(component_id="correlation-message", component_property="color"),
    Output(component_id='scenarios-sorted', component_property='data'),
    Output(component_id='range-slider-k', component_property='max'),
    Output(component_id='range-slider-k', component_property='marks'),

    Input(component_id='dataset-selection', component_property='value'),  # Take dropdown value
    Input(component_id='date-picker', component_property='value'),  # Take date-picker date
    Input("scenarios-picker", "value"),  # Input the scenario to reset the position of the slider to the best scenario
    Input(component_id='users-dates-formatted', component_property='data'),
    Input(component_id='current-market-cap', component_property='data'),
    Input(component_id='users-revenue-correlation', component_property='data'),
    Input(component_id='graph-unit', component_property='data'),  # Getting the Unit used
    prevent_initial_call=True)

# Analysis to load the different scenarios (low & high) when a dropdown value is selected
def load_data(dropdown_value, date_picked, scenario_value, df_dataset_dict, current_market_cap,
              users_revenue_correlation, key_unit):
    print("Starting scenarios calculation")
    t1 = time.perf_counter(), time.process_time()
    date_picked_formatted = main.date_formatting_from_string(date_picked)

    # The data is loaded from airtable
    #df = dataAPI.get_airtable_data(dropdown_value)

    # Dates array definition from dictionary
    dates_new = np.array([entry['Date'] for entry in df_dataset_dict])
    dates = dates_new - 1970
    # Users are taken from the database and multiply by a million
    users_new = np.array([entry['Users'] for entry in df_dataset_dict])
    users = users_new.astype(float) * 1000000
    #print(df)

    # Test to be deleted, changing dates & users to use moving average
    dates, users = main.moving_average_smoothing(dates, users, 1)

    # Resizing of the dataset taking into account the date picked
    history_value_formatted = date_picked_formatted-1970  # New slider: Puts back the historical value to the format for computations
    dates_actual = main.get_earlier_dates(dates, history_value_formatted)
    data_len = len(dates_actual)  # length of the dataset to consider for retrofitting

    # All parameters are calculated by ignoring data 1 by 1, taking the history reference as the end point
    df_full = main.parameters_dataframe(dates[0:data_len], users[0:data_len])  # Dataframe containing all parameters with all data ignored
    print("df_full", df_full)
    df_sorted = main.parameters_dataframe_cleaning(df_full, users[0:data_len])  # Dataframe where inadequate scenarios are eliminated
    if df_sorted.empty:
        print("No good scenario could be calculated")
        df_sorted = main.parameters_dataframe_cleaning_minimal(df_full, users[0:data_len])
    else:
        print("Successful scenarios exist")
    print("df_sorted", df_sorted)
    df_sorted_dict = df_sorted.to_dict(orient='records')  # Transforming it to dict to be stored
    if dropdown_value is None:  # Exception for when dropdown is not selected yet, initializing df
        df = df_full
    current_valuation = 100
    if date_picked_formatted:
        if df_sorted.empty:
            state_alert = True
        else:
            state_alert = False


    # Best scenario definition ---> Index of the row containing the highest R^Square
    highest_r2_index = df_sorted['R Squared'].idxmax()


    # Scenario analysis
    # Growth: for the best growth scenario (highest R^2), if the difference between the log R^2 and the linear R^2
    #           is <0.1, then that means the growth is stabilizing and a classical logistic growth is to be expeced
    #           if it is > 0.1 then it means that the dataset is still in its exponential growth and the probability
    #           for exponential growth is high

    diff_r2lin_log = df_sorted.at[highest_r2_index, 'Lin/Log Diff']

# Growth Accordion
# Promising Growth
    if diff_r2lin_log > 0.1:
        growth_message_title = "Promising Exponential Growth Ahead!"
        growth_message_body = "Groowt's model predicts a strong likelihood of exponential growth in the foreseeable " \
                              "future, surpassing the best-case scenario displayed."
        growth_message_color = "green"

# Stable Growth
    else:
        growth_message_title = "Consistent and Predictable Growth!"
        growth_message_body = "Groowt's model suggests a high probability that the dataset has transitioned into a " \
                              "stable growth pattern, aligning closely with our best-case scenario."
        growth_message_color = "yellow"

# Plateau definition & time to 90% of the plateau

    k_scenarios = np.array(df_sorted['K'])
    r_scenarios = np.array(df_sorted['r'])
    p0_scenarios = np.array(df_sorted['p0'])

    # High Growth
    if k_scenarios[-1] < 1e9:
        plateau_high_growth = f"{k_scenarios[-1] / 1e6:.1f} M"
    else:
        plateau_high_growth = f"{k_scenarios[-1] / 1e9:.1f} B"
    time_high_growth = main.time_to_population(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1],
                                               k_scenarios[-1]*0.9)+1970
    # Low Growth
    if k_scenarios[0] < 1e9:
        plateau_low_growth = f"{k_scenarios[0] / 1e6:.1f} M"
    else:
        plateau_low_growth = f"{k_scenarios[0] / 1e9:.1f} B"
    time_high_growth = main.time_to_population(k_scenarios[0], r_scenarios[0], p0_scenarios[0],
                                               k_scenarios[0] * 0.9)+1970
    # Best Growth
    if k_scenarios[highest_r2_index] < 1e9:
        plateau_best_growth = f"{k_scenarios[highest_r2_index] / 1e6:.1f} M"
    else:
        plateau_best_growth = f"{k_scenarios[highest_r2_index] / 1e9:.1f} B"
    time_best_growth = main.time_to_population(k_scenarios[highest_r2_index],
                                               r_scenarios[highest_r2_index],
                                               p0_scenarios[highest_r2_index],
                                               k_scenarios[highest_r2_index] * 0.9)+1970

    # Plateau Accordion
    if diff_r2lin_log > 0.1:
        plateau_message_title = "Plateau could be reached in " + main.string_formatting_to_date(time_high_growth) \
                               + " with " + str(plateau_high_growth) + " users "
        plateau_message_body = "Given the likelihood of exponential growth in the foreseeable " \
                              "future, the high growth scenario is likely with a plateau at " + \
                              str(plateau_high_growth) + " users which should happen in " + main.string_formatting_to_date(time_high_growth)
    else:
        plateau_message_title = "Plateau could be reached in " + main.string_formatting_to_date(time_best_growth) \
                               + " with " + str(plateau_best_growth) + " users"
        plateau_message_body = "Given the likelihood of a stable growth in the foreseeable " \
                              "future, the best growth scenario is likely to reach its plateau in " \
                              + main.string_formatting_to_date(time_best_growth) + " with " + str(plateau_best_growth) + " users"

    # Plateau Accordion
    arpu_needed = main.arpu_for_valuation(k_scenarios[highest_r2_index], r_scenarios[highest_r2_index],
                                          p0_scenarios[highest_r2_index], 0.2, 0.05, 10, current_market_cap*1000000)
    # Formating the displayed market cap:
    if current_market_cap >= 1000:
        formatted_market_cap = f"{current_market_cap / 1000:.2f} B$"
    else:
        formatted_market_cap = f"{current_market_cap} mio$"
    if current_market_cap != 0:
        valuation_message_title = "Current market cap is " + str(formatted_market_cap)
        valuation_message_body = "Given the projected user growth, " + str(dropdown_value) + " should make " + \
                                 f"{arpu_needed:.0f} $" + " per user and per year to justify the current market cap " \
                                                    "(assuming a 20% profit margin & a 5% discount rate)"
        valuation_message_color = "green"
    else:
        valuation_message_title = "Valuation not applicable"
        valuation_message_body = "The valuation information is only relevant for companies"
        valuation_message_color = "gray"

    # Formatting of the displayed correlation message
    print("CORRELATION", users_revenue_correlation)
    # Formating the displayed r^2:
    formatted_correlation = f"{users_revenue_correlation:.2f}"
    if users_revenue_correlation >= 0.9:
        correlation_message_title = "Great metric selected!"
        correlation_message_body = "The " + str(key_unit) + " you are using seem to be the right metric to " \
                                                            "estimate the valuation, because there is a very strong " \
                                                            "correlation between the " + str(key_unit) +\
                                 " and the revenue (R^2 = " + str(formatted_correlation) +")"
        correlation_message_color = "green"
    elif users_revenue_correlation > 0:
        correlation_message_title = "Another metric could be better"
        correlation_message_body = str(key_unit) + "do not have a strong correlation with the revenue over time. " \
                                                   "You may want to consider another metric to estimate this " \
                                                   "company's valuation (R^2 = " + str(formatted_correlation) +")"
        correlation_message_color = "Yellow"

    else:
        correlation_message_title = "Correlation not applicable"
        correlation_message_body = "The correlation information is only relevant for companies"
        correlation_message_color = "gray"

    # Slider definition
    df_scenarios = df_sorted
    data_ignored_array = df_scenarios.index.to_numpy()
    slider_max_value = data_ignored_array[-1]

    # Slider max definition
    if k_scenarios[-1] >= 1_000_000_000:  # If the max value of the slider is over 1 B
        if highest_r2_index == data_ignored_array[-1]:  # If the best = max, then display them side by side"
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000000000:.1f}B"},
                {"value": data_ignored_array[-1], "label": f"★{k_scenarios[-1] / 1000000000:.1f}B"},
            ]
        elif highest_r2_index == data_ignored_array[0]:  # If the best = mind, then display them side by side"
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"★{k_scenarios[0] / 1000000000:.1f}B"},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1] / 1000000000:.1f}B"},
            ]
        else:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000000000:.1f}B"},
                {"value": highest_r2_index, "label": "★"},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1] / 1000000000:.1f}B"},
            ]
    elif k_scenarios[-1] >= 1_000_000:
        if highest_r2_index == data_ignored_array[-1]:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0]/1000000:.0f}M"},
                {"value": data_ignored_array[-1], "label": f"★{k_scenarios[-1]/1000000:.0f}M"},
            ]
        elif highest_r2_index == data_ignored_array[0]:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"★{k_scenarios[0] / 1000000:.0f}M"},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1] / 1000000:.0f}M"},
            ]
        else:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0]/1000000:.0f}M"},
                {"value": highest_r2_index, "label": "★"},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1]/1000000:.0f}M"},
            ]

    else :  # If K max smaller than 1 million
        if highest_r2_index == data_ignored_array[-1]:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0]/1000:.0f}K"},
                {"value": data_ignored_array[-1], "label": f"★{k_scenarios[-1]/1000:.0f}K"},
            ]
        elif highest_r2_index == data_ignored_array[0]:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"★{k_scenarios[0] / 1000:.0f}K"},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1] / 1000:.0f}K"},
            ]
        else:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0]/1000:.0f}K"},
                {"value": highest_r2_index, "label": "★"},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1]/1000:.0f}K"},
            ]

    # Updating the datepicker graph traces, the high & the low growth scenario
    main_plot.update_traces(
        selector=dict(name="current-date"),
        x=date_picked_formatted,
    )
    t2 = time.perf_counter(), time.process_time()
    print(f" Scenarios calculation")
    print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
    return highest_r2_index, growth_message_title, growth_message_body, growth_message_color, \
        "customization", plateau_message_title, plateau_message_body, "blue", valuation_message_title, \
        valuation_message_body, valuation_message_color, correlation_message_title, correlation_message_body, \
        correlation_message_color,  df_sorted_dict, slider_max_value, marks_slider

@app.callback([
    Output(component_id='main-graph1', component_property='figure'),  # Update graph 1
    # Output(component_id='main-graph2', component_property='figure'),  # Update graph 2 about regression
    # Output(component_id='main-graph3', component_property='figure'),  # Update graph 3
    #Output(component_id='carrying-capacity', component_property='children'),  # Update the carrying capacity
    Output(component_id='r2-ring-progress', component_property='sections'),  # Update regression
    #Output(component_id='range-slider-k', component_property='max'),
    #Output(component_id='range-slider-k', component_property='marks'),
    Output(component_id='graph-message', component_property='hide'),
    Output(component_id='graph-message', component_property='children'),
    ],

    [
    Input(component_id='range-slider-k', component_property='value'),  # Take user slider value
    Input(component_id='date-picker', component_property='value'), # Take date-picker date
    Input(component_id='users-dates-formatted', component_property='data'),
    Input(component_id='scenarios-sorted', component_property='data'),
    Input(component_id='graph-unit', component_property='data'),  # Stores the graph unit (y axis legend)
    Input(component_id='users-dates-raw', component_property='data'),
    Input(component_id='range-arpu-growth', component_property='value'),
    Input(component_id='current-arpu-stored', component_property='data'),
    ], prevent_initial_call=True)
def graph_update(data_slider, date_picked_formatted_original, df_dataset_dict, df_scenarios_dict, graph_unit, df_raw,
                 arpu_growth, current_arpu):
    # --------- Data Loading
    t1 = time.perf_counter(), time.process_time()
    # Data prepared earlier is fetched here
    # Dates array definition from dictionary
    dates = np.array([entry['Date'] for entry in df_dataset_dict])
    dates_raw = np.array([entry['Date'] for entry in df_raw])
    dates = dates - 1970
    # Users are taken from the database and multiply by a million
    users = np.array([entry['Users'] for entry in df_dataset_dict])
    users = users.astype(float) * 1000000
    arpu_growth = arpu_growth/100

    print("datepIckedinItial", date_picked_formatted_original)
    # Gets the date selected from the new date picker
    date_picked_formatted = main.date_formatting_from_string(date_picked_formatted_original)
    history_value = date_picked_formatted
    history_value_graph = datetime.strptime(date_picked_formatted_original, "%Y-%m-%d")
    print(history_value_graph)
    print(date_picked_formatted)
    # Extract the x-coordinate for the vertical line
    x_coordinate = history_value_graph

    # Calculating the length of historical values to be considered in the plots
    # history_value_formatted = history_value[0] - 1970  # Puts back the historical value to the format for computations
    history_value_formatted = date_picked_formatted - 1970  # New slider: Puts back the historical value to the format for computations
    dates_actual = main.get_earlier_dates(dates, history_value_formatted)
    data_len = len(dates_actual)  # length of the dataset to consider for retrofitting
    users_actual = users[0:data_len]

    print("Selected date", date_picked_formatted)
    print(graph_unit)


    # If selecting all possible scenarios,  Creation of the arrays of parameters
    k_scenarios = np.array([entry['K'] for entry in df_scenarios_dict])
    r_scenarios = np.array([entry['r'] for entry in df_scenarios_dict])
    p0_scenarios = np.array([entry['p0'] for entry in df_scenarios_dict])
    rsquared_scenarios = np.array([entry['R Squared'] for entry in df_scenarios_dict])
    number_ignored_data_scenarios = np.array([entry['Data Ignored'] for entry in df_scenarios_dict])

    # Based on the slider's value, the related row of parameters is selected
    row_selected = data_slider
    # Parameters definition
    k = k_scenarios[row_selected]
    r = r_scenarios[row_selected]
    p0 = p0_scenarios[row_selected]
    r_squared_showed = np.round(rsquared_scenarios[row_selected], 3)
    number_ignored_data = int(number_ignored_data_scenarios[row_selected])

    # R^2 Ring progress definition of the selected prediction line
    value_section = r_squared_showed*100
    if r_squared_showed > 0.9:
        sections = [
            {"value": value_section, "color": "Green", "tooltip": "Very Good"},
        ]
    elif 0.6 < r_squared_showed <= 0.9:
        sections = [
            {"value": value_section, "color": "LightGreen", "tooltip": "Good"},
        ]

    elif 0.4 < r_squared_showed <= 0.6:
        sections = [
            {"value": value_section, "color": "Yellow", "tooltip": "Medium"},
        ]

    elif r_squared_showed <= 0.4:
        sections = [
            {"value": value_section, "color": "Red", "tooltip": "Meeeeh"},
        ]

    else:
        sections = [
            {"value": value_section, "color": "LightGrey", "tooltip": "Computation issue"},
        ]

    print("Value Ring", value_section, r_squared_showed)



    highest_r2_index = np.argmax(rsquared_scenarios)
    print("HIGHEST", highest_r2_index)

    # Graph message

    # Selected Growth
    if k_scenarios[data_slider] < 1e9:
        plateau_selected_growth = f"{k_scenarios[data_slider] / 1e6:.1f} M"
    else:
        plateau_selected_growth = f"{k_scenarios[data_slider] / 1e9:.1f} B"
    time_selected_growth = main.time_to_population(k_scenarios[data_slider],
                                               r_scenarios[data_slider],
                                               p0_scenarios[data_slider],
                                               k_scenarios[data_slider] * 0.9)+1970

    graph_message = "Anticipated Plateau Date (blue line): " + main.string_formatting_to_date(time_selected_growth) + ", Projected at " + \
                    str(plateau_selected_growth) + " users"



    # Polynomial approximation
    # logfit = main.log_approximation(dates[number_ignored_data:data_len], users[number_ignored_data:data_len])
    #k_log = np.exp(-logfit[1]/logfit[0])
    #df_log = main.parameters_dataframe_given_k(dates[0:data_len], users[0:data_len])
    #print("LOG params")
    #print(df_log)
    #polynum3 = main.polynomial_approximation(dates[number_ignored_data:data_len], users[number_ignored_data:data_len], 3)
    #polynum2 = main.polynomial_approximation(dates[number_ignored_data:data_len], users[number_ignored_data:data_len],
                                             # 2)
    #polynum1 = main.polynomial_approximation(dates[number_ignored_data:data_len], users[number_ignored_data:data_len], 1)

    # Calculating the other parameters, given K provided by the log approximation
    # r_log, p0_log, r_squared_log = main.logistic_parameters_given_K(dates[number_ignored_data:data_len],
                                                     # users[number_ignored_data:data_len], k_log)
    # Build Main Chart
    # ---------------------
    hovertemplate_maingraph = "%{text}"
    #fig_main = go.Figure(layout=layout_main_graph)
    fig_main = make_subplots(specs=[[{"secondary_y": True}]])
    fig_main.update_layout(layout_main_graph)
    x_axis = [dates[0] + 1970, dates[-1] * 2 - dates[0] + 1970]
    #fig_main.update_xaxes(range=x_axis)  # Fixing the size of the X axis with users max + 10%
    fig_main.update_yaxes(range=[0, k_scenarios[-1]*1.1])  # Fixing the size of the Y axis
    # Historical data
    # Highlight points considered for the approximation
    fig_main.add_trace(go.Bar(name="Dataset", x=dates_raw[number_ignored_data:data_len],
                              y=users[number_ignored_data:data_len],
                              marker_color="Black", showlegend=False, hoverinfo='none'))
    y_predicted = users
    formatted_y_values = [f"{y / 1e6:.1f} M" if y < 1e9 else f"{y / 1e9:.2f} B" for y in y_predicted]
    # Line linking the historical data for smoothing the legend hover
    fig_main.add_trace(go.Scatter(name="Historical data", x=dates_raw,
                              y=y_predicted, mode='lines', opacity=0,
                              marker_color="Black", text=formatted_y_values, hovertemplate=hovertemplate_maingraph))
    # Highlight points not considered for the approximation
    fig_main.add_trace(
        go.Bar(name="Data omitted", x=dates_raw[0:number_ignored_data], y=users[0:number_ignored_data],
               marker_color="Grey", hoverinfo='none', showlegend=False))
    # Highlight points past the current date
    fig_main.add_trace(go.Bar(name="Forecast Range", x=dates_raw[data_len:],
                              y=users[data_len:],
                              marker_color='#e6ecf5', hoverinfo='none',))
    print("AQUI", date_picked_formatted_original)
    print(x_coordinate)
    # Add vertical line indicating the year of the prediction for retrofitting
    #fig_main.add_vline(x=history_value_graph, line_width=1, line_dash="dot",
                       #opacity=0.5, annotation_text="   Forecast")
    fig_main.add_shape(
        go.layout.Shape(
            type="line",
            x0=x_coordinate,
            x1=x_coordinate,
            y0=0,
            y1=k_scenarios[-1],
            line=dict(color="gray", width=1, dash="dot"),
        )
    )
    print("asdfasdf")
    # Update layout to customize the annotation
    fig_main.update_layout(
        hovermode="x unified",
        annotations=[
            dict(
                x=x_coordinate,
                y=0.9*k_scenarios[-1],  # Adjust the y-position as needed
                text="                      F O R E C A S T",
                showarrow=False,
                font=dict(
                    size=8,  # Adjust the size as needed
                    color="black",  # Text color
                    # letter=5,
                ),
                opacity=0.3  # Set the opacity
            )
        ],
        yaxis=dict(
            fixedrange=True,
            title=graph_unit,
        ),
        xaxis=dict(
            # title="Timeline",
            #linecolor="Grey",

        ),
        dragmode="pan",
    )
    fig_main.update_yaxes(fixedrange=True, secondary_y=True)

    # Prediction, S-Curves


    date_a = datetime.strptime(dates_raw[0], "%Y-%m-%d")
    date_b = datetime.strptime(dates_raw[-1], "%Y-%m-%d")

    # Calculate date_end using the formula date_b + 2 * (date_b - date_a)
    date_end = date_b + (date_b - date_a)
    print(dates[-1]*2-dates[0])
    print(date_end)

    date_end_formatted = main.date_formatting_from_string(date_end.strftime("%Y-%m-%d"))
    print(date_end_formatted)

    # Add S-curve - S-Curve the user can play with
    x = np.linspace(dates[0], float(date_end_formatted)-1970, num=50)
    y_predicted = main.logisticfunction(k, r, p0, x)

    x_scenarios = np.linspace(dates[-1], float(date_end_formatted)-1970, num=50)

    # Generate x_dates array
    x_dates = np.linspace(date_a.timestamp(), date_end.timestamp(), num=50)
    x_dates_scenarios = np.linspace(date_b.timestamp(), date_end.timestamp(), num=50)
    x_dates = [datetime.fromtimestamp(timestamp) for timestamp in x_dates]
    x_dates_scenarios = [datetime.fromtimestamp(timestamp) for timestamp in x_dates_scenarios]


    print(x_dates)
    print(x)
    #print(len(x_dates), x_dates)
    #print(len(x), x)
    formatted_y_values = [f"{y / 1e6:.1f} M" if y < 1e9 else f"{y / 1e9:.2f} B" for y in y_predicted]
    fig_main.add_trace(go.Scatter(name="Prediction", x=x_dates, y=y_predicted,
                                  mode="lines", line=dict(color='#4dabf7', width=2), opacity=0.8,
                                  text=formatted_y_values, hovertemplate=hovertemplate_maingraph))
    # Add 3 scenarios
    x0 = np.linspace(dates_actual[-1] + 0.25, dates_actual[-1]*2-dates_actual[0], num=10)  # Creates a future timeline the size of the data

    # Low growth scenario
    #x = np.linspace(dates[-1], dates[-1] * 2 - dates[0], num=50)
    y_trace = main.logisticfunction(k_scenarios[0], r_scenarios[0], p0_scenarios[0], x_scenarios)
    formatted_y_values = [f"{y / 1e6:.1f} M" if y < 1e9 else f"{y / 1e9:.2f} B" for y in y_trace]
    fig_main.add_trace(go.Scatter(name="Low growth", x=x_dates_scenarios,
                             y=main.logisticfunction(k_scenarios[0], r_scenarios[0], p0_scenarios[0], x_scenarios), mode='lines',
                             line=dict(color='LightGrey', width=0.5), showlegend=False, text=formatted_y_values, hovertemplate=hovertemplate_maingraph)),
    #fig.add_trace(go.Line(name="Predicted S Curve", x=x + 1970,
                             #y=main.logisticfunction(k_scenarios[1], r_scenarios[1], p0_scenarios[1], x), mode="lines"))
    y_trace = main.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1], x_scenarios)
    formatted_y_values = [f"{y / 1e6:.1f} M" if y < 1e9 else f"{y / 1e9:.2f} B" for y in y_trace]
    # High growth scenario, if existent
    if len(k_scenarios) > 1:
        fig_main.add_trace(go.Scatter(name="High Growth", x=x_dates_scenarios,
                             y=y_trace, mode='lines',
                             line=dict(color='LightGrey', width=0.5),
                                      textposition="top left", textfont_size=6, showlegend=False,
                                      text=formatted_y_values, hovertemplate=hovertemplate_maingraph))
    y_trace = main.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1], x)
    # Filling the area of possible scenarios
    x_area = np.append(x, np.flip(x))  # Creating one array made of two Xs
    y_area_low = main.logisticfunction(k_scenarios[0], r_scenarios[0], p0_scenarios[0], x) # Low growth array
    y_area_high = main.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1], np.flip(x)) # High growth array
    y_area = np.append(y_area_low, y_area_high)
    dates_area = np.append(x_dates, np.flip(x_dates))
    fig_main.add_trace(go.Scatter(x=dates_area,
                                  y=y_area,
                                  fill='toself',
                                  line_color='LightGrey',
                                  fillcolor='LightGrey',
                                  opacity=0.2,
                                  hoverinfo='none',
                                  showlegend=False,
                                  )
                       )

    # REVENUE Lines

    revenue = np.array([entry['Revenue'] for entry in df_dataset_dict])*1_000_000
    # Find the indices where cells in the second array are not equal to "N/A"
    valid_indices = np.where(revenue != 0)
    print(date_picked_formatted_original, type(date_picked_formatted_original))

    years = 6
    current_date = datetime.now()
    print(current_date, type(current_date))
    future_arpu = [current_arpu * (1 + arpu_growth) ** year for year in range(years)]
    future_arpu_dates = [datetime.strptime(date_picked_formatted_original, '%Y-%m-%d') + timedelta(days=365 * year) for year in range(years)]
    print("ARPU future")
    print(future_arpu_dates)
    print(future_arpu)

    # Filter rows based on valid indices
    dates_revenue = dates_raw[valid_indices]
    users_revenue = users[valid_indices]
    dates_revenue_actual = main.get_earlier_dates(dates[valid_indices], history_value_formatted)
    #users_revenue_actual = main.get_earlier_dates(users_revenue, history_value_formatted)
    data_len_revenue_array = dates_raw[data_len:]
    data_len_revenue = len(data_len_revenue_array[data_len_revenue_array != 0])
    revenue = revenue[valid_indices]
    if len(revenue) > 0:
        annual_revenue_per_user = revenue*4/users_revenue
        x_revenue = dates_revenue
        y_revenue = annual_revenue_per_user
        formatted_y_values = [f"${y:.1f}" if y < 1000 else f"${y / 1e3:.2f} K" for y in y_revenue]
        # Past revenue outline to increase the contrast
        fig_main.add_trace(go.Scatter(
            name="Annual Revenue per User (arpu)",
            x=x_revenue,
            y=y_revenue,
            mode='lines',
            line=dict(color='White', width=2),
            opacity=0.8,
            showlegend=False,
            text=formatted_y_values,
            hovertemplate=hovertemplate_maingraph),
            secondary_y=True,
        )
        # Past revenue line
        fig_main.add_trace(go.Scatter(
            name="Annual Revenue per User (arpu)",
            x=x_revenue,
            y=y_revenue,
            mode='lines',
            line=dict(color='Red', width=1),
            showlegend=True,
            text=formatted_y_values,
            hovertemplate=hovertemplate_maingraph),
            secondary_y=True,
        )
        fig_main.add_trace(go.Scatter(
            name="Future Annual Revenue per User (arpu)",
            x=future_arpu_dates,
            y=future_arpu,
            mode='markers',
            marker=dict(color='#ff6666', size=4),
            showlegend=True,
            text=formatted_y_values,
            hovertemplate=hovertemplate_maingraph),
            secondary_y=True,
        )
        # Revenue past the selected date that are known [data_len:]
        fig_main.add_trace(go.Scatter(
            name="Annual Revenue per User (arpu)",
            x=x_revenue[len(dates_revenue_actual):],
            y=y_revenue[len(dates_revenue_actual):],
            mode='lines',
            line=dict(color='Gray', width=1),
            showlegend=False,
            text=formatted_y_values,
            hovertemplate=hovertemplate_maingraph),
            secondary_y=True,
        )
        fig_main.update_yaxes(range=[min(annual_revenue_per_user) * 0.9, max(annual_revenue_per_user) * 1.5],
                              title_text="Annual Revenue per User [$]",
                              color="#ff6666",
                              secondary_y=True)

    else:
        print("No revenue to be added to the graph")

    # fig_main.update_traces(hovertemplate="%{x|%b %Y}")
    # Calculate custom x-axis labels based on the numeric values
    # custom_x_labels = [f"{int(val):%B %Y}" for val in x_values]

    x1 = np.linspace(dates[-1] + 0.25, dates[-1] + 10, num=10)
    # Add predicted bars
    # fig_main.add_trace(go.Bar(name="Predicted S Curve", x=x1+1970, y=main.logisticfunction(k, r, p0, x1),
                         # marker_color='White', marker_line_color='Black'))

    # Build second chart containing the discrete growth rates & Regressions
    # -------------------------------------------------------
    '''
    fig_second = go.Figure(layout=layout_second_graph)
    fig_second.update_xaxes(range=[0, users[-1]*1.1])  # Fixing the size of the X axis with users max + 10%
    max_rd_value = df_sorted['r'].max()

    fig_second.update_yaxes(range=[0, max_rd_value]) # Fixing the size of the Y axis
    fig_second.add_trace(
        go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
                   y=main.discrete_growth_rate(users, dates+1970), mode="markers",line=dict(color='#54c4f4')))
    # Add trace of the regression
    fig_second.add_trace(
        go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
                   y=-r/k*main.discrete_user_interval(users)+r, mode="lines", line=dict(color='#54c4f4')))
    # Add trace of the regression obtained by fixing k
    fig_second.add_trace(
        go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
                   y=-r_log / k_log * main.discrete_user_interval(users) + r_log, mode="lines", line=dict(color='Purple')))
    # Changes the color of the scatters ignored
    # print(main.discrete_user_interval(users[0:number_ignored_data]))
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
                       
    # Add trace of the polynomial approximation
    #fig_second.add_trace(
        #go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
                   #y=np.polyval(polynum1, main.discrete_user_interval(users)), mode="lines", line=dict(color="Green")))
    #fig_second.add_trace(
    #    go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
    #               y=np.polyval(polynum2, main.discrete_user_interval(users)), mode="lines", line=dict(color="Blue")))
    #fig_second.add_trace(
    #    go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
    #               y=np.polyval(polynum3, main.discrete_user_interval(users)), mode="lines", line=dict(color="Red")))
    fig_second.add_trace(
        go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
                   y=np.polyval(logfit, np.log(main.discrete_user_interval(users))), mode="lines", line=dict(color="Orange")))
    
    '''

    # Build third chart containing the evolution of r^2 & rmsd linked to the # of data ignored
    # -------------------------------------------
    '''
    fig_third = make_subplots(specs=[[{"secondary_y": True}]])
    df_sorted_n_ignored = df_sorted.sort_values(by='Data Ignored')
    x_3_axis = df_sorted_n_ignored['Data Ignored']
    y_3_axis = df_sorted_n_ignored['R Squared']
    y_3_axis2 = df_sorted_n_ignored['RMSD']
    fig_third.add_trace(
        go.Scatter(name="R^2", x=x_3_axis,
                   y=y_3_axis, mode="markers", line=dict(color='#54c4f4')))
    fig_third.add_trace(
        go.Scatter(name="RMSD", x=x_3_axis,
                   y=y_3_axis2, mode="markers", line=dict(color='Green')), secondary_y=True)
    # Vertical line indicating what is the value shown in the main graph.
    fig_third.add_vline(x=number_ignored_data, line_width=3, line_dash="dot", opacity=0.25)
    '''


    # Carrying capacity to be printed
    k_printed = int(np.rint(k)/pow(10, 6))
    k_printed = "{:,} M".format(k_printed)
    # PLATEAU: Time when the plateau is reached, assuming the plateau is "reached" when p(t)=95%*K
    print(p0)
    if p0 > 2.192572e-11:
        t_plateau = main.time_to_population(k, r, p0, 0.95*k) + 1970
        month_plateau = math.ceil((t_plateau - int(t_plateau))*12)
        year_plateau = int(np.round(t_plateau, 0))
        date_plateau = datetime(year_plateau, month_plateau, 1).date()
        date_plateau_displayed = date_plateau.strftime("%b, %Y")
        t_plateau_displayed = 'Year {:.1f}'.format(t_plateau)
    else:
        date_plateau_displayed = "Plateau could not be calculated"
    print("2. CALLBACK END")
    t2 = time.perf_counter(), time.process_time()
    print(f" Creating graph")
    print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
    return fig_main, sections, False, graph_message

# Callback displaying the functionalities & graph cards, and hiding the text
@app.callback(
    Output(component_id="graph-card-content", component_property='style'),
    Output(component_id='functionalities-card', component_property='style'),
    Output(component_id='welcome-timeline', component_property='style'),
    Output(component_id='launch-counter', component_property='data'),
    Input(component_id='dataset-selection', component_property='value'),
    [State('launch-counter', 'data')]
    , prevent_initial_call=True
)
def show_cards(data, launch_counter):
    print("Displaying cards", launch_counter, type(launch_counter))
    if launch_counter['flag'] is not True:
        launch_counter['flag'] = True
        show_graph_card = {'display': 'block'}
        hide_graph_card = {'display': 'none'}
        print(launch_counter)
        return show_graph_card, show_graph_card, hide_graph_card, launch_counter

    else:
        print("Card already displayed", launch_counter)
        raise PreventUpdate



# Callback calculating the ARPU needed depending on the chosen scenario
@app.callback(
    Output(component_id="arpu-needed", component_property="children"),
    [
    Input(component_id='scenarios-sorted', component_property='data'),
    Input("range-profit-margin", "value"),
    Input("range-discount-rate", "value"),
    Input("range-slider-k", "value"),
    Input(component_id='current-market-cap', component_property='data'),
    Input(component_id='current-arpu-stored', component_property='data'),
    ], prevent_initial_call=True
)
def calculate_arpu(df_sorted, profit_margin, discount_rate, row_index, current_market_cap, current_arpu):
    # The entire callback is skipped if the current market cap = 0, i.e. if it is not a public company
    if current_market_cap == 0:
        raise PreventUpdate
    k_selected = df_sorted[row_index]['K']
    r_selected = df_sorted[row_index]['r']
    p0_selected = df_sorted[row_index]['p0']
    profit_margin = profit_margin/100
    discount_rate = discount_rate/100
    YEARS_DCF = 10
    current_market_cap = current_market_cap * 1000000
    # Ignored to avoid calculating this. Can be discommented to reuse this function
    #arpu_needed = main.arpu_for_valuation(k_selected, r_selected, p0_selected, profit_margin, discount_rate, YEARS_DCF, current_market_cap)
    arpu_needed = 0
    arpu_difference = arpu_needed/current_arpu
    printed_arpu = f"{arpu_needed:.0f} $. The current arpu " +f"({current_arpu:.0f} $)"+" should be multiplied by "+f"{arpu_difference:.2f}!" # formatting
    print("printed arpu", printed_arpu, type(printed_arpu))
    return printed_arpu

# Callback Adapting the Hype-meter
@app.callback(
    Output(component_id="hype-meter-noa", component_property="value"),
    Output(component_id="hype-tooltip-noa", component_property="children"),
    Output(component_id="hype-meter-users", component_property="value"),
    Output(component_id="hype-tooltip-users", component_property="children"),
    Output(component_id="hype-meter-hype", component_property="value"),
    Output(component_id="hype-tooltip-hype", component_property="children"),
    Output(component_id="hype-meter-indicator", component_property="color"),
    Output(component_id="hype-meter-indicator", component_property="children"),
    [
    Input(component_id='scenarios-sorted', component_property='data'),
    Input("range-profit-margin", "value"),
    Input("range-discount-rate", "value"),
    Input("range-slider-k", "value"),
    Input("range-arpu-growth", "value"),
    Input(component_id='current-market-cap', component_property='data'),
    Input(component_id='current-arpu-stored', component_property='data'),
    Input(component_id='total-assets', component_property='data'),
    Input(component_id='users-dates-formatted', component_property='data')
    ], prevent_initial_call=True
)
def calculate_arpu(df_sorted, profit_margin, discount_rate, row_index, arpu_growth, current_market_cap, current_arpu,
                   total_assets, df_dataset_dict):
    # The entire callback is skipped if the current market cap = 0, i.e. if it is not a public company
    if current_market_cap == 0:
        raise PreventUpdate
    # Parameters definition
    users = np.array([entry['Users'] for entry in df_dataset_dict]) * 1_000_000
    k_selected = df_sorted[row_index]['K']
    r_selected = df_sorted[row_index]['r']
    p0_selected = df_sorted[row_index]['p0']
    profit_margin = profit_margin/100
    discount_rate = discount_rate/100
    arpu_growth = arpu_growth / 100
    YEARS_DCF = 15
    current_market_cap = current_market_cap * 1000000

    print("K selected", k_selected)
    print("total asserts", total_assets)

    # Analysis to be deleted
    #current_customer_equity =

    # Equity calculation
    current_customer_equity = users[-1] * current_arpu * profit_margin
    future_customer_equity = main.net_present_value_arpu_growth(k_selected, r_selected, p0_selected, current_arpu,
                                                                arpu_growth, profit_margin, discount_rate, YEARS_DCF)
    total_customer_equity = current_customer_equity + future_customer_equity

    non_operating_assets = total_assets
    hype_total = current_market_cap - total_customer_equity - non_operating_assets

    # Calculating the values of the hype meter
    non_operating_assets_ratio = non_operating_assets / current_market_cap *100
    noa_tooltip = f"Non-Operating Assets: ${total_assets/1e9:.2f} B. \n They represent additional valuable company " \
                  f"assets, such as Goodwill"
    customer_equity_ratio = total_customer_equity / current_market_cap * 100
    print("CE ratio for hype meter", customer_equity_ratio)
    customer_equity_tooltip = f"Customer Equity: ${total_customer_equity / 1e9:.2f} B.   It represents current and " \
                              f"future customer-generated profit, calculated with the selected parameters with a " \
                              f"discounted cashflow method"
    hype_ratio = hype_total / current_market_cap * 100
    print("NOA Ratio", non_operating_assets_ratio, "CE ratio", customer_equity_ratio, "Hype ratio", hype_ratio)
    if hype_total < 0.0:
        hype_ratio = 0.0
    hype_tooltip = f"Hype: ${hype_total / 1e9:.2f} B.  It reflects the current overvaluation of the company in terms " \
                   f"of market capitalization versus actual value."

    hype_indicator_color, hype_indicator_text = main.hype_meter_indicator_values(hype_ratio/100)

    # Calculation of the ARPU needed for a given market cap, margin & growth rate
    #arpu_needed = main.arpu_for_valuation(k_selected, r_selected, p0_selected, profit_margin,discount_rate, YEARS_DCF, current_market_cap)
    #arpu_difference = arpu_needed/current_arpu
    #printed_arpu = f"{arpu_needed:.0f} $. The current arpu " +f"({current_arpu:.0f} $)"+" should be multiplied by "+f"{arpu_difference:.2f}!" # formatting

    return non_operating_assets_ratio, noa_tooltip, customer_equity_ratio, customer_equity_tooltip, hype_ratio, \
        hype_tooltip, hype_indicator_color, hype_indicator_text

@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open




if __name__ == '__main__':
    app.run_server(debug=True)