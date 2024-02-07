# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import dash
import dash_mantine_components as dmc
from dash import Dash, html, dcc, register_page
from dash import callback
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dataAPI
import main
import dash_bootstrap_components as dbc
# import datetime
from datetime import datetime, timedelta, date
import math
from plotly.subplots import make_subplots
from dash_iconify import DashIconify
import time
from dash.exceptions import PreventUpdate

pd.set_option('display.max_columns', None)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
APP_TITLE = "RAST"

# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.LUX],
                title=APP_TITLE,
                use_pages=True,
                )

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-DE44VVN8LR"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', 'G-DE44VVN8LR');
        </script>
        <meta name="RAST | Customer-based companies valuation" content="RAST is a tool for valuating customer-based or
        user-based publicly traded companies">
        <title>RAST</title>
        <link rel="icon" href="/assets/favicon.ico">
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>

    </body>
</html>"""

# ---------------------------------------------------------------------------

# Values for the dropdown (all different companies in the DB)
labels = dataAPI.get_airtable_labels_new()

# Constants for the calculation
YEAR_OFFSET = 1970  # The year "zero" for all the calculations
MIN_DATE_INDEX = 5  # Defines the minimum year below which no date can be picked in the datepicker
YEARS_DCF = 15  # Amount of years taken into account for DCF calculation

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
# company_test = "testtest"
# labels_new.append({"value": company_test, "label": f" {company_test}", "disabled": True})

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

# Hype meter indicator
hype_meter_indicator_progress = dbc.Progress(
    children=
    [
        dbc.Progress(value=5, color="#D3F9D8", bar=True, id="marginally-hyped"),
        dbc.Progress(value=5, color="#FFF3BF", bar=True, id="moderately-hyped"),
        dbc.Progress(value=5, color="#FFE8CC", bar=True, id="strongly-hyped"),
        dbc.Progress(value=85, color="#C92A2A", bar=True, animated=True, striped=True, id="super-hyped"),
        dbc.Tooltip("Customer Equity: $3.0B", target="marginally-hyped", placement="top"),
        dbc.Tooltip("Delta depending on the chosen scenario", target="moderately-hyped", placement="top"),
        dbc.Tooltip("Hype: $4.0B", target="strongly-hyped", placement="top"),
        dbc.Tooltip("Super Hyped", target="super-hyped", placement="top"),
    ],
    style={"height": "5px", "border-radius": "0px"},
)
reset_parameters_button = dmc.Button(
    id="reset-parameters",
    children="Reset Parameters to Default",
    leftIcon=DashIconify(icon="fluent:arrow-reset-24-filled"),
    size="xs",
    variant="outline",
    disabled="True",
),

# Hype meter
hype_meter_bootstrap = dbc.Progress(
    children=
    [
        dbc.Progress(value=10, color="#228BE6", bar=True, label="N-O Assets", id="hype-meter-noa"),
        dbc.Progress(value=10, color="#74C0FC", bar=True, label="Customer Equity", id="hype-meter-users"),
        # dbc.Progress(value=20, color="#D1D1D1", bar=True, animated=True, striped=True, id="hype-meter-delta"),
        dbc.Progress(value=10, color="#D1D1D1", bar=True, animated=True, striped=True, label="Hype",
                     id="hype-meter-hype"),
        dbc.Tooltip("Non-Operating Assets: $3.0B", target="hype-meter-noa", id='hype-tooltip-noa', placement="top"),
        dbc.Tooltip("Customer Equity: $3.0B", target="hype-meter-users", id='hype-tooltip-users', placement="top"),
        # dbc.Tooltip("Delta depending on the chosen scenario", target="hype-meter-delta", id="tooltip-equity-text", placement="top"),
        dbc.Tooltip("Hype: $4.0B", target="hype-meter-hype", id='hype-tooltip-hype', placement="top"),
    ],
    style={"height": "30px", "border-radius": "30px"},
)

hype_meter_example = dbc.Progress(
    children=
    [
        dbc.Progress(value=30, color="#228BE6", bar=True, label="N-O Assets", id="hype-meter-noa-ex"),
        dbc.Progress(value=40, color="#74C0FC", bar=True, label="Customer Equity", id="hype-meter-users-ex"),
        dbc.Progress(value=30, color="#D1D1D1", bar=True, animated=True, striped=True, label="Hype",
                     id="hype-meter-hype-ex"),
        dbc.Tooltip("Non-Operating Assets: $3.0B", target="hype-meter-noa-ex", placement="top"),
        dbc.Tooltip("Customer Equity: $3.0B", target="hype-meter-users-ex", placement="top"),
        # dbc.Tooltip("Delta depending on the chosen scenario", target="hype-meter-delta", id="tooltip-equity-text", placement="top"),
        dbc.Tooltip("Hype: $4.0B", target="hype-meter-hype-ex", placement="top"),
    ],
    style={"height": "30px", "border-radius": "30px"},
)
offcanvas_card_growth_analysis = dmc.Card(
    children=[
        dmc.Group(
            [
                dmc.Title("GROWTH", order=6),
                dmc.Text("For all datasets", size="xs", color="dimmed")
            ],
            position="apart",
            mt="md",
            # mb="xs",
        ),
        dmc.Space(h=20),
        dmc.Text(
            # id="hype-meter-text",
            children=[dmc.List([
                dmc.ListItem([dmc.Text("Dataset Selection", weight=500),
                              "Quickly choose your dataset from the dropdown menu. We are continuously adding new "
                              "datasets."]),
                dmc.ListItem([dmc.Text("Historical Data Visualization", weight=500),
                              "Dive into your selected dataset's past performance, unveiling growth trends "
                              "over time."]),
                dmc.ListItem([dmc.Text("Predictive Analysis", weight=500),
                              "Harness RAST's advanced predictive capabilities to forecast future dataset "
                              "growth."]),
            ], size="sm", listStyleType="decimal")]
            ,
            size="xs",
            color="Black",
            # style={'display':'inline-block'}
        ),
    ],
    # id="hype-meter-card",
    # style={'display': 'none'},
    withBorder=True,
    shadow="sm",
    radius="md",
)

offcanvas_card_valuation_analysis = dmc.Card(
    children=[
        dmc.Group(
            [
                dmc.Title("COMPANY VALUATION", order=6),
            ],
            position="apart",
            mt="md",
            # mb="xs",
        ),
        dmc.Space(h=20),
        dmc.Text("Methodology", size="sm", weight=700),
        dmc.Space(h=5),
        dmc.Text("In user-dependent companies, their value is tied to the number of users and the revenue each "
                 "user generates. The total worth, known as 'Customer Equity', combines current and future "
                 "value. To calculate the overall company value, add non-operating assets and subtract debt: "
                 , size="sm"),
        dmc.Text("Company Value = Non-Operating Assets + Customer Equity - Debt", align="center", size="sm",
                 weight=500),
        dmc.Text("Comparing this value to the "
                 "market cap reveals investor sentiments, showing how much 'hope' or 'hype' surrounds "
                 "the company. In the example below, we observe that the hype accounts for 30% of the company's "
                 "current valuation. This suggests that unless there's a notable enhancement in its business "
                 "model, there's a high likelihood that the value may decrease."
                 , size="sm"),
        dmc.Space(h=10),
        hype_meter_example,
        dmc.Space(h=15),
        dmc.Text("Functionalities", size="sm", weight=700),
        dmc.Space(h=5),
        dmc.Text(children=[
            dmc.List([
                dmc.ListItem([dmc.Text("Hypemeter", weight=500),
                              "Get a quick read on a company's hype level. A company is considered Super Hyped when "
                              "the hype exceeds 20% of the total value.", dmc.Group(children =[
                           dmc.Badge("", variant="outline", color="green"),  dmc.Badge("", variant="outline", color="yellow"), dmc.Badge("", variant="outline", color="orange"),
                           dmc.Badge("Super Hyped!", variant="filled", color="red")], spacing=2)]),
                dmc.ListItem([dmc.Text("Growth Forecast", weight=500),
                              "Slide through different growth scenarios, correlating stronger growth with higher "
                              "future value and current valuation."]),
                dmc.ListItem([dmc.Text("Profit Margin", weight=500),
                              "Evaluate a company's value by considering its profit margin. A positive margin "
                              "indicates revenue generation, and the higher the margin, the higher the current value."]),
                dmc.ListItem([dmc.Text("Discount Rate", weight=500),
                              "Factor in future uncertainties with the discount rate. The higher the rate, "
                              "the more uncertainty about the future, leading to a lower current valuation."]),
                dmc.ListItem([dmc.Text("Revenue (ARPU) per year", weight=500),
                              "Assess customer equity by changing the annual average revenue generated per user "
                              "(ARPU). "
                              "For example, Netflix users contribute around $130 per year based on their annual "
                              "subscription value."]),
            ], size="sm", listStyleType="decimal")],
            size="xs",
            color="Black",
        ),
    ],
    # style={'display':'inline-block'}
    # id="hype-meter-card",
    # style={'display': 'none'},
    withBorder=True,
    shadow="sm",
    radius="md",
)

# OffCanvas (side panel that opens to give more information)
offcanvas = html.Div(
    [
        dbc.Button("How it works?", id="open-offcanvas", n_clicks=0),
        dbc.Offcanvas([
            dmc.Container(children=[
                dmc.Text(
                    "Are you a Tech investor, journalist or simply curious about tech valuation? We got you."
                    " Meet RAST, your go-to tool for determining the intrinsic"
                    "value of publicly traded Tech companies.", size="sm"),
                dmc.Space(h=15),
                offcanvas_card_growth_analysis,
                dmc.Space(h=15),
                offcanvas_card_valuation_analysis,
                dmc.Space(h=15),
                dmc.Text(
                    "We're continually adding new datasets & functionalities. Interested in specific datasets or have "
                    "a feature request? Drop us a line! 🚀 rastapp@proton.me.", size="sm"),
                # dmc.Group(hype_meter_indicator_progress),
            ]
            ),
        ],
            id="offcanvas",
            title="Welcome to RAST",
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
                          dbc.NavbarBrand("RAST", style={'margin-left': '10px'})
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
                                    dbc.NavbarBrand("RAST", style={'margin-left': '20px'}),
                                    # dropdown5,
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
        dbc.NavItem(dbc.NavbarBrand("RAST", style={'margin-left': '20px'})),
        # dropdown4,
        # dbc.NavItem(dropdown5),
        dbc.NavItem(offcanvas, style={'height': '20px'}),
    ], fill=True
),

    color="primary",
    dark=True)

app_button = dmc.Button(
    id="app-button",
    children="APP",
    leftIcon=DashIconify(icon="fluent:app-title-24-regular"),
    size="xs",
    variant="gradient",
    gradient={"from": "cyan", "to": "blue"},
    # color="white",
    # color.title(white).
),

navbar6 = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row([
                dbc.Col(html.Img(src="/assets/Vector_white.svg", height="25px")),
                dbc.Col(dbc.NavbarBrand("RAST", className="ms-2", href='/'))
            ],
                align="bottom",
                className="g-0"),
            dbc.Row([
                dbc.Col([
                    dbc.Nav([
                        dbc.NavItem(app_button),
                    ],
                        navbar=True
                    )
                ],
                    width={"size": "auto"})
            ],
                align="right"),
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

navbar7 = dbc.NavbarSimple(
    children=[
        dbc.NavItem(
            dbc.NavLink(
                [
                    "App"  # Text beside icon
                ],
                href="/app",
                # target="_blank"
            )

        ),
        offcanvas,
        # dbc.DropdownMenu(
        #    nav=True,
        #    in_navbar=True,
        #    label="Menu",
        #    align_end=True,
        #    children=[  # Add as many menu items as you need
        #        dbc.DropdownMenuItem("Home", href='/'),
        #        dbc.DropdownMenuItem(divider=True),
        #        dbc.DropdownMenuItem("Page 2", href='/page2'),
        #       dbc.DropdownMenuItem("Page 3", href='/page3'),
        #     ],
        # ),
    ],
    #brand=['R A ', html.Img(src="/assets/favicon.ico", height="21px"), ' T'],
    brand=[html.Img(src="/assets/Vector_White_Full.svg", height="21px")],
    brand_href="/",
    sticky="top",  # Uncomment if you want the navbar to always appear at the top on scroll.
    color="primary",  # Change this to change color of the navbar e.g. "primary", "secondary" etc.
    dark=True,  # Change this to change color of text within the navbar (False for dark text)
)

# Sliders
slider = html.Div(children=[dcc.RangeSlider(id="range-slider-data-ignored1", min=0, step=1,
                                            marks={},
                                            value=[0],
                                            tooltip={"placement": "bottom", "always_visible": True},
                                            vertical=True),
                            html.Div(id="max-label")])

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
    max=60,
    marks=[
        {"value": 2, "label": "2%"},
        {"value": 10, "label": "10%"},
        {"value": 20, "label": "20%"},
        {"value": 50, "label": "50%"}
    ],
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
    color='green',
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
            # minDate=date(2020, 8, 5),
            # inputFormat="MMMM,YY",
            dropdownType="popover",
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
    id="accordion-main",
    # value=["growth"],
    # variant="separated",
    radius="xl",
    children=[
        dmc.AccordionItem(
            [
                dmc.AccordionControl(
                    "Growth",
                    id="accordion-growth",
                    disabled=True,
                    icon=DashIconify(icon="uit:chart-growth", color=dmc.theme.DEFAULT_COLORS["blue"][6], width=20),
                    #c="red",
                    #style={'item': {'color': 'red'}},
                ),
                dmc.AccordionPanel(
                    growth_message
                ),
            ],
            value="growth",
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
            value="plateau",
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
            value="valuation",
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
            value="correlation",
        ),
    ],
)

# Graph message
graph_message = dmc.Alert(
    dmc.Text("About the graph"),
    id="graph-message",
    title="About the Growth Forecast",
    color="blue",
    # hide="False",
    withCloseButton="True")

# Graph message
valuation_graph_message = dmc.Alert(
    dmc.Text("About the Current Market Cap"),
    id="valuation-graph-message",
    title="About the Current Market Cap",
    color="blue",
    # hide="False",
    withCloseButton="True")

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
                dmc.Title("Browse", order=5),
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
                dmc.Title("Parameters", order=5),
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
                        "Growth Forecast",
                        size="sm",
                        weight=700,
                    ),
                    dmc.Tooltip(
                        DashIconify(icon="feather:info", width=15),
                        label="Select 'Custom' to move the blue curve and see how well it fits the dataset. "
                              "The star indicates RAST's best prediction",
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
        html.Div(slider_k, style={"marginLeft": 15, "marginRight": 15}),
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
                            label="Adjust the yearly growth of the Average Revenue Per User for the next years. This"
                                  " changes the projected ARPU and therefore the value of future users",
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
                    ], ),
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
    # style={"height": 500},
)

# Welcome timeline introducing the user to RAST

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
                # lineVariant="dashed",
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
                            "For publicly traded user-based companies, assess whether their current valuation is justified"
                            " or strongly 'hyped'",
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
                            "We are continuously adding new datasets and metrics. "
                            "Have new datasets or feature requests? Contact us",
                            dmc.Anchor(
                                " here!",
                                href="mailto:rastapp@proton.me",
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

main_graph = dcc.Graph(id='main-graph1', config={'displayModeBar': False, 'scrollZoom': True})

# Graph that contains the valuation calculation over time
valuation_over_time = html.Div(children=[dcc.Graph(id='valuation-graph', config={'displayModeBar': False,
                                                                                 'scrollZoom': True})])

# Tabs
tabs_graph = dmc.Tabs(
    [
        dmc.TabsList(
            # grow=True,
            children=
            [
                dmc.Tab("Future Outlook", icon=DashIconify(icon="simple-icons:futurelearn"), value="1"),
                dmc.Tab("Past Performance",
                        icon=DashIconify(icon="material-symbols:history"),
                        value="2",
                        # disabled=True
                        ),
            ],
        ),
        dmc.TabsPanel(html.Div(children=[graph_message, main_graph]),
                      id="tab-one", value="1"),
        dmc.TabsPanel(html.Div(children=[valuation_graph_message, valuation_over_time]), id="tab-two", value="2"),
    ],
    value="1",
    variant="outline",
    # id='graph-card-content',
    # style={'display': 'none'}
)

source = dmc.Text(
    id="data-source",
    children="Source",
    size="xs",
    color="dimmed", )

graph_card = dmc.Card(
    children=[
        # Card Title
        dmc.Group(
            [
                dmc.Title("Welcome to RAST", id="graph-title", order=5),
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
            dmc.Space(h=10),
            # html.Div(graph_message),
            dmc.Space(h=10),
            html.Div(tabs_graph),
            dmc.Space(h=10),
            html.Div(source),
            # html.Div(graph_message),
            # Card Content
            # html.Div(main_graph),
        ],
            id='graph-card-content',
            style={'display': 'none'}
        )
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
)

hype_meter = dmc.Progress(
    size=40,
    radius="xl",
    styles={"label": {"font-size": "15px", "font-weight": 600}},
    # striped=True,
    # animate=True,
    sections=[
        {"value": 50, "color": "#74C0FC", "label": "Users value", "tooltip": "Users value - $5.0B"},
        {"value": 6, "color": "Gray", "tooltip": "Users value delta - $0.6B"},
        {"value": 11, "color": "#228BE6", "label": "NO Assets", "tooltip": "Non-Operating Assets - $1.1B",
         "animate": True, "striped": True},
    ],
)
data = [
    {"value": "Low", "label": "React", "color": "red"},
    {"value": "Medium", "label": "Angular"},
    {"value": "High", "label": "Svelte"},
    {"value": "Huge", "label": "Vue"},
]
hype_meter_indicator = dmc.Badge("Super hyped", variant="outline", color="red", id="hype-meter-indicator")

hype_meter_card = dmc.Card(
    children=[
        dmc.Group(
            [
                dmc.Title("Hype Meter", order=5),
                hype_meter_indicator,
            ],
            position="apart",
            mt="md",
            mb="xs",
        ),
        # hype_meter,
        dmc.Stack([
            dmc.Text("Market Cap: $10.1B", size="xs", weight=500, align="center", id="hype-market-cap"),
            hype_meter_bootstrap,
        ],
            align="stretch"
        ),
        dmc.Space(h=20),
        dmc.Text(
            id="hype-meter-text",
            children=[
                "Adjust profit margin, discount rate, and ARPU to evaluate the company's current hype through its "
                "three components: Non-Operating Assets, Customer Equity, and Hype.",
                # dmc.Text("Non-Operating Assets represent additional valuable company assets.", color="#228BE6"),
                # dmc.Text("Customer Equity signifies current and future customer-generated profit,"
                #         " calculated with the selected parameters with a discounted cashflow "
                #         "method", color="#74C0FC"),
                # dmc.Text("Hype reflects the current overvaluation of the company in terms of market "
                #         "capitalization versus actual value.", color="dimmed"),
                ]
            ,
            size="xs",
            color="Black",
            style={'display': 'inline-block'}
        ),
        dmc.Space(h=10),
        dmc.Center(reset_parameters_button),
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
        l=0,  # left margin
        r=0,  # right margin
        b=0,  # bottom margin
        t=20,  # top margin
    ),
    legend=dict(
        # Adjust click behavior
        itemclick="toggleothers",
        itemdoubleclick="toggle",
        # orientation="h",
        # x=0.5,
        # y=-0.1,
        yanchor="top",
        y=0.96,
        xanchor="left",
        x=0.01,
        font=dict(
            # family="Courier",
            size=10,
            # color="black"
        ),
    ),
    xaxis=dict(
        # title="Timeline",
        linecolor="Grey",
        # hoverformat=".0f",
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
        # size=16,
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
        # size=16,
        # color="Black"
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
        # size=16,
        # color="Black"
    ),
)

main_plot.update(
    layout=layout_main_graph
)

# loading = dcc.Loading(id="loading-component", children=[html.Div([html.Div(id="loading-output")])], type="circle",),

# ----------------------------------------------------------------------------------
# App Layout
app.layout = html.Div(style={'backgroundColor': '#F9F9F9'}, children=
[
    # navbar6,
    navbar7,
    dmc.Space(mb=20),  # Margin/space between the navbar and the content
    # Mantine Grid

    dmc.Container(fluid=True, children=[
        dmc.Grid([
            # dmc.Col(span=0.5, lg=0), # Empty left column
            # dmc.Col(selector_card, span="auto", order=1),
            dmc.Col([
                dmc.LoadingOverlay(
                    # graph_card
                ),
                # valuation_over_time_card  # Comment this line to remove the analysis graphs
            ], span=12, lg=6, orderXs=3, orderSm=3, orderLg=2),
            # dmc.Col([hype_meter_card, dmc.Space(h=20), functionalities_card], span=12, lg=3, orderXs=2, orderSm=2, orderLg=3),
            # dmc.Col(span="auto", lg=0), # Empty right column
        ],
            gutter="xl",
            justify="space-around",
            # align="center",
        ),
    ]),
    dash.page_container
])

server = app.server


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
    Output("loader-general", "style"),

    Input("dataset-selection", "value")
], prevent_initial_call=True)
def select_value(value):
    title = value
    subtitle = "Explore " + str(
        value) + "'s Future Outlook to assess its current valuation and explore RAST's past valuations. Customize " \
                 "Predictions with the Slider in the 'Functionalities' Section and Adjust " \
                 "the Forecast Start Date Using the Datepicker. Use the 'Past performance' section " \
                 "to see RAST's calculated hype over time."
    show_loader = {'display': 'block'}
    return False, False, False, False, show_loader


# Callback defining the minimum and the maximum date of the datepicker and loading the dataset
@app.callback([
    Output(component_id='date-picker', component_property='minDate'),  # Calculate the min of the new history slider
    Output(component_id='date-picker', component_property='maxDate'),  # Calculate the min of the new history slider
    Output(component_id='date-picker', component_property='value'),
    # Resets the date to the last available date of the dataset
    Output(component_id='users-dates-raw', component_property='data'),  # Stores the users + dates data
    Output(component_id='users-dates-formatted', component_property='data'),
    # Stores the users + dates formatted for computation
    Output(component_id='graph-unit', component_property='data'),  # Stores the graph unit (y axis legend)
    # Output(component_id='main-graph0', component_property='figure'), # Stores the users + dates formatted for computation
    Output("graph-title", "children"),
    Output("graph-subtitle", "children"),
    # Output(component_id='main-plot-container', component_property='figure'), # Stores the users + dates formatted for computation
    Output(component_id='profit-margin', component_property='style'),  # Show/hide depending on company or not
    Output(component_id='discount-rate', component_property='style'),  # Show/hide depending on company or not
    # Output(component_id='arpu-card', component_property='style'),  # Show/hide depending on company or not
    Output(component_id='hype-meter-card', component_property='style'),  # Show/hide depending on company or not
    Output(component_id='arpu-growth', component_property='style'),  # Show/hide depending on company or not
    Output(component_id='profit-margin-container', component_property='children'),
    Output(component_id='best-profit-margin-container', component_property='children'),
    # Change the text below the profit margin slider
    Output(component_id='range-profit-margin', component_property='marks'),
    # Adds a mark to the slider if the profit margin > 0
    Output(component_id='range-profit-margin', component_property='value'),
    # Sets the value to the current profit margin
    Output(component_id='total-assets', component_property='data'),  # Stores the current arpu
    Output(component_id='users-revenue-correlation', component_property='data'),  # Stores the correlation between
    Output(component_id='range-discount-rate', component_property='value'),
    Output(component_id='initial-sliders-values', component_property='data'),  # Stores the default slider values
    Output(component_id='data-source', component_property='children'),  # Stores the source of the data shown
    Output(component_id='data-selection-counter', component_property='data'),  # Flags that the data has changed

    # the chosen KPI and the revenue

    Input(component_id='dataset-selection', component_property='value')],  # Take dropdown value
    # [State('main-plot-container', 'figure')],
    prevent_initial_call=True,
)
def set_history_size(dropdown_value):
    t1 = time.perf_counter(), time.process_time()
    try:
        # Fetch dataset from API
        df = dataAPI.get_airtable_data(dropdown_value)
        key_unit = df.loc[0, 'Unit']
        data_source = df.loc[0, 'Source']
        print("DF", df)

        # Creating the title & subtitle for the graph
        title = dropdown_value + " - " + key_unit
        subtitle = "Explore " + str(dropdown_value) + "'s Historical " + key_unit + " Data (Bars) and Future Growth " \
                                                                                    "Projections. Customize " \
                                                                                    "Predictions with the Slider in the 'Functionalities' Section and Adjust " \
                                                                                    "the Forecast Start Date Using the Datepicker."

        # Creating the source string for the graph
        if data_source == "Financial Report":
            source_string = "Source: " + dropdown_value + " Quarterly " + str(data_source)
        else:
            source_string = "Source: " + str(data_source)

        # Transforming it to a dictionary to be stored
        users_dates_dict = df.to_dict(orient='records')
        print("USERDATESDICT", users_dates_dict)

        # Process & format df. The dates in a panda serie of format YYYY-MM-DD are transformed to a decimal yearly array
        dates = np.array(main.date_formatting(df["Date"]))
        dates_formatted = dates + YEAR_OFFSET
        dates_unformatted = np.array(df["Date"])
        users_formatted = np.array(df["Users"]).astype(float) * 1000000

        # Logic to be used when implementing changing the ARPU depending on the date picked
        # date_last_quarter = main.previous_quarter_calculation().strftime("%Y-%m-%d")
        # closest_index = main.find_closest_date(date_last_quarter,dates_unformatted)

        # Check whether it is a public company: Market cap fetching & displaying profit margin,
        # discount rate and arpu for Companies
        symbol_company = df.loc[0, 'Symbol']
        if symbol_company != "N/A":
            show_company_functionalities = {'display': 'block'}  # Style component showing the fin. function.
            try:
                yearly_revenue, total_assets = dataAPI.get_previous_quarter_revenue(symbol_company)  # Getting with API
                print("Latest yearly revenue & total assets fetched")
            except Exception as e:
                print("Error fetching revenue & total assets, standard value assigned")
                total_assets = 1000
            filtered_revenue_df = df[df["Revenue"] != 0]  # Getting rid of the revenue != 0
            quarterly_revenue = np.array(filtered_revenue_df["Revenue"]) * 1_000_000  # Getting in database
            # Regression between Users and revenue
            users_revenue_regression = main.linear_regression(users_formatted[-len(quarterly_revenue):],
                                                              quarterly_revenue)

            # Profit margin text and marks
            profit_margin_array = np.array(df["Profit Margin"])

            current_annual_profit_margin = profit_margin_array[-1]
            max_annual_profit_margin = max(profit_margin_array)
            text_best_profit_margin = "Best recorded profit margin ever: " + str(max_annual_profit_margin) + "%",
            if current_annual_profit_margin > 1:
                value_profit_margin_slider = float(current_annual_profit_margin)
                marks_profit_margin_slider = [
                    {"value": 2, "label": "2%"},
                    {"value": 10, "label": "10%"},
                    {"value": 20, "label": "20%"},
                    {"value": 50, "label": "50%"},
                ]
                text_profit_margin = "Latest annual profit margin: " + str(current_annual_profit_margin) + "% 🤩",

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
            total_assets = 0
            show_company_functionalities = {'display': 'none'}
            users_revenue_regression = 0
            text_profit_margin = ""
            value_profit_margin_slider = 5.0
            marks_profit_margin_slider = [
                {"value": 2, "label": "2%"},
                {"value": 10, "label": "10%"},
                {"value": 20, "label": "20%"},
                {"value": 50, "label": "50%"},
            ]

        df_formatted = df
        df_formatted["Date"] = dates_formatted

        # Final DF containing dates, users, Units, Symbols & Quarterly revenue
        users_dates_formatted_dict = df_formatted.to_dict(orient='records')

        min_history_datepicker = str(dates_unformatted[MIN_DATE_INDEX])  # Minimum date that can be picked
        max_dataset_date = datetime.strptime(dates_unformatted[-1], "%Y-%m-%d")  # Fetching the last date of the dataset
        max_history_datepicker_date = max_dataset_date + timedelta(
            days=6)  # Adding one day to the max, to include all dates
        #max_history_datepicker = max_history_datepicker_date.strftime("%Y-%m-%d")
        current_date = datetime.now()
        max_history_datepicker = current_date.date()
        date_value_datepicker = max_history_datepicker  # Sets the value of the datepicker as the max date
        # current_date = dates_formatted[-1]
        print("Other data", min_history_datepicker, max_dataset_date, max_history_datepicker_date,
              max_history_datepicker, date_value_datepicker)

        # Discount Rate
        value_discount_rate_slider = 5

        # Graph creation
        # fig_main = go.Figure(layout=layout_main_graph)
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
        # Initial_sliders_values
        initial_sliders_values = {'slider_profit_margin': value_profit_margin_slider,
                                  'slider_discount_rate': value_discount_rate_slider}

        t2 = time.perf_counter(), time.process_time()
        print(f" Calculation of the different sliders")
        print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
        print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
        return min_history_datepicker, max_history_datepicker, date_value_datepicker, users_dates_dict, \
            users_dates_formatted_dict, y_legend_title, title, subtitle, \
            show_company_functionalities, show_company_functionalities, show_company_functionalities, \
            show_company_functionalities, text_profit_margin, text_best_profit_margin, marks_profit_margin_slider, \
            value_profit_margin_slider, total_assets, users_revenue_regression, value_discount_rate_slider, \
            initial_sliders_values, source_string, True
    except Exception as e:
        print(f"Error fetching or processing dataset: {str(e)}")
        return "", "", "", "", "", "", "", "", "",


@app.callback(
    # Output("loading-component", "loading"),
    Output(component_id='range-slider-k', component_property='value'),  # Reset slider value to the best value
    Output(component_id='initial-sliders-values', component_property='data', allow_duplicate=True),
    Output(component_id="growth-message", component_property="title"),
    Output(component_id="growth-message", component_property="children"),
    Output(component_id="growth-message", component_property="color"),
    Output(component_id="accordion-growth", component_property="icon"),
    Output(component_id="accordion-main", component_property="value"),
    Output(component_id="plateau-message", component_property="title"),
    Output(component_id="plateau-message", component_property="children"),
    Output(component_id="plateau-message", component_property="color"),
    Output(component_id="accordion-plateau", component_property="icon"),
    Output(component_id="valuation-message", component_property="title"),
    Output(component_id="valuation-message", component_property="children"),
    Output(component_id="valuation-message", component_property="color"),
    Output(component_id="accordion-valuation", component_property="icon"),
    Output(component_id="correlation-message", component_property="title"),
    Output(component_id="correlation-message", component_property="children"),
    Output(component_id="correlation-message", component_property="color"),
    Output(component_id="accordion-correlation", component_property="icon"),
    Output(component_id='scenarios-sorted', component_property='data'),
    Output(component_id='range-slider-k', component_property='max'),
    Output(component_id='range-slider-k', component_property='marks'),
    Output(component_id='current-arpu-stored', component_property='data'),  # Stores the current arpu
    Output(component_id='hype-market-cap', component_property='children'),  # Stores the current arpu
    Output(component_id='current-market-cap', component_property='data'),  # Stores the company market cap
    Output(component_id='latest-market-cap', component_property='data'),  # Stores the current (now) company market cap
    Output(component_id='range-arpu-growth', component_property='value'),  # Stores the current (now) company market cap
    Output(component_id='growth-rate-graph-message', component_property='children'),
    Output(component_id='growth-rate-graph-message', component_property='color'),

    Input(component_id='dataset-selection', component_property='value'),  # Take dropdown value
    Input(component_id='date-picker', component_property='value'),  # Take date-picker date
    Input("scenarios-picker", "value"),  # Input the scenario to reset the position of the slider to the best scenario
    Input(component_id='users-dates-formatted', component_property='data'),
    Input(component_id='users-revenue-correlation', component_property='data'),
    Input(component_id='graph-unit', component_property='data'),  # Getting the Unit used
    Input(component_id='users-dates-raw', component_property='data'),
    Input(component_id='initial-sliders-values', component_property='data'),
    prevent_initial_call=True)
# Analysis to load the different scenarios (low & high) when a dropdown value is selected
def load_data(dropdown_value, date_picked, scenario_value, df_dataset_dict,
              users_revenue_correlation, key_unit, df_raw, initial_slider_values):
    print("Starting scenarios calculation")
    t1 = time.perf_counter(), time.process_time()
    date_picked_formatted = main.date_formatting_from_string(date_picked)
    df_dataset = pd.DataFrame(df_dataset_dict)
    print("DF_dataset_first", df_dataset)
    # Dates array definition from dictionary
    dates_raw = np.array([entry['Date'] for entry in df_raw])
    dates_new = np.array([entry['Date'] for entry in df_dataset_dict])
    dates = dates_new - 1970
    data_len = len(main.get_earlier_dates(dates, date_picked_formatted - 1970))
    print(data_len)
    print("Data_len")
    print(len(dates_new), dates_new)
    print(dates_new[0:data_len+1])
    print(dates_new[0:data_len])
    # Users are taken from the database and multiply by a million
    users_new = np.array([entry['Users'] for entry in df_dataset_dict])
    users_original = users_new.astype(float) * 1000000
    # print(df)

    # Test to be deleted, changing dates & users to use moving average
    #dates, users = main.moving_average_smoothing(dates, users_original, 1)
    users = users_original
    # Resizing of the dataset taking into account the date picked
    history_value_formatted = date_picked_formatted - 1970  # New slider: Puts back the historical value to the format for computations
    dates_actual = main.get_earlier_dates(dates, history_value_formatted)
    closest_index = data_len - 1  # Index of the last data matching the date selected
    current_users_array = users_new * 1e6
    current_users = current_users_array[closest_index]

    # All parameters are calculated by ignoring data 1 by 1, taking the history reference as the end point
    df_full = main.parameters_dataframe(dates[0:data_len],
                                        users[0:data_len])  # Dataframe containing all parameters with all data ignored
    print("df_full", df_full)
    df_sorted = main.parameters_dataframe_cleaning(df_full, users[
                                                            0:data_len])  # Dataframe where inadequate scenarios are eliminated
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
    # Growth: for the best growth scenario (highest R^2),
    #   First rule:
    #           if the difference between the log R^2 and the linear R^2
    #           is <0.1, then that means the growth is stabilizing and a classical logistic growth is to be expeced
    #           if it is > 0.1 then it means that the dataset is still in its exponential growth and the probability
    #           for exponential growth is high
    #   Second rule:
    #           if either K or r are < 0 in the last 4 iterations, that means that there is a potential for high growth

    diff_r2lin_log = df_sorted.at[highest_r2_index, 'Lin/Log Diff']

    # Plateau definition & time to 90% of the plateau

    k_scenarios = np.array(df_sorted['K'])
    r_scenarios = np.array(df_sorted['r'])
    p0_scenarios = np.array(df_sorted['p0'])

    k_full = np.array(df_full['K'])
    r_full = np.array(df_full['r'])

    # Growth Rate
    rd = main.discrete_growth_rate(users[0:data_len], dates[0:data_len] + 1970)
    print(rd, "rdrd")
    print(users[0:data_len], dates[0:data_len] + 1970)
    average_rd = sum(rd[-3:])/3

    # Growth Rate message
    if average_rd < 0.1:
        growth_rate_graph_message1 = "The annual average discrete growth rate is approaching 0 (" + f"{average_rd:.3f}"+ \
                                     "), indicating an approaching end of the growth."
        growth_rate_graph_color= "yellow"
        if any(r < 0 for r in r_full[-5:]):
            growth_rate_graph_message1 = growth_rate_graph_message1 + " However, the latest growth rates vary substantially," \
                                                                      "  which could lead to a prolonged growth."
    else:
        growth_rate_graph_message1 = "The annual average discrete growth rate is larger than 0.1, (" + f"{average_rd:.3f}"+ \
                                     ") indicating a substantial growth."
        growth_rate_graph_color = "green"


    # Growth Accordion
    # Promising Growth
    if diff_r2lin_log > 0.1 or any(k < 0 for k in k_full[-5:]) or any(r < 0 for r in r_full[-5:] if r > 0.1):
        growth_message_title = "Promising Exponential Growth Ahead!"
        growth_message_body = "Rast's model predicts a strong likelihood of exponential growth in the foreseeable " \
                              "future, surpassing the best-case scenario displayed."
        growth_message_color = "green"
        growth_icon_color = DashIconify(icon="uit:chart-growth", color=dmc.theme.DEFAULT_COLORS["green"][6], width=20)

    # Stable Growth
    else:
        growth_message_title = "Consistent and Predictable Growth!"
        growth_message_body = "Rast's model suggests a high probability that the dataset has transitioned into a " \
                              "stable growth pattern, aligning closely with our best-case scenario."
        growth_message_color = "yellow"
        growth_icon_color = DashIconify(icon="uit:chart-growth", color=dmc.theme.DEFAULT_COLORS["yellow"][6], width=20)

    # High Growth
    if k_scenarios[-1] < 1e9:
        plateau_high_growth = f"{k_scenarios[-1] / 1e6:.1f} M"
    else:
        plateau_high_growth = f"{k_scenarios[-1] / 1e9:.1f} B"
    time_high_growth = main.time_to_population(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1],
                                               k_scenarios[-1] * 0.9) + 1970
    # Low Growth
    if k_scenarios[0] < 1e9:
        plateau_low_growth = f"{k_scenarios[0] / 1e6:.1f} M"
    else:
        plateau_low_growth = f"{k_scenarios[0] / 1e9:.1f} B"
    time_high_growth = main.time_to_population(k_scenarios[0], r_scenarios[0], p0_scenarios[0],
                                               k_scenarios[0] * 0.9) + 1970
    # Best Growth
    if k_scenarios[highest_r2_index] < 1e9:
        plateau_best_growth = f"{k_scenarios[highest_r2_index] / 1e6:.1f} M"
    else:
        plateau_best_growth = f"{k_scenarios[highest_r2_index] / 1e9:.1f} B"

    time_best_growth = main.time_to_population(k_scenarios[highest_r2_index],
                                               r_scenarios[highest_r2_index],
                                               p0_scenarios[highest_r2_index],
                                               k_scenarios[highest_r2_index] * 0.95) + 1970

    # Plateau Accordion
    if diff_r2lin_log > 0.1:
        plateau_message_title = "Plateau (95%) could be reached in " + main.string_formatting_to_date(time_high_growth) \
                                + " with " + str(plateau_high_growth) + " users "
        plateau_message_body = "Given the likelihood of exponential growth in the foreseeable " \
                               "future, the high growth scenario is likely with 95% of its plateau at " + \
                               str(plateau_high_growth) + " users which should happen in " + main.string_formatting_to_date(
            time_high_growth)
    else:
        plateau_message_title = "Plateau could be reached in " + main.string_formatting_to_date(time_best_growth) \
                                + " with " + str(plateau_best_growth) + " users"
        plateau_message_body = "Given the likelihood of a stable growth in the foreseeable " \
                               "future, the best growth scenario is likely to reach 95% of its plateau in " \
                               + main.string_formatting_to_date(time_best_growth) + " with " + str(
            plateau_best_growth) + " users"
    # Plateau message color
    if time_best_growth < date_picked_formatted:
        plateau_message_color = "red"
        plateau_icon_color = DashIconify(icon="radix-icons:pin-top", color=dmc.theme.DEFAULT_COLORS["red"][6], width=20)
    else:
        plateau_message_color = "green"
        plateau_icon_color = DashIconify(icon="radix-icons:pin-top", color=dmc.theme.DEFAULT_COLORS["green"][6], width=20)

    print("Time growth", time_best_growth, date_picked, date_picked_formatted)
    print(plateau_message_color)

    # Formatting of the displayed correlation message

    formatted_correlation = f"{users_revenue_correlation * 100:.2f}"  # Formatting the displayed r^2:
    if users_revenue_correlation >= 0.9:
        correlation_message_title = "Great metric selected!"
        correlation_message_body = "The " + str(key_unit) + " you are using seem to be the right metric to " \
                                                            "estimate the valuation, because " + str(key_unit) + \
                                   " account for " + str(formatted_correlation) + "% of the revenue variability."
        correlation_message_color = "green"
        correlation_icon_color = DashIconify(icon="uit:chart-growth", color=dmc.theme.DEFAULT_COLORS["green"][6],
                                         width=20)
    elif users_revenue_correlation > 0:
        correlation_message_title = "Another metric could be better"
        correlation_message_body = str(key_unit) + " do not have a strong correlation with the revenue over time. " \
                                                   "You may want to consider another metric to estimate this " \
                                                   "company's valuation, since only " + str(formatted_correlation) + \
                                   "% of the revenue variability is explained by this metric."
        correlation_message_color = "yellow"
        correlation_icon_color = DashIconify(icon="uit:chart-growth", color=dmc.theme.DEFAULT_COLORS["yellow"][6],
                                             width=20)

    else:
        correlation_message_title = "Correlation not applicable"
        correlation_message_body = "The correlation information is only relevant for companies"
        correlation_message_color = "gray"
        correlation_icon_color = DashIconify(icon="uit:chart-growth", color=dmc.theme.DEFAULT_COLORS["gray"][6],
                                             width=20)

    # Slider definition
    df_scenarios = df_sorted
    data_ignored_array = df_scenarios.index.to_numpy()
    slider_max_value = data_ignored_array[-1]

    print("SLIDERTEST")
    print(highest_r2_index)
    # Defining the upper/lower limit after which the star is displayed right next to the label
    percentage_limit_label = 0.1
    max_limit_slider_label = data_ignored_array[int(len(data_ignored_array) * (1-percentage_limit_label))]
    min_limit_slider_label = data_ignored_array[int(len(data_ignored_array)*percentage_limit_label)]
    print(max_limit_slider_label)
    print(min_limit_slider_label)
    # Slider max definition
    if k_scenarios[-1] >= 1_000_000_000:  # If the max value of the slider is over 1 B
        if highest_r2_index > max_limit_slider_label:  # If the best = max, then display them side by side"
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000000000:.1f}B"},
                {"value": highest_r2_index},
                {"value": data_ignored_array[-1], "label": f"★{k_scenarios[-1] / 1000000000:.1f}B"},
            ]
        elif highest_r2_index < min_limit_slider_label:  # If the best = mind, then display them side by side"
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000000000:.1f}B ★"},
                {"value": highest_r2_index},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1] / 1000000000:.1f}B"},
            ]
        else:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000000000:.1f}B"},
                {"value": highest_r2_index, "label": "★"},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1] / 1000000000:.1f}B"},
            ]
    elif k_scenarios[-1] >= 1_000_000:
        if highest_r2_index > max_limit_slider_label:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000000:.0f}M"},
                {"value": data_ignored_array[-1], "label": f"★{k_scenarios[-1] / 1000000:.0f}M"},
            ]
        elif highest_r2_index < min_limit_slider_label:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000000:.0f}M ★"},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1] / 1000000:.0f}M"},
            ]
        else:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000000:.0f}M"},
                {"value": highest_r2_index, "label": "★"},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1] / 1000000:.0f}M"},
            ]

    else:  # If K max smaller than 1 million
        if highest_r2_index > max_limit_slider_label:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000:.0f}K"},
                {"value": data_ignored_array[-1], "label": f"★{k_scenarios[-1] / 1000:.0f}K"},
            ]
        elif highest_r2_index < min_limit_slider_label:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000:.0f}K ★"},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1] / 1000:.0f}K"},
            ]
        else:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000:.0f}K"},
                {"value": highest_r2_index, "label": "★"},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1] / 1000:.0f}K"},
            ]

    # Updating the datepicker graph traces, the high & the low growth scenario
    main_plot.update_traces(
        selector=dict(name="current-date"),
        x=date_picked_formatted,
    )

    # Financial Values Calculation

    # Calculating the date picked (removing one day that is added previously
    date_str = date_picked
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')

    # Remove one day
    new_date_obj = date_obj - timedelta(days=1)

    # Convert back to string
    new_date_str = new_date_obj.strftime('%Y-%m-%d')

    # Check whether it is a public company: Market cap fetching & displaying profit margin,
    # discount rate and arpu for Companies
    symbol_company = df_dataset.loc[0, 'Symbol']
    if symbol_company != "N/A":
        # If the date picked is the latest, then API call
        try:
            latest_market_cap = dataAPI.get_marketcap(symbol_company)
        except Exception as e:
            print("Couldn't fetch latest market cap, assigning DB value")
            latest_market_cap = df_dataset.loc[closest_index, 'Market Cap'] * 1e3
        if new_date_str == dates_raw[-1]:
            current_market_cap = latest_market_cap  # Sets valuation if symbol exists
        # Otherwise, the market cap of the last quarter is picked
        else:
            current_market_cap = df_dataset.loc[closest_index, 'Market Cap'] * 1e3
        current_annual_profit_margin = df_dataset.loc[closest_index, 'Profit Margin']
        current_revenue_array = np.array(df_dataset['Revenue'])
        current_revenue_array = current_revenue_array[:closest_index + 1]
        current_revenue_df = df_dataset.iloc[:-closest_index].copy()
        filtered_revenue = current_revenue_array[current_revenue_array != 0]
        hype_market_cap = f"Market Cap: ${current_market_cap / 1000:.2f}B"  # Formatted text for hype meter
        # yearly_revenue, total_assets = dataAPI.get_previous_quarter_revenue(symbol_company)  # Getting with API
        quarterly_revenue = filtered_revenue * 1_000_000  # Getting in database
        yearly_revenue_quarters = sum(quarterly_revenue[-4:])
        average_users_past_year = (current_users + current_users_array[closest_index - 4]) / 2
        #current_arpu = yearly_revenue_quarters / average_users_past_year
        current_arpu = sum(quarterly_revenue[-4:] / current_users_array[-4:])
        printed_current_arpu = f"{current_arpu:.0f} $ (current arpu)"  # formatting
        marks_profit_margin_slider = []
        if current_annual_profit_margin > 1:
            value_profit_margin_slider = float(current_annual_profit_margin)
            text_profit_margin = "Latest annual profit margin: " + str(current_annual_profit_margin) + "% 🤩",

        else:

            text_profit_margin = "Latest annual profit margin: " + str(current_annual_profit_margin) + "% 😰",

    else:
        current_market_cap = 0  # Otherwise, market_cap = zero
        current_arpu = 0
        total_assets = 0
        hype_market_cap = ""
        show_company_functionalities = {'display': 'none'}
        users_revenue_regression = 0
        printed_current_arpu = 0
        text_profit_margin = ""
        latest_market_cap = 0

    # Plateau Accordion
    arpu_needed = main.arpu_for_valuation(k_scenarios[highest_r2_index], r_scenarios[highest_r2_index],
                                          p0_scenarios[highest_r2_index], 0.2, 0.05, 10,
                                          current_market_cap * 1000000)
    # Formating the displayed market cap:
    if current_market_cap >= 1000:
        formatted_market_cap = f"{current_market_cap / 1000:.2f} B$"
    else:
        formatted_market_cap = f"{current_market_cap} mio$"
    if current_market_cap != 0:
        valuation_message_title = "Current market cap is " + str(formatted_market_cap)
        valuation_message_body = "Given the projected user growth, " + str(dropdown_value) + " should make " + \
                                 f"{arpu_needed:.0f} $" + " per user and per year to justify the current market cap " \
                                                          "(assuming a 20% profit margin & a 5% discount rate). They are" \
                                                          " currently making " + f"{current_arpu:.0f} $" + " per user" \
                                                                                                           " and have a " + f"{current_annual_profit_margin:.1f} % " + "" \
                                                                                                                                                                       "net profit margin."
        valuation_message_color = "green"
        valuation_icon_color = DashIconify(icon="radix-icons:rocket", color=dmc.theme.DEFAULT_COLORS["green"][6],
                                         width=20)
    else:
        valuation_message_title = "Valuation not applicable"
        valuation_message_body = "The valuation information is only relevant for companies"
        valuation_message_color = "gray"
        valuation_icon_color = DashIconify(icon="radix-icons:rocket", color=dmc.theme.DEFAULT_COLORS["gray"][6],
                                           width=20)

    # Initial ARPU Growth definition
    arpu_growth = 2
    print("Couleurs")
    print(growth_icon_color, plateau_icon_color, valuation_icon_color, correlation_icon_color)

    # Initial slider k value
    initial_slider_values['slider_k'] = highest_r2_index
    initial_slider_values['slider_arpu'] = arpu_growth

    t2 = time.perf_counter(), time.process_time()
    print(f" Scenarios calculation")
    print(plateau_message_color)
    print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
    return highest_r2_index, initial_slider_values, growth_message_title, growth_message_body, growth_message_color, growth_icon_color, \
        ["growth"], plateau_message_title, plateau_message_body, plateau_message_color, plateau_icon_color, valuation_message_title, \
        valuation_message_body, valuation_message_color, valuation_icon_color, correlation_message_title, correlation_message_body, \
        correlation_message_color, correlation_icon_color, df_sorted_dict, slider_max_value, marks_slider, current_arpu, hype_market_cap, \
        current_market_cap, latest_market_cap, arpu_growth, growth_rate_graph_message1, growth_rate_graph_color


@app.callback([
    Output(component_id='main-graph1', component_property='figure'),  # Update graph 1
    Output(component_id='main-graph2', component_property='figure'),  # Update graph 2 about regression
    # Output(component_id='main-graph3', component_property='figure'),  # Update graph 3
    # Output(component_id='carrying-capacity', component_property='children'),  # Update the carrying capacity
    Output(component_id='r2-ring-progress', component_property='sections'),  # Update regression
    # Output(component_id='range-slider-k', component_property='max'),
    # Output(component_id='range-slider-k', component_property='marks'),
    # Output(component_id='graph-message', component_property='hide'),
    Output(component_id='graph-message', component_property='children'),
],

    [
        Input(component_id='range-slider-k', component_property='value'),  # Take user slider value
        Input(component_id='date-picker', component_property='value'),  # Take date-picker date
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
    users_raw = np.array([entry['Users'] for entry in df_raw]) * 1e6
    dates = dates - 1970
    # Users are taken from the database and multiply by a million
    users = np.array([entry['Users'] for entry in df_dataset_dict])
    users = users.astype(float) * 1000000
    arpu_growth = arpu_growth / 100

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
    value_section = r_squared_showed * 100
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
                                                   k_scenarios[data_slider] * 0.9) + 1970

    graph_message = "Anticipated Plateau Date (blue line): " + main.string_formatting_to_date(
        time_selected_growth) + ", Projected at " + \
                    str(plateau_selected_growth) + " users"

    # Polynomial approximation
    # logfit = main.log_approximation(dates[number_ignored_data:data_len], users[number_ignored_data:data_len])
    # k_log = np.exp(-logfit[1]/logfit[0])
    # df_log = main.parameters_dataframe_given_k(dates[0:data_len], users[0:data_len])
    # print("LOG params")
    # print(df_log)
    # polynum3 = main.polynomial_approximation(dates[number_ignored_data:data_len], users[number_ignored_data:data_len], 3)
    # polynum2 = main.polynomial_approximation(dates[number_ignored_data:data_len], users[number_ignored_data:data_len],
    # 2)
    # polynum1 = main.polynomial_approximation(dates[number_ignored_data:data_len], users[number_ignored_data:data_len], 1)

    # Calculating the other parameters, given K provided by the log approximation
    # r_log, p0_log, r_squared_log = main.logistic_parameters_given_K(dates[number_ignored_data:data_len],
    # users[number_ignored_data:data_len], k_log)
    # Build Main Chart
    # ---------------------
    hovertemplate_maingraph = "%{text}"
    # fig_main = go.Figure(layout=layout_main_graph)
    fig_main = make_subplots(specs=[[{"secondary_y": True}]])

    x_axis = [dates[0] + 1970, dates[-1] * 2 - dates[0] + 1970]
    # fig_main.update_xaxes(range=x_axis)  # Fixing the size of the X axis with users max + 10%
    # Historical data
    # Highlight points considered for the approximation
    fig_main.add_trace(go.Bar(name="Dataset", x=dates_raw[number_ignored_data:data_len],
                              y=users[number_ignored_data:data_len],
                              marker_color="Black", showlegend=False, hoverinfo='none'))
    y_predicted = users
    formatted_y_values = [f"{y / 1e6:.1f} M" if y < 1e9 else f"{y / 1e9:.2f} B" for y in y_predicted]
    # Line linking the historical data for smoothing the legend hover
    fig_main.add_trace(go.Scatter(name="Historical data", x=dates_raw,
                                  y=y_predicted, mode='lines', opacity=1,
                                  marker_color="Black", text=formatted_y_values, hovertemplate=hovertemplate_maingraph))
    # Highlight points not considered for the approximation
    fig_main.add_trace(
        go.Bar(name="Data omitted", x=dates_raw[0:number_ignored_data], y=users[0:number_ignored_data],
               marker_color="Grey", hoverinfo='none', showlegend=False))
    # Highlight points past the current date
    fig_main.add_trace(go.Bar(name="Future data", x=dates_raw[data_len:],
                              y=users[data_len:],
                              marker_color='#e6ecf5', hoverinfo='none', ))

    # Add vertical line indicating the year of the prediction for retrofitting
    # fig_main.add_vline(x=history_value_graph, line_width=1, line_dash="dot",
    # opacity=0.5, annotation_text="   Forecast")
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
    # Update layout to customize the annotation
    fig_main.update_layout(layout_main_graph)
    # fig_main.update_yaxes(range=[0, k_scenarios[-1]*1.1])  # Fixing the size of the Y axis
    print("USERSRAW")
    print(users_raw)
    if k_scenarios[-1] > users_raw[-1]:
        range_y = [0, k_scenarios[-1] * 1.5]
    else:
        range_y = [0, users_raw[-1] * 1.5]
    fig_main.update_layout(
        hovermode="x unified",
        # Styling of the "FORECAST" text
        annotations=[
            dict(
                x=x_coordinate,
                y=0.9 * k_scenarios[-1],  # Adjust the y-position as needed
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
            range=range_y,
            fixedrange=True,
            title=graph_unit,
            minallowed=0,
            # maxallowed=k_scenarios[-1] * 1.5,
        ),
        xaxis=dict(
            # fixedrange=True,
            constrain='domain',
            minallowed=dates_raw[0],

        ),
        dragmode="pan",
    )
    fig_main.update_yaxes(fixedrange=True, secondary_y=True)

    # Prediction, S-Curves

    date_a = datetime.strptime(dates_raw[0], "%Y-%m-%d")
    date_b = datetime.strptime(dates_raw[-1], "%Y-%m-%d")

    # Calculate date_end using the formula date_b + 2 * (date_b - date_a)
    date_end = date_b + (date_b - date_a)

    date_end_formatted = main.date_formatting_from_string(date_end.strftime("%Y-%m-%d"))

    # Add S-curve - S-Curve the user can play with
    x = np.linspace(dates[0], float(date_end_formatted) - 1970, num=50)
    y_predicted = main.logisticfunction(k, r, p0, x)

    x_scenarios = np.linspace(dates[-1], float(date_end_formatted) - 1970, num=50)

    # Generate x_dates array
    x_dates = np.linspace(date_a.timestamp(), date_end.timestamp(), num=50)
    x_dates_scenarios = np.linspace(date_b.timestamp(), date_end.timestamp(), num=50)
    x_dates = [datetime.fromtimestamp(timestamp) for timestamp in x_dates]
    x_dates_scenarios = [datetime.fromtimestamp(timestamp) for timestamp in x_dates_scenarios]

    # print(len(x_dates), x_dates)
    # print(len(x), x)
    formatted_y_values = [f"{y / 1e6:.1f} M" if y < 1e9 else f"{y / 1e9:.2f} B" for y in y_predicted]
    fig_main.add_trace(go.Scatter(name="Growth Forecast", x=x_dates, y=y_predicted,
                                  mode="lines", line=dict(color='#4dabf7', width=2), opacity=0.8,
                                  text=formatted_y_values, hovertemplate=hovertemplate_maingraph))
    # Add 3 scenarios
    x0 = np.linspace(dates_actual[-1] + 0.25, dates_actual[-1] * 2 - dates_actual[0],
                     num=10)  # Creates a future timeline the size of the data

    # Low growth scenario
    print("lowlow")
    print(dates_raw)
    print(users)
    print(x_dates_scenarios)
    print(main.logisticfunction(k_scenarios[0], r_scenarios[0], p0_scenarios[0], x_scenarios))
    print(main.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1], x_scenarios))
    # x = np.linspace(dates[-1], dates[-1] * 2 - dates[0], num=50)
    y_trace = main.logisticfunction(k_scenarios[0], r_scenarios[0], p0_scenarios[0], x_scenarios)
    formatted_y_values = [f"{y / 1e6:.1f} M" if y < 1e9 else f"{y / 1e9:.2f} B" for y in y_trace]
    fig_main.add_trace(go.Scatter(name="Low growth", x=x_dates_scenarios,
                                  y=main.logisticfunction(k_scenarios[0], r_scenarios[0], p0_scenarios[0], x_scenarios),
                                  mode='lines',
                                  line=dict(color='LightGrey', width=0.5), showlegend=False, text=formatted_y_values,
                                  hovertemplate=hovertemplate_maingraph)),
    # fig.add_trace(go.Line(name="Predicted S Curve", x=x + 1970,
    # y=main.logisticfunction(k_scenarios[1], r_scenarios[1], p0_scenarios[1], x), mode="lines"))
    y_trace = main.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1], x_scenarios)
    formatted_y_values = [f"{y / 1e6:.1f} M" if y < 1e9 else f"{y / 1e9:.2f} B" for y in y_trace]
    # High growth scenario, if existent
    if len(k_scenarios) > 1:
        fig_main.add_trace(go.Scatter(name="High Growth", x=x_dates_scenarios,
                                      y=y_trace, mode='lines',
                                      line=dict(color='LightGrey', width=0.5),
                                      textposition="top left", textfont_size=6, showlegend=False,
                                      text=formatted_y_values, hovertemplate=hovertemplate_maingraph))
    years_future_users = list(range(2023 - 1970, 2039 - 1970))
    print("High Growth")
    print(main.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1], years_future_users))
    print("Low Growth")
    print(main.logisticfunction(k_scenarios[0], r_scenarios[0], p0_scenarios[0], years_future_users))

    # Filling the area of possible scenarios
    x_area = np.append(x, np.flip(x))  # Creating one array made of two Xs
    y_area_low = main.logisticfunction(k_scenarios[0], r_scenarios[0], p0_scenarios[0], x)  # Low growth array
    y_area_high = main.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1],
                                        np.flip(x))  # High growth array
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

    # Filling the area of possible scenarios
    x_area = np.append(x, np.flip(x))  # Creating one array made of two Xs
    y_area_low = main.logisticfunction(k_scenarios[0], r_scenarios[0], p0_scenarios[0], x)  # Low growth array
    y_area_high = main.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1],
                                        np.flip(x))  # High growth array
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

    revenue = np.array([entry['Revenue'] for entry in df_dataset_dict]) * 1_000_000
    # Find the indices where cells in the second array are not equal to "N/A"
    valid_indices = np.where(revenue != 0)
    print(date_picked_formatted_original, type(date_picked_formatted_original))

    years = 6
    current_date = datetime.now()
    future_arpu = [current_arpu * (1 + arpu_growth) ** year for year in range(years)]
    future_arpu_dates = [datetime.strptime(date_picked_formatted_original, '%Y-%m-%d') + timedelta(days=365 * year) for
                         year in range(years)]

    # Filter rows based on valid indices
    dates_revenue = dates_raw[valid_indices]
    users_revenue = users[valid_indices]
    dates_revenue_actual = main.get_earlier_dates(dates[valid_indices], history_value_formatted)
    # users_revenue_actual = main.get_earlier_dates(users_revenue, history_value_formatted)
    data_len_revenue_array = dates_raw[data_len:]
    data_len_revenue = len(data_len_revenue_array[data_len_revenue_array != 0])
    revenue = revenue[valid_indices]
    if len(revenue) > 0:
        annual_revenue_per_user = revenue * 4 / users_revenue
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
            #text=formatted_y_values,
            #hovertemplate=hovertemplate_maingraph
            ),
            secondary_y=True,
        )
        # Past revenue line
        fig_main.add_trace(go.Scatter(
            name="Annual Revenue per User (arpu)",
            x=x_revenue,
            y=y_revenue,
            mode='lines',
            line=dict(color='#51CF66', width=1),
            showlegend=True,
            text=formatted_y_values,
            hovertemplate=hovertemplate_maingraph),
            secondary_y=True,
            # visible='legendonly',
        )
        fig_main.add_trace(go.Scatter(
            name="Future Annual Revenue per User (arpu)",
            x=future_arpu_dates,
            y=future_arpu,
            mode='lines',
            line_dash="dot",
            marker=dict(color='#51CF66', size=4),
            showlegend=True,
            text=formatted_y_values,
            hovertemplate=hovertemplate_maingraph),
            secondary_y=True,
        )
        # Revenue past the selected date that are known [data_len:]
        fig_main.add_trace(go.Scatter(
            name="Annual Revenue per User/Unit (arpu)",
            x=x_revenue[len(dates_revenue_actual):],
            y=y_revenue[len(dates_revenue_actual):],
            mode='lines',
            line=dict(color='Gray', width=1),
            showlegend=False,
            #text=formatted_y_values,
            hovertemplate=hovertemplate_maingraph),
            secondary_y=True,
        )
        fig_main.update_yaxes(range=[min(annual_revenue_per_user) * 0.9, max(annual_revenue_per_user) * 1.5],
                              title_text="Annual Revenue per User/Unit [$]",
                              color="#51CF66",
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

    fig_second = go.Figure(layout=layout_main_graph)
    fig_second.update_xaxes(range=[0, users[-1] * 1.1])  # Fixing the size of the X axis with users max + 10%
    # max_rd_value = df_sorted['r'].max()

    # fig_second.update_yaxes(range=[0, max_rd_value]) # Fixing the size of the Y axis
    fig_second.add_trace(
        go.Scatter(name="Discrete Growth Rate Considered", x=main.discrete_user_interval(users),
                   y=main.discrete_growth_rate(users, dates + 1970), mode="markers", line=dict(color='#54c4f4')
                   ))
    print("Rdrdrd")
    print(users, dates + 1970)
    print(main.discrete_growth_rate(users, dates + 1970))
    # Add trace of the regression
    fig_second.add_trace(
        go.Scatter(name="Regression", x=main.discrete_user_interval(users),
                   y=-r / k * main.discrete_user_interval(users) + r, mode="lines", line=dict(color='#54c4f4')))
    # Add trace of the regression obtained by fixing k
    # fig_second.add_trace(
    #    go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
    #               y=-r_log / k_log * main.discrete_user_interval(users) + r_log, mode="lines", line=dict(color='Purple')))
    # Changes the color of the scatters ignored
    # print(main.discrete_user_interval(users[0:number_ignored_data]))
    if number_ignored_data > 0:
        fig_second.add_trace(
            go.Scatter(name="Ignored Data Points", x=main.discrete_user_interval(users[0:number_ignored_data]),
                       y=main.discrete_growth_rate(users[0:number_ignored_data], dates[0:number_ignored_data] + 1970),
                       mode="markers", line=dict(color='#808080')))

    # Changes the color of the scatters after the date considered
    if data_len < len(dates):
        fig_second.add_trace(
            go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users[data_len:]),
                       y=main.discrete_growth_rate(users[data_len:], dates[data_len:] + 1970),
                       mode="markers", line=dict(color='#e6ecf5')))

    # Add trace of the polynomial approximation
    # fig_second.add_trace(
    # go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
    # y=np.polyval(polynum1, main.discrete_user_interval(users)), mode="lines", line=dict(color="Green")))
    # fig_second.add_trace(
    #    go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
    #               y=np.polyval(polynum2, main.discrete_user_interval(users)), mode="lines", line=dict(color="Blue")))
    # fig_second.add_trace(
    #    go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
    #               y=np.polyval(polynum3, main.discrete_user_interval(users)), mode="lines", line=dict(color="Red")))
    # fig_second.add_trace(
    #    go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users),
    #               y=np.polyval(logfit, np.log(main.discrete_user_interval(users))), mode="lines", line=dict(color="Orange")))

    '''

    # Build third chart containing the evolution of r^2 & rmsd linked to the # of data ignored
    # -------------------------------------------
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
    k_printed = int(np.rint(k) / pow(10, 6))
    k_printed = "{:,} M".format(k_printed)
    # PLATEAU: Time when the plateau is reached, assuming the plateau is "reached" when p(t)=95%*K
    print(p0)
    if p0 > 2.192572e-11:
        t_plateau = main.time_to_population(k, r, p0, 0.95 * k) + 1970
        month_plateau = math.ceil((t_plateau - int(t_plateau)) * 12)
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
    return fig_main, fig_second, sections, graph_message


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
    if launch_counter['flag'] is not True:
        launch_counter['flag'] = True
        show_graph_card = {'display': 'block'}
        hide_graph_card = {'display': 'none'}
        print("Displaying the graph hihi")
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
    profit_margin = profit_margin / 100
    discount_rate = discount_rate / 100
    YEARS_DCF = 10
    current_market_cap = current_market_cap * 1000000
    # Ignored to avoid calculating this. Can be discommented to reuse this function
    # arpu_needed = main.arpu_for_valuation(k_selected, r_selected, p0_selected, profit_margin, discount_rate, YEARS_DCF, current_market_cap)
    arpu_needed = 0
    arpu_difference = arpu_needed / current_arpu
    printed_arpu = f"{arpu_needed:.0f} $. The current arpu " + f"({current_arpu:.0f} $)" + " should be multiplied by " + f"{arpu_difference:.2f}!"  # formatting
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
    Output(component_id="current-valuation-calculated", component_property="data"),
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
    profit_margin = profit_margin / 100
    discount_rate = discount_rate / 100
    arpu_growth = arpu_growth / 100
    current_market_cap = current_market_cap * 1000000

    # Equity calculation
    current_customer_equity = users[-1] * current_arpu * profit_margin
    future_customer_equity = main.net_present_value_arpu_growth(k_selected, r_selected, p0_selected, current_arpu,
                                                                arpu_growth, profit_margin, discount_rate, YEARS_DCF)
    total_customer_equity = current_customer_equity + future_customer_equity
    non_operating_assets = total_assets

    current_valuation = total_customer_equity + non_operating_assets
    hype_total = current_market_cap - total_customer_equity - non_operating_assets

    # Calculating the values of the hype meter
    non_operating_assets_ratio = non_operating_assets / current_market_cap * 100
    noa_tooltip = f"Non-Operating Assets: ${total_assets / 1e9:.2f} B. \n They represent additional valuable company " \
                  f"assets, such as Goodwill"
    customer_equity_ratio = total_customer_equity / current_market_cap * 100
    customer_equity_tooltip = f"Customer Equity: ${total_customer_equity / 1e9:.2f} B.   It represents current and " \
                              f"future customer-generated profit, calculated with the selected parameters with a " \
                              f"discounted cashflow method"
    hype_ratio = hype_total / current_market_cap * 100
    if hype_total < 0.0:
        hype_ratio = 0.0
    hype_tooltip = f"Hype: ${hype_total / 1e9:.2f} B.  It reflects the current overvaluation of the company in terms " \
                   f"of market capitalization versus actual value."
    hype_indicator_color, hype_indicator_text = main.hype_meter_indicator_values(hype_ratio / 100)

    return non_operating_assets_ratio, noa_tooltip, customer_equity_ratio, customer_equity_tooltip, hype_ratio, \
        hype_tooltip, hype_indicator_color, hype_indicator_text, current_valuation


# Callback displaying the functionalities & graph cards, and hiding the text
@app.callback(
    Output(component_id='data-selection-counter', component_property='data', allow_duplicate=True),
    # Output(component_id='valuation-graph', component_property='figure'),  # Update valuation graph
    # Output(component_id='valuation-graph-message', component_property='children'),
    # Output(component_id='valuation-graph-message', component_property='color'),
    # Output(component_id='valuation-graph-message', component_property='title'),
    Output(component_id='valuation-over-time', component_property='data'),
    Output("loader-general", "style", allow_duplicate=True),
    # Input(component_id='date-picker', component_property='value'),  # Take date-picker date
    Input(component_id='users-dates-formatted', component_property='data'),
    Input(component_id='total-assets', component_property='data'),
    Input(component_id='dataset-selection', component_property='value'),
    Input(component_id='users-dates-raw', component_property='data'),
    Input(component_id='latest-market-cap', component_property='data'),  # Stores the current (now) company market cap
    # State(component_id='valuation-over-time', component_property='data'),
    [State('data-selection-counter', 'data')]
    , prevent_initial_call=True
)
def historical_valuation_calculation(df_formatted, total_assets, data, df_raw, latest_market_cap,
                                     df_rawdataset_counter, ):
    print("Dataset Flag")
    print(df_rawdataset_counter)
    # The entire callback is skipped if the current market cap = 0, i.e. if it is not a public company OR
    # if it was already calculated
    if latest_market_cap == 0 or df_rawdataset_counter == False:
        raise PreventUpdate
    t1 = time.perf_counter(), time.process_time()
    dates_raw = np.array([entry['Date'] for entry in df_raw])
    dates_new = np.array([entry['Date'] for entry in df_formatted])
    revenue_df = np.array([entry['Revenue'] for entry in df_formatted])
    profit_margin_df = np.array([entry['Profit Margin'] for entry in df_formatted])
    profit_margin_original = profit_margin_df / 100
    market_cap_df = np.array([entry['Market Cap'] for entry in df_formatted])
    market_cap_original = market_cap_df*1e9
    dates_original = dates_new - 1970
    # Users are taken from the database and multiplied by a million
    users_new = np.array([entry['Users'] for entry in df_formatted])
    users_original = users_new.astype(float) * 1_000_000
    MIN_REVENUE_INDEX = MIN_DATE_INDEX

    # Iteration range for valuation calculation
    iteration_range = [MIN_DATE_INDEX,
                       len(dates_original)]  # Range for calculating all the valuations, starting from the 4th date
    # Dataframe creation for all the valuation over time

    # Valuation calculation
    non_operating_assets = total_assets
    # df_valuation_over_time = pd.DataFrame(columns=columns)
    valuation_data = []
    print("Iteration range", iteration_range)
    if df_rawdataset_counter:  # calculates the historic of valuation only if the dataset has been updated
        for i in range(iteration_range[0], iteration_range[1]):
            dates_valuation = dates_original[:i]
            users_valuation = users_original[:i]
            quarterly_revenue = revenue_df * 1_000_000  # Getting in database
            revenue_valuation = quarterly_revenue[:i]
            market_cap_valuation = market_cap_original[i]

            profit_margin_valuation = profit_margin_original[:i]

            # Smoothing the data
            #dates, users = main.moving_average_smoothing(dates_valuation, users_valuation, 1)
            dates = dates_valuation
            users = users_valuation

            # All parameters are calculated by ignoring data 1 by 1, taking the history reference as the end point
            df_full = main.parameters_dataframe(dates,
                                                users)  # Dataframe containing all parameters with all data ignored
            df_sorted = main.parameters_dataframe_cleaning(df_full,
                                                           users)  # Dataframe where inadequate scenarios are eliminated

            if df_sorted.empty: # Smoothening data for cases where it doesn't work
                # Smoothing the data
                #dates1, users1 = main.moving_average_smoothing(dates_valuation, users_valuation, 4)
                dates = dates_valuation
                users = users_valuation

                # All parameters are calculated by ignoring data 1 by 1, taking the history reference as the end point
                df_full1 = main.parameters_dataframe(dates,
                                                    users)  # Dataframe containing all parameters with all data ignored
                df_sorted = main.parameters_dataframe_cleaning(df_full1,
                                                               users)  # Dataframe where inadequate scenarios are eliminated
                if df_sorted.empty:
                    print("Cleaning it minimally")
                    df_sorted = main.parameters_dataframe_cleaning_minimal(df_full, users)
                    print("df_sorted_minimally", df_sorted)
                    if df_sorted.empty:
                        print("No scenario could be calculated")
                    #continue
            else:
                print("Successful scenarios exist")
            # Number of scenarios to store
            i -= MIN_DATE_INDEX

            # Profit margin assessment
            profit_margin = np.empty(2)
            profit_margin_previous_year = profit_margin_valuation[-4:]
            average_profit_margin = sum(profit_margin_previous_year) / 4
            if average_profit_margin <= 0:
                min_profit_margin = 0.01
                max_profit_margin = 0.1
            else:
                min_profit_margin = average_profit_margin
                #max_profit_margin = average_profit_margin + 0.05
                max_profit_margin = max(profit_margin_valuation) + 0.05

            profit_margin[0] = min_profit_margin  # Low scenario
            profit_margin[1] = max_profit_margin  # High scenario

            # Discount Rate assessment
            discount_rate = np.empty(2)
            discount_rate[0] = 0.1  # Low scenario
            discount_rate[1] = 0.1  # High scenario

            # Arpu growth assessment
            arpu_growth = np.empty(2)
            arpu_growth[0] = 0.01  # Low scenario
            arpu_growth[1] = 0.05  # High scenario

            # Current ARPU calculation
            yearly_revenue_quarters = sum(revenue_valuation[-4:])
            average_users_past_year = (users_valuation[-1] + users_valuation[-5]) / 2
            current_arpu = yearly_revenue_quarters / average_users_past_year

            num_iterations = 2
            # Storing the data of two scenarios for a given date
            for j in range(num_iterations):
                # If no scenario is found, 0 is appended. Later the 0 is transformed in the last known valuation
                if df_sorted.empty:
                    valuation_data.append([
                        dates_new[i + MIN_DATE_INDEX],
                        dates_raw[i + MIN_DATE_INDEX],
                        0, 0, 0, 0, 0, 0, 0
                    ])
                else:
                    k_selected = df_sorted.at[j * (len(df_sorted) - 1), 'K']
                    r_selected = df_sorted.at[j * (len(df_sorted) - 1), 'r']
                    p0_selected = df_sorted.at[j * (len(df_sorted) - 1), 'p0']
                    future_customer_equity = main.net_present_value_arpu_growth(k_selected, r_selected, p0_selected,
                                                                                current_arpu, arpu_growth[j],
                                                                                profit_margin[j], discount_rate[j],
                                                                                YEARS_DCF)
                    current_customer_equity = users_valuation[-1] * current_arpu * profit_margin[j]
                    valuation_data.append([
                        dates_new[i + MIN_DATE_INDEX],
                        dates_raw[i + MIN_DATE_INDEX],
                        k_selected,
                        r_selected,
                        p0_selected,
                        profit_margin[j],
                        current_arpu,
                        future_customer_equity + current_customer_equity + non_operating_assets,
                        market_cap_valuation
                    ])
    # Convert the list to a DataFrame
    columns = ['Date', 'Date Raw', 'K', 'r', 'p0', 'Profit Margin', 'ARPU', 'Valuation', 'Market Cap']
    df_valuation_over_time = pd.DataFrame(valuation_data, columns=columns)
    df_valuation_over_time_dict = df_valuation_over_time.to_dict(orient='records')
    print("DF Valuation over time")
    print(df_valuation_over_time)
    hide_loader = {'display': 'none'}

    print("DF Valuation over time")
    print(df_valuation_over_time)
    # print(df_valuation_over_time2)
    t2 = time.perf_counter(), time.process_time()
    print(f" Performance of the valuation over time")
    print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
    return False, df_valuation_over_time_dict, hide_loader


@app.callback(
    # Output(component_id='data-selection-counter', component_property='data', allow_duplicate=True),
    Output(component_id='valuation-graph', component_property='figure', allow_duplicate=True),  # Update valuation graph
    Output(component_id='valuation-graph-message', component_property='children'),
    Output(component_id='valuation-graph-message', component_property='color'),
    Output(component_id='valuation-graph-message', component_property='title'),

    Input(component_id='valuation-over-time', component_property='data'),
    State(component_id='date-picker', component_property='value'),  # Take date-picker date
    State(component_id='users-dates-formatted', component_property='data'),
    State(component_id='total-assets', component_property='data'),
    State(component_id='users-dates-raw', component_property='data'),
    State(component_id='latest-market-cap', component_property='data'),  # Stores the current (now) company market cap
    Input(component_id="current-valuation-calculated", component_property="data"),
    prevent_initial_call=True,
)
def graph_valuation_over_time(valuation_over_time_dict, date_picked, df_formatted, total_assets, df_raw,
                              latest_market_cap, current_valuation):
    if latest_market_cap == 0:
        raise PreventUpdate
    print("Graph Valuation Start")
    t1 = time.perf_counter(), time.process_time()
    dates_raw = np.array([entry['Date'] for entry in df_raw])
    dates_new = np.array([entry['Date'] for entry in df_formatted])
    revenue_df = np.array([entry['Revenue'] for entry in df_formatted])
    profit_margin_df = np.array([entry['Profit Margin'] for entry in df_formatted])

    # Valuation calculation
    non_operating_assets = total_assets
    print("valuationoovertime")
    df_valuation_over_time = pd.DataFrame(valuation_over_time_dict)
    print(df_valuation_over_time)
    print(valuation_over_time_dict)
    # Graph creation

    # Creating the plot of the market cap - valuations
    dates_valuation_graph = df_valuation_over_time['Date Raw'].values
    valuation_values = df_valuation_over_time['Valuation'].values
    print("Vdates1")
    print(dates_valuation_graph)

    # Separate scenarios (odd and even rows)
    low_scenario_valuation = valuation_values[::2]  # Start from index 0, step by 2
    high_scenario_valuation = valuation_values[1::2]  # Start from index 1, step by 2
    dates_valuation_graph = dates_valuation_graph[::2]
    print("Vdates")
    print(dates_valuation_graph)

    # Create market cap array
    market_cap_array = np.array([entry['Market Cap'] for entry in df_formatted]) * 1e9
    market_cap_array = market_cap_array[MIN_DATE_INDEX:]
    market_cap_array2 = df_valuation_over_time['Market Cap'].values
    market_cap_array2 = market_cap_array2[::2]
    print("Mmmarket cap")
    print(market_cap_array)
    print(market_cap_array2)

    # Append today's date and latest market cap
    today_date = date.today()
    market_cap_array = np.append(market_cap_array, latest_market_cap * 1e6)
    zeros_array = [0] * 4 # Adding the 4 data ignored originally
    market_cap_array2 = np.append(zeros_array, market_cap_array2)
    dates_raw_market_cap = np.append(dates_raw, today_date)
    print("Vvvaluation")
    print(market_cap_array)
    print(dates_raw_market_cap)
    print(high_scenario_valuation)
    # today_date_formatted = main.date_formatting_from_string(today_date)

    fig_valuation = go.Figure(layout=layout_main_graph)

    # Hype interval
    # Filling the area of hype, between the market cap and the highest valuation
    dates_until_today = np.append(dates_valuation_graph, today_date)
    # length_market_cap_to_be_considered = len(market_cap_array) -
    y_area_low = market_cap_array[len(market_cap_array) - len(high_scenario_valuation) - 1:]  # Low growth array
    y_area_high = np.flip(np.append(high_scenario_valuation, current_valuation))  # High growth array
    y_area = np.append(y_area_low, y_area_high)
    dates_area = np.append(dates_until_today, np.flip(dates_until_today))

    # Hype Area
    fig_valuation.add_trace(go.Scatter(x=dates_area,
                                       y=y_area,
                                       fill='toself',
                                       line_color='rgba(255,255,255,0)',
                                       #fillcolor='#C92A2A',
                                       fillpattern={'shape': '/', 'bgcolor': 'white', 'fgcolor': '#C92A2A'},
                                       opacity=0.6,
                                       hoverinfo='none',
                                       showlegend=True,
                                       name='Hype',
                                       )
                            )
    print("AreaArrays")
    print(y_area_low)
    print(y_area_high)
    print(dates_area)

    # Confidence Interval
    # Filling the area of possible scenarios
    y_area_low = np.append(low_scenario_valuation, low_scenario_valuation[-1])  # Low growth array
    y_area_high = np.flip(np.append(high_scenario_valuation, high_scenario_valuation[-1]))  # High growth array
    y_area = np.append(y_area_low, y_area_high)
    dates_area = np.append(dates_until_today, np.flip(dates_until_today))
    fig_valuation.add_trace(go.Scatter(x=dates_area,
                                       y=y_area,
                                       fill='toself',
                                       line_color='rgba(255,255,255,0)',
                                       fillcolor='#E7F5FF',
                                       # opacity=0.3,
                                       hoverinfo='none',
                                       showlegend=True,
                                       name='Confidence Interval',
                                       )
                            )

    hovertemplate_maingraph = "%{text}"
    # Low Valuation
    formatted_y_values = [f"{y / 1e6:.1f} M" if y < 1e9 else f"{y / 1e9:.2f} B" for y in low_scenario_valuation]
    fig_valuation.add_trace(go.Scatter(name="Low Valuation", x=np.append(dates_valuation_graph, today_date), y=np.append(low_scenario_valuation, low_scenario_valuation[-1]),
                                       mode="lines", line=dict(color='#74C0FC', width=1, dash="dash"),
                                       text=formatted_y_values, hovertemplate=hovertemplate_maingraph))
    # High Valuation
    formatted_y_values = [f"{y / 1e6:.1f} M" if y < 1e9 else f"{y / 1e9:.2f} B" for y in high_scenario_valuation]
    fig_valuation.add_trace(go.Scatter(name="High Valuation", x=np.append(dates_valuation_graph, today_date), y=np.append(high_scenario_valuation, high_scenario_valuation[-1]),
                                       mode="lines", line=dict(color="#228BE6", width=1, dash="dash"),
                                       text=formatted_y_values, hovertemplate=hovertemplate_maingraph))
    # Market Cap
    formatted_y_values = [f"{y / 1e6:.1f} M" if y < 1e9 else f"{y / 1e9:.2f} B" for y in market_cap_array]
    fig_valuation.add_trace(go.Scatter(name="Market Cap", x=dates_raw_market_cap[MIN_DATE_INDEX:], y=market_cap_array,
                                       mode="lines", line=dict(color="#51CF66", width=2), text=formatted_y_values,
                                       hovertemplate=hovertemplate_maingraph))

    # Current valuation
    #print("Datata", date_picked, type(date_picked))
    # date_obj = datetime.strptime(date_picked, '%Y-%m-%d')
    if current_valuation > high_scenario_valuation[-1]:
        color_dot = "#C92A2A"
    else:
        color_dot = "green"

    fig_valuation.add_scatter(name="Calculated Valuation", x=[date_picked], y=[current_valuation],
                              marker=dict(
                                  color=color_dot,
                                  size=10
                              ), text=formatted_y_values,
                              hovertemplate=hovertemplate_maingraph)

    # Current Date - Vertical line
    # Defining the max y value
    if max(market_cap_array) > max(high_scenario_valuation):
        y_max = max(market_cap_array) * 1.1
    else:
        y_max = max(high_scenario_valuation) * 1.1

    fig_valuation.add_shape(
        go.layout.Shape(
            type="line",
            x0=date_picked,
            x1=date_picked,
            y0=0,
            y1=y_max,
            line=dict(color="gray", width=1, dash="dot"),
            opacity=0.6
        )
    )

    # Update Layout
    fig_valuation.update_layout(
        hovermode="x unified",
        yaxis=dict(
            # range=[0, k_scenarios[-1] * 1.1],
            fixedrange=True,
            title="Valuation & Market Cap [$B]",
            minallowed=0,
            # maxallowed=k_scenarios[-1] * 1.5,
        ),
        xaxis=dict(
            # fixedrange=True,
            constrain='domain',
            minallowed=dates_valuation_graph[0],

        ),
        dragmode="pan",
        # Adding "Selected date"
        annotations=[
            dict(
                x=date_picked,
                y=y_max * 1.02,  # Adjust the y-position as needed
                text="Picked Date",
                showarrow=False,
                font=dict(
                    size=8,  # Adjust the size as needed
                    color="black",  # Text color
                    # letter=5,
                ),
                opacity=0.3  # Set the opacity
            )
        ],
    )
    # Valuation message
    if market_cap_array[-1] < high_scenario_valuation[-1]:
        valuation_graph_title = "Promising investment!"
        valuation_graph_message = "The Current Market Cap is lower than the most optimistic valuation (" + \
                                  f"{high_scenario_valuation[-1] / 1e9:.2f} B$). It could be a good time to invest!"
        valuation_graph_color = "green"
    else:
        valuation_graph_title = "Risky investment!"
        valuation_graph_message = "The Current Market Cap is higher than the most optimistic valuation (" + \
                                  f"{high_scenario_valuation[-1] / 1e9:.2f} B$). It could be a good time to sell!"
        valuation_graph_color = "yellow"

    return fig_valuation, valuation_graph_message, valuation_graph_color, valuation_graph_title,


# Callback resetting enabling the reset button
@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


# Callback activating the button resetting the parameters
@app.callback(
    Output(component_id='reset-parameters', component_property='disabled'),
    Input(component_id='initial-sliders-values', component_property='data'),
    Input(component_id='range-slider-k', component_property='value'),
    Input(component_id='range-profit-margin', component_property='value'),
    Input(component_id='range-discount-rate', component_property='value'),
    Input(component_id='range-arpu-growth', component_property='value'),
    prevent_initial_call=True,
)
def activate_reset_button(initial_sliders_values, slider_k, slider_profit_margin, slider_discount_rate,
                          slider_arpu_growth):
    sliders_moved = any([
        int(slider_k) != int(initial_sliders_values['slider_k']),
        float(slider_profit_margin) != float(initial_sliders_values['slider_profit_margin']),
        float(slider_discount_rate) != float(initial_sliders_values['slider_discount_rate']),
        float(slider_arpu_growth) != float(initial_sliders_values['slider_arpu'])
    ])
    if sliders_moved == False:
        disabled_button = True

    else:
        disabled_button = False

    return disabled_button


# Callback resetting the initial values
@app.callback(
    Output(component_id='range-slider-k', component_property='value', allow_duplicate=True),
    Output(component_id='range-profit-margin', component_property='value', allow_duplicate=True),
    Output(component_id='range-discount-rate', component_property='value', allow_duplicate=True),
    Output(component_id='range-arpu-growth', component_property='value', allow_duplicate=True),
    Input(component_id='reset-parameters', component_property='n_clicks'),
    Input(component_id='initial-sliders-values', component_property='data'),
    prevent_initial_call=True,
)
def activate_reset_button(n_clicks, initial_sliders_values):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    slider_k = initial_sliders_values['slider_k']
    slider_profit_margin = initial_sliders_values['slider_profit_margin']
    slider_discount_rate = initial_sliders_values['slider_discount_rate']
    slider_arpu_growth = initial_sliders_values['slider_arpu']

    return slider_k, slider_profit_margin, slider_discount_rate, slider_arpu_growth


if __name__ == '__main__':
    app.run_server(debug=True)
