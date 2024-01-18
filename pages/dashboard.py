from dash import html, register_page  #, callback # If you need callbacks, import it here.
# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import dash
import dash_mantine_components as dmc
from dash import Dash, html, dcc, callback
from dash import callback
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dataAPI
import main
import dash_bootstrap_components as dbc
#import datetime
from datetime import datetime, timedelta, date
import math
from plotly.subplots import make_subplots
from dash_iconify import DashIconify
import time
from dash.exceptions import PreventUpdate


register_page(
    __name__,
    name='Dashboard',
    top_nav=True,
    path='/app'
)

# Values for the dropdown (all different companies in the DB)
labels = dataAPI.get_airtable_labels_new()


# Constants for the calculation
YEAR_OFFSET = 1970  # The year "zero" for all the calculations
MIN_DATE_INDEX = 5  # Defines the minimum year below which no date can be picked in the datepicker
YEARS_DCF = 15 # Amount of years taken into account for DCF calculation

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
            #dbc.Progress(value=20, color="#D1D1D1", bar=True, animated=True, striped=True, id="hype-meter-delta"),
            dbc.Progress(value=10, color="#D1D1D1", bar=True, animated=True, striped=True, label="Hype", id="hype-meter-hype"),
            dbc.Tooltip("Non-Operating Assets: $3.0B", target="hype-meter-noa", id='hype-tooltip-noa', placement="top"),
            dbc.Tooltip("Customer Equity: $3.0B", target="hype-meter-users", id='hype-tooltip-users', placement="top"),
            #dbc.Tooltip("Delta depending on the chosen scenario", target="hype-meter-delta", id="tooltip-equity-text", placement="top"),
            dbc.Tooltip("Hype: $4.0B", target="hype-meter-hype", id='hype-tooltip-hype', placement="top"),
        ],
    style={"height": "30px", "border-radius": "30px"},
)

hype_meter_example = dbc.Progress(
    children=
        [
            dbc.Progress(value=30, color="#228BE6", bar=True, label="N-O Assets", id="hype-meter-noa-ex"),
            dbc.Progress(value=40, color="#74C0FC", bar=True, label="Customer Equity", id="hype-meter-users-ex"),
            dbc.Progress(value=30, color="#D1D1D1", bar=True, animated=True, striped=True, label="Hype", id="hype-meter-hype-ex"),
            dbc.Tooltip("Non-Operating Assets: $3.0B", target="hype-meter-noa-ex", placement="top"),
            dbc.Tooltip("Customer Equity: $3.0B", target="hype-meter-users-ex", placement="top"),
            #dbc.Tooltip("Delta depending on the chosen scenario", target="hype-meter-delta", id="tooltip-equity-text", placement="top"),
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
            #mb="xs",
        ),
        dmc.Space(h=20),
        dmc.Text(
            #id="hype-meter-text",
            children=[dmc.List([
                    dmc.ListItem([dmc.Text("Dataset Selection", weight=500),
                                  "Quickly choose your dataset from the dropdown menu. We are continuously adding new "
                                  "datasets."]),
                    dmc.ListItem([dmc.Text("Historical Data Visualization", weight=500),
                                  "Dive into your selected dataset's past performance, unveiling growth trends "
                                  "over time."]),
                    dmc.ListItem([dmc.Text("Predictive Analysis", weight=500),
                                  "Harness Groowt's advanced predictive capabilities to forecast future dataset "
                                  "growth."]),
                ], size="sm", listStyleType="decimal")]
                      ,
            size="xs",
            color="Black",
            #style={'display':'inline-block'}
        ),
    ],
    #id="hype-meter-card",
    #style={'display': 'none'},
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
            #mb="xs",
        ),
        dmc.Space(h=20),
        dmc.Text("Methodology", size="sm", weight=700),
        dmc.Space(h=5),
        dmc.Text("In user-dependent companies, their value is tied to the number of users and the revenue each "
                         "user generates. The total worth, known as 'Customer Equity', combines current and future "
                         "value. To calculate the overall company value, add non-operating assets and subtract debt: "
                         , size="sm"),
        dmc.Text("Company Value = Non-Operating Assets + Customer Equity - Debt", align="center", size="sm", weight=500),
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
                              "the hype exceeds 20% of the total value."]),
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
    #style={'display':'inline-block'}
    #id="hype-meter-card",
    #style={'display': 'none'},
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
                    " Meet GROOWT, your go-to tool for determining the intrinsic"
                    "value of publicly traded Tech companies.", size="sm"),
                dmc.Space(h=15),
                offcanvas_card_growth_analysis,
                dmc.Space(h=15),
                offcanvas_card_valuation_analysis,
                dmc.Space(h=15),
                dmc.Text("We're continually adding new datasets & functionalities. Interested in specific datasets or have "
                         "a feature request? Drop us a line! 🚀 groowt@proton.me.", size="sm"),
                #dmc.Group(hype_meter_indicator_progress),
            ]
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

app_button = dmc.Button(
    id="app-button",
    children="APP",
    leftIcon=DashIconify(icon="fluent:app-title-24-regular"),
    size="xs",
    variant="gradient",
    gradient={"from": "cyan", "to": "blue"},
    #color="white",
    #color.title(white).
        ),

navbar6 = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row([
                    dbc.Col(html.Img(src="/assets/Vector_white.svg", height="25px")),
                    dbc.Col(dbc.NavbarBrand("GROOWT", className="ms-2", href='/'))
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
                    #target="_blank"
                )

            ),
            offcanvas,
            #dbc.DropdownMenu(
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
            #),
        ],
        brand=[html.Img(src="/assets/Vector_white.svg", height="25px"), '   GROOWT'],
        brand_href="/",
        # sticky="top",  # Uncomment if you want the navbar to always appear at the top on scroll.
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
                        #minDate=date(2020, 8, 5),
                        #inputFormat="MMMM,YY",
                        #dropdownType="modal",
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
    #value=["growth"],
    #variant="separated",
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
    #hide="False",
    withCloseButton="True")

# Graph message
valuation_graph_message = dmc.Alert(
    dmc.Text("About the Current Market Cap"),
    id="valuation-graph-message",
    title="About the Current Market Cap",
    color="blue",
    #hide="False",
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
        dmc.Text("Are you a Tech investor, journalist or simply curious about tech valuation? We got you."
                    " Meet GROOWT, your go-to tool for predicting dataset growth and determining the "
                    "value of publicly traded Tech companies.", color="blue", size="sm", mb="sm", weight=300),
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
                        "For publicly traded user-based companies, assess whether their current valuation is justified"
                        "or strongly 'hyped'",
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

main_graph = dcc.Graph(id='main-graph1', config={'displayModeBar': False, 'scrollZoom': True})


# Graph that contains the valuation calculation over time
valuation_over_time = html.Div(children=[dcc.Graph(id='valuation-graph', config={'displayModeBar': False,
                                                                                 'scrollZoom': True})])

# Tabs
tabs_graph = dmc.Tabs(
    [
        dmc.TabsList(
            #grow=True,
            children=
                [
                    dmc.Tab("Future Outlook", icon=DashIconify(icon="simple-icons:futurelearn"), value="1"),
                    dmc.Tab("Past Performance",
                            icon=DashIconify(icon="material-symbols:history"),
                            value="2",
                            #disabled=True
                            ),
                ],
        ),
        dmc.TabsPanel(html.Div(children=[graph_message, main_graph]),
            id="tab-one", value="1"),
        dmc.TabsPanel(html.Div(children=[valuation_graph_message, valuation_over_time]), id="tab-two", value="2"),
    ],
    value="1",
    variant="outline",
    #id='graph-card-content',
    #style={'display': 'none'}
)

source = dmc.Text(
        id= "data-source",
        children="Source",
        size="xs",
        color="dimmed",)

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
        dmc.Space(h=10),
        #html.Div(graph_message),
        dmc.Space(h=10),
        html.Div(tabs_graph),
        dmc.Space(h=10),
        html.Div(source),
        #html.Div(graph_message),
        # Card Content
        #html.Div(main_graph),
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
                dmc.Title("Hype Meter", order=5),
                hype_meter_indicator,
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
            children=["Adjust profit margin, discount rate, and ARPU to evaluate the company's current hype through its "
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
        yanchor="top",
        y=0.96,
        xanchor="left",
        x=0.01,
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

def layout():
    layout = html.Div([
        dmc.Container(fluid=True, children=[
            dmc.Grid([
                # dmc.Col(span=0.5, lg=0), # Empty left column
                dmc.Col(selector_card, span="auto", order=1),
                dmc.Col([
                    dmc.LoadingOverlay(graph_card),
                    # valuation_over_time_card  # Comment this line to remove the analysis graphs
                ], span=12, lg=6, orderXs=3, orderSm=3, orderLg=2),
                dmc.Col([hype_meter_card, dmc.Space(h=20), functionalities_card], span=12, lg=3, orderXs=2, orderSm=2,
                        orderLg=3),
                # dmc.Col(span="auto", lg=0), # Empty right column
            ],
                gutter="xl",
                justify="space-around",
                # align="center",
            ),
            dmc.Space(h=1000),
        ],
                      ),

        dbc.Container(children=[
            # Storing the key dataframe with all parameters
            dcc.Store(id='users-data'),
            dcc.Store(id='users-dates-raw'),  # DF containing the initial users/dates from the API
            dcc.Store(id='users-dates-formatted'),  # DF containing the users & dates in float for computation
            dcc.Store(id='scenarios-sorted'),  # DF containing all the possible growth scenarios
            dcc.Store(id='current-market-cap'),
            # Market cap of the company selected, 0 if N/A at the relative current time (depending on the date picked)
            dcc.Store(id='latest-market-cap'),  # Market cap of the company at the absolute current time (now)
            dcc.Store(id='graph-unit'),  # Graph unit (MAU, Population, etc.)
            dcc.Store(id='launch-counter', data={'flag': False}),
            # Counter that shows 0 if no dataset has been selected, or 1 otherwise
            dcc.Store(id='revenue-dates'),  # DF Containing the quarterly revenue and the dates
            dcc.Store(id='current-arpu-stored'),  # DF Containing the current ARPU
            dcc.Store(id='total-assets'),  # DF Containing the current total assets of the company
            dcc.Store(id='users-revenue-correlation'),  # R^2 indicating the strength of the correlation between the KPI
            # used and the revenue
            # dcc.Store(id='data-source'),  # sources of the data
            dcc.Store(id='data-selection-counter', data={'flag': False}),
            # Counter that shows if a new dataset has been selected
            dcc.Store(id='initial-sliders-values'),
            dcc.Store(id='current-valuation-calculated'),
            # Current valuation calculated with the current parameters and date
            # Counter that shows if a new dataset has been selected


        ], fluid=True),
    ])
    return layout