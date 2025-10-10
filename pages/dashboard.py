from dash import html, register_page  #, callback # If you need callbacks, import it here.
# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import dash
import dash_mantine_components as dmc
from dash import Dash, html, dcc, callback, dash_table
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
import random
import dash_daq as daq
#from dash_extensions import DeferScript
from functools import lru_cache

register_page(
    __name__,
    name='RAST | APP Dashboard for user-based companies valuation',
    top_nav=True,
    path='/'
)


# Values for the dropdown (all different companies in the DB)
labels = dataAPI.get_airtable_labels()



# Constants for the calculation
YEAR_OFFSET = 1970  # The year "zero" for all the calculations
MIN_DATE_INDEX = 5  # Defines the minimum year below which no date can be picked in the datepicker
YEARS_DCF = 15 # Amount of years taken into account for DCF calculation

# ------------------------------------------------------------------------------------------------------------
# Components definition
# Dropdown - Taking data from "Labels"

dropdown6 = html.Div(
    [
        dmc.Select(
            # label="Select framework",
            placeholder="Company (and other)...",
            id="dataset-selection",
            data=labels,
            style={"marginBottom": 10},
            styles={"disabled": {
                "root": {
                "fontWeight": 800
                    }
                }
            },
            nothingFound="We don't have this company yet!",
            dropdownPosition="bottom",
            searchable=True,
            selectOnBlur=True,
            transition="pop",
            transitionDuration=200,
        )
    ]
)
# Upload field
upload_field = html.Div([dcc.Upload(
        id='upload-data',
        children=dmc.Button("Upload your own Dataset (CSV or XLS)", variant="outline", id='upload-button'),
        # Allow multiple files to be uploaded
        multiple=False
    ),
    ])

upload_modal = dmc.Modal(
            title="Uploaded data",
            id="upload-modal",
            overflow="inside",
            zIndex=10000,
            children=[
                dmc.Text("Verify that your data has been correctly uploaded"),
                dmc.Space(h=20),
                html.Div(id='output-data-upload'),
                dmc.Group(
                    [
                        dmc.Button("Submit", id="modal-submit-button"),
                        dmc.Button(
                            "Close",
                            color="red",
                            variant="outline",
                            id="modal-close-button",
                        ),
                    ],
                    position="right",
                ),
            ],
        )

download_graph_button = dmc.Button(
                            "Download Graph",
                            color="primaryPurple",
                            variant="outline",
                            id="download-graph-button",
                        ),

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
    style={"height": "5px", "borderRadius": "0px"},
)


# Hype meter
hype_meter_bootstrap = dbc.Progress(
    children=
        [
            dbc.Progress(value=10, color="#C58400", bar=True, label="N-O Assets", id="hype-meter-noa"),
            dbc.Progress(value=10, color="#FFD000", bar=True, label="Intrinsic value", id="hype-meter-users"),
            #dbc.Progress(value=20, color="#D1D1D1", bar=True, animated=True, striped=True, id="hype-meter-delta"),
            dbc.Progress(value=10, color="white", bar=True, animated=True, striped=True, label="Hype", id="hype-meter-hype"),
            dbc.Tooltip("Non-Operating Assets: $3.0B", target="hype-meter-noa", id='hype-tooltip-noa', placement="top"),
            dbc.Tooltip("Intrinsic value: $3.0B", target="hype-meter-users", id='hype-tooltip-users', placement="top"),
            #dbc.Tooltip("Delta depending on the chosen scenario", target="hype-meter-delta", id="tooltip-equity-text", placement="top"),
            dbc.Tooltip("Hype: $4.0B", target="hype-meter-hype", id='hype-tooltip-hype', placement="top"),
        ],
    style={"height": "30px", "borderRadius": "0px"},
)

hype_meter_bootstrap_undervaluation = dbc.Progress(
    children=
        [
            dbc.Progress(value=91.1025, color="white", bar=True, id="hype-meter-undervaluation-rest"),
            dbc.Progress(value=8.8975, color="#FFD000", bar=True, striped=True, id="hype-meter-undervaluation-hype"),
            #dbc.Progress(value=20, color="#D1D1D1", bar=True, animated=True, striped=True, id="hype-meter-delta"),
            #dbc.Progress(value=10, color="#FFD000", bar=True, animated=True, striped=True, label="Hype", id="hype-meter-hype"),
            #dbc.Tooltip("Non-Operating Assets: $3.0B", target="hype-meter-noa", id='hype-tooltip-noa', placement="top"),
            #dbc.Tooltip("Hype: $3.0B", target="hype-meter-users", id='hype-tooltip-users', placement="top"),
            #dbc.Tooltip("Delta depending on the chosen scenario", target="hype-meter-delta", id="tooltip-equity-text", placement="top"),
            #dbc.Tooltip("Hype: $4.0B", target="hype-meter-hype", id='hype-tooltip-hype', placement="top"),
        ],
    #style={"height": "30px", "borderRadius": "30px"},
    style={"height": "10px", "borderRadius": "0px"},
)

hype_meter_bootstrap_price = dbc.Progress(
    children=
        [
            dbc.Progress(value=100, color="#953AF6", bar=True, label="Current price", id="hype-meter-price"),
            dbc.Progress(value=0, color="white", bar=True, label="Current price", id="hype-meter-price-rest"),
            #dbc.Progress(value=8.8975, color="#FFD000", bar=True, label="Customer Equity"),
            #dbc.Progress(value=20, color="#D1D1D1", bar=True, animated=True, striped=True, id="hype-meter-delta"),
            #dbc.Progress(value=10, color="#FFD000", bar=True, animated=True, striped=True, label="Hype", id="hype-meter-hype"),
            #dbc.Tooltip("Non-Operating Assets: $3.0B", target="hype-meter-noa", id='hype-tooltip-noa', placement="top"),
            #dbc.Tooltip("Hype: $3.0B", target="hype-meter-users", id='hype-tooltip-users', placement="top"),
            #dbc.Tooltip("Delta depending on the chosen scenario", target="hype-meter-delta", id="tooltip-equity-text", placement="top"),
            #dbc.Tooltip("Hype: $4.0B", target="hype-meter-hype", id='hype-tooltip-hype', placement="top"),
        ],
    #style={"height": "30px", "borderRadius": "30px"},
    style={"height": "30px", "borderRadius": "0px"},
)

hype_meter_example = dbc.Progress(
    children=
        [
            dbc.Progress(value=30, color="#953AF6", bar=True, label="N-O Assets", id="hype-meter-noa-ex"),
            dbc.Progress(value=40, color="#F963F1", bar=True, label="Customer Equity", id="hype-meter-users-ex"),
            dbc.Progress(value=30, color="#FFD000", bar=True, animated=True, striped=True, label="Hype", id="hype-meter-hype-ex"),
            dbc.Tooltip("Non-Operating Assets: $3.0B", target="hype-meter-noa-ex", placement="top"),
            dbc.Tooltip("Customer Equity: $3.0B", target="hype-meter-users-ex", placement="top"),
            #dbc.Tooltip("Delta depending on the chosen scenario", target="hype-meter-delta", id="tooltip-equity-text", placement="top"),
            dbc.Tooltip("Hype: $4.0B", target="hype-meter-hype-ex", placement="top"),
        ],
    style={"height": "30px", "borderRadius": "30px"},
)



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



# Sliders
slider = html.Div(children=[dcc.RangeSlider(id="range-slider-data-ignored1", min=0, step=1,
                                                               marks={},
                                                               value=[0],
                            tooltip={"placement": "bottom", "always_visible": True},
                                            vertical=True),
                            html.Div(id="max-label")])


# Card that contains the regression
bottom_card = dbc.Card(id="bottom-card", children=[
                        html.Div(id='graph-container2', children=[dcc.Graph(id='main-graph2')])
                      ],
                       #style={'display': 'none'}
                       )
# Card that contains the evolution of R square and RMSD
bottom_bottom_card = dbc.Card(id="bottom-bottom-card", children=[
                        html.Div(id='graph-container3', children=[dcc.Graph(id='main-graph3')])
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
            value=10,
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
            max=15,
            value=2,
            step=0.1,
            color='green',
            marks=[
                {"value": 0, "label": "0%"},
                {"value": 5, "label": "5%"},
                {"value": 10, "label": "10%"},
                {"value": 15, "label": "15%"},
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

# Product Maturity
product_maturity_message = dmc.Alert(
    children=dmc.Text(""),
    id="product-maturity-message",
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
                    "Growth",
                    id="accordion-plateau",
                    disabled=True,
                    icon=DashIconify(icon="simple-icons:futurelearn", width=20)
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
                    "Revenue",
                    id="accordion-correlation",
                    disabled=True,
                    icon=DashIconify(icon="lineicons:target-revenue", width=20)
                ),
                dmc.AccordionPanel(
                    correlation_message
                ),
            ],
            value="correlation",
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl(
                    "Product Maturity",
                    id="accordion-product-maturity",
                    disabled=True,
                    icon=DashIconify(icon="fluent-mdl2:product-release", width=20)
                ),
                dmc.AccordionPanel(
                    product_maturity_message
                ),
            ],
            value="product-maturity",
        ),
    ],
)

# Graph message
graph_message = dmc.Alert(
    dmc.Text("About the graph"),
    id="graph-message",
    title="About the Growth Forecast",
    color="primaryPurple",
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

# Graph message
revenue_graph_message = dmc.Alert(
    dmc.Text("About the Average Revenue per User"),
    id="revenue-graph-message",
    title="About the Current Market Cap",
    color="blue",
    #hide="False",
    withCloseButton="True")

# Graph message growth rate
growth_rate_graph_message = dmc.Alert(
    dmc.Text("About the Discrete Growth Rate"),
    id="growth-rate-graph-message",
    title="About the Discrete Growth Rate",
    color="blue",
    #hide="False",
    withCloseButton="True")

# Graph message growth rate
product_maturity_graph_message = dmc.Alert(
    dmc.Text("About the Product Maturity"),
    id="product-maturity-graph-message",
    title="About the Product Maturity",
    color="blue",
    #hide="False",
    withCloseButton="True")


# Scenario picker
data_scenarios = ["Worst", "Base", "Best", "Custom"]

scenarios_picker = dmc.SegmentedControl(
        data=data_scenarios,
        value="Base",
        fullWidth=True,
        color="#953AF6",
        radius=20,
        id="scenarios-picker")

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
            "Select a company (or other dataset) to visualize its historical data and forecast its future growth.",
            size="xs",
            color="dimmed",
        ),
        dmc.Space(h=10),
        dropdown6,
        #upload_field,
        upload_modal,
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
                dmc.Title("Scenarios analysis", order=5),
            ],
            position="apart",
            mt="md",
            mb="xs",
        ),
        #dmc.Text(
        #    "See where data is heading and move the predicted growth (blue) easily. "
        #    "For companies, figure out if their worth makes sense right now.",
        #    size="xs",
        #    color="dimmed",
        #),
        #dmc.Space(h=10),
        dmc.Space(h=10),
        scenarios_picker,
        # Plateau slider
        html.Div(
            children=[
                dmc.Space(h=10),
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
                                  "annual average revenue per user. Increasing the profit margin increases the company's"
                                  " profit and therefore the company's value. MAX indicates the maximum theoretical"
                                  " net profit margin for this company given its current business model",
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
                dmc.Text(
                    "Best annual profit margin ever: 45%",
                    id="best-profit-margin-container",
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
# Welcome timeline introducing the user to RAST

welcome_timeline = html.Div([
    dmc.Timeline(
    active=0,
    bulletSize=25,
    lineWidth=2,
    id='welcome-timeline',
    children=[
        dmc.TimelineItem(
            title="Choose a company",
            bullet=DashIconify(icon="teenyicons:add-solid", width=12),
            #lineVariant="dashed",
            color="dimmed",
            children=[
                dmc.Text(
                    [
                        "Use the dropdown menu on the side to select a company. Visualize its valuation and growth.",
                        dmc.Anchor("", href="#", size="sm"),
                    ],
                    color="dimmed",
                    size="sm",
                ),
            ],
        ),
        dmc.TimelineItem(
            title="Explore growth and valuation",
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

config_graph = {
    'displayModeBar': True,
    'scrollZoom': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['zoom', 'zoomIn', 'zoomOut', 'pan', 'lasso', 'select','autoScale', 'resetScale'],
    'toImageButtonOptions': {
            'format': 'svg', # one of png, svg, jpeg, webp
            'filename': 'RAST_Growth',
            'height': 735,
            'width': 1050,
            'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
          },
}

main_graph = dcc.Graph(id='main-graph1', config=config_graph)
revenue_graph = dcc.Graph(id='revenue-graph', config=config_graph)
growth_graph = dcc.Graph(id='main-graph2', config=config_graph)
product_maturity_graph = dcc.Graph(id='product-maturity-graph', config=config_graph)


# Graph that contains the valuation calculation over time
valuation_over_time = html.Div(children=[dcc.Graph(id='valuation-graph', config=config_graph)])

# Tabs and related graphs
tabs_graph = dmc.Tabs(
    [
        dmc.Loader(color="red", size="md", variant="oval", style={'display': 'none'}, id='loader-general'),
        dmc.TabsList(
            #grow=True,
            children=
                [
                    dmc.LoadingOverlay(dmc.Tab("Valuation",
                                        icon=DashIconify(icon="radix-icons:rocket"),
                                        id="market-cap-tab",
                                        value="1",
                                        #disabled=True
                                        style={'display': ''},
                                        )),
                    dmc.Tab("Growth", icon=DashIconify(icon="simple-icons:futurelearn"), value="2"),
                    dmc.Tab("Revenue", icon=DashIconify(icon="lineicons:target-revenue"), value="5"),
                    dmc.Tab("Growth Rate",
                            icon=DashIconify(icon="radix-icons:bar-chart"),
                            value="3",
                            #disabled=True
                            ),
                    dmc.Tab("Product Maturity", icon=DashIconify(icon="fluent-mdl2:product-release"), value="4"),
                ],
        ),
        # Valuation graph
        dmc.TabsPanel(html.Div(children=[valuation_graph_message, valuation_over_time]), id="tab-two", value="1"),
        # User evolution graph
        dmc.TabsPanel(html.Div(children=[graph_message, main_graph]),
            id="tab-one", value="2"),
        # Revenue Graph
        dmc.TabsPanel(html.Div(children=[revenue_graph_message, revenue_graph]),
            id="tab-five", value="5"),
        # Growth Rate Graph
        dmc.TabsPanel(html.Div(children=[growth_rate_graph_message, growth_graph]), id="tab-three", value="3"),
        # Product Maturity Graph
        dmc.TabsPanel(html.Div(children=[product_maturity_graph_message, product_maturity_graph]), id="tab-four", value="4"),
    ],
    value="1",
    variant="pills",
    color='violet',
    id='tabs-component',
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
                        dmc.Title("Welcome to RAST", id="graph-title", order=5),
                        html.Img(id='company-logo',
                                 src='',
                                 style={
                                     'height': '20px',  # Fixed height
                                     'width': 'auto',  # Width adjusts automatically to maintain aspect ratio
                                     'display': 'block',  # Prevents inline spacing issues
                                     #'marginTop': '20px',
                                     'maxWidth': '100%',  # Prevents overflow in smaller containers
                                     'objectFit': 'contain'  # Ensures the image is scaled inside the box
                                 }
                                 )
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

hype_score_gauge = html.Div([
            daq.Gauge(
                id='my-gauge-1',
                color={"gradient":False,"ranges":{"teal":[-1,0],"green":[0,1],"yellow":[1,1.5],"orange":[1.5,2.5],"red":[2.5,3]}},
                showCurrentValue=True,
                #label="Hype score",
                size=180,
                min=-1,
                max=3,
                value=0
             )])

line = html.Div(
            style={
                #"width": "2px",
                "height": "20px",
                #"backgroundColor": "black",
                "borderLeft": "2px dotted black",
                "marginLeft": "auto",
                "marginBottom": 0,   # remove bottom margin
                "marginTop": 0   # remove bottom margin
            }
        )
line_middle = html.Div(
            style={
                #"width": "2px",
                "height": "20px",
                #"backgroundColor": "black",
                "borderLeft": "2px dotted black",
                "marginRight": "auto",
                "marginBottom": 0,   # remove bottom margin
                "marginTop": 0   # remove bottom margin
            }
        )

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
            noWrap=True,
        ),
        #hype_meter,
        dmc.Stack([
                dmc.Text("Hype score, base case = 0.98", size="xs", weight=500, align="left", id="hype-score-text", m=0),
                dmc.Text("Overvaluation", size="xs", weight=500, align="right", id="hype-overvaluation-label", m=0),
                line,
                hype_meter_bootstrap_undervaluation,
                hype_meter_bootstrap,
                hype_meter_bootstrap_price,
                line_middle,
                dmc.Text("Market cap = $10.1B", size="xs", weight=500, align="left", id="hype-market-cap"),
                #hype_score_gauge,
            ],
            align="stretch",
            spacing="xs"
        ),
        dmc.Space(h=20),
        dmc.Text(
            id="hype-meter-text",
            children=["Adjust profit margin, discount rate, and ARPU to change the company's current Hype.",
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

aside_column = dmc.Aside(
    p="md",
    width={"base": 400},
    withBorder=False,
    hidden=True,
    hiddenBreakpoint='md',
    #height=500,
    fixed=True,
    #position={"right": 0, "top": 400},
    children=[
        hype_meter_card,
        functionalities_card,
    ],
)

navbar_column = dmc.Navbar(
    p="md",
    width={"base": 400},
    withBorder=False,
    hidden=True,
    hiddenBreakpoint='md',
    #height=500,
    fixed=True,
    #position={"right": 0, "top": 400},
    children=[
        selector_card,
    ],
)

# Table

# Sample DataFrame
companies = pd.DataFrame({
    "Company Name": ["Company A", "Company B", "Company C", "Company D", "Company E"],
    "Hype Score": [90, 20, 60, 95, 85]  # Higher score means more hype
})


table_hype = dmc.Card(children=[
    dmc.Group([
        dmc.Title("RAST Ranking", order=5),
            dmc.MultiSelect(
                    #label="Select the companies that you want to see",
                    placeholder="Filter by industry",
                    id="hyped-table-industry",
                    #description="You can select up to 3 industries.",
                    #value="All",
                    data=[
                        {"value": "most-hyped", "label": "Most hyped"},
                        {"value": "least-hyped", "label": "Least hyped"},
                    ],
                    clearable=True,
                    maxSelectedValues=3,
                    #w=350,
                    mb=10,
                    icon=DashIconify(icon="mdi-light:factory"),
                ),
        dmc.Select(
                    #label="Select the companies that you want to see",
                    placeholder="Most or least hyped companies",
                    id="hyped-table-select",
                    value="least-hyped",
                    data=[
                        {"value": "most-hyped", "label": "Most hyped"},
                        {"value": "least-hyped", "label": "Least hyped"},
                    ],
                    w=200,
                    mb=10,
                    allowDeselect=False,
                ),
        ],
        position="apart",
        mt="md",
        mb="xs",
    ),
    dmc.ScrollArea(
        h=400,
        children=[
            dmc.Table(id='top_25_companies')
        ]
    ),
], withBorder=True, shadow='lg', radius='md')

graph_hype = dmc.Card(children=[
    dmc.Group([
        dmc.Title("RAST Quadrant", order=5),
        ],
        position="apart",
        mt="md",
        mb="xs",
    ),
    dcc.Graph(id='hyped-ranking-graph', config=config_graph),
], withBorder=True, shadow='lg', radius='md')





def layout(company=None, **other_unknown_query_strings):
    layout =html.Div([
            dmc.Container(fluid=True, children=[
                dmc.Grid([
                    # dmc.Col(span=0.5, lg=0), # Empty left column
                    dmc.Col(selector_card, span="auto", orderXs=1, orderSm=1, orderLg=1),
                    #dmc.Col(navbar_column, span="auto", order=1),
                    dmc.Col([
                        dmc.LoadingOverlay(graph_card), dmc.Space(h=20), dmc.LoadingOverlay(table_hype), dmc.Space(h=20),
                        dmc.LoadingOverlay(graph_hype)
                        # valuation_over_time_card  # Comment this line to remove the analysis graphs
                    ], span=12, lg=6, orderXs=2, orderSm=2, orderLg=2),
                    dmc.Col([hype_meter_card, dmc.Space(h=20), functionalities_card], span=12, lg=3, orderXs=3, orderSm=3,
                            orderLg=3),
                    #dmc.Col([aside_column], span=12, lg=3, orderXs=2, orderSm=2,
                    #               orderLg=3),
                    # dmc.Col(span="auto", lg=0), # Empty right column
                ],
                    gutter="xl",
                    justify="space-around",
                    # align="center",
                ),
                dmc.Space(h=20),
                #bottom_card,

            ],
                          ),

            dbc.Container(children=[
                # Storing the key dataframe with all parameters
                dcc.Store(id='users-data'),
                dcc.Store(id='users-dates-raw'),  # DF containing the initial users/dates from the API
                dcc.Store(id='users-dates-formatted'),  # DF containing the users & dates in float for computation
                dcc.Store(id='valuation-over-time'),  # DF containing the valuation over time for a given dataset
                dcc.Store(id='scenarios-sorted'),  # DF containing all the possible growth scenarios
                dcc.Store(id='current-market-cap'),
                # Market cap of the company selected, 0 if N/A at the relative current time (depending on the date picked)
                dcc.Store(id='latest-market-cap'),  # Market cap of the company at the absolute current time (now)
                dcc.Store(id='graph-unit'),  # Graph unit (MAU, Population, etc.)
                dcc.Store(id='symbol-dataset'),  # Symbol of the Public company (N/A if not)
                dcc.Store(id='launch-counter', data={'flag': False}),
                # Counter that shows 0 if no dataset has been selected, or 1 otherwise
                dcc.Store(id='revenue-dates'),  # DF Containing the quarterly revenue and the dates
                dcc.Store(id='current-arpu-stored'),  # DF Containing the current ARPU
                dcc.Store(id='total-assets'),  # DF Containing the current total assets of the company
                dcc.Store(id='users-revenue-correlation'),  # R^2 indicating the strength of the correlation between the KPI
                # used and the revenue
                # dcc.Store(id='data-source'),  # sources of the data
                dcc.Store(id='data-selection-counter', data={'flag': False}),
                dcc.Store(id='dataset-selected-url', data=str(company)), # stores the dataset given through the url through ?company={company}
                dcc.Store(id='dataset-selected'),  # stores the dataset selected either through the dropdown or the URL
                # Counter that shows if a new dataset has been selected
                dcc.Store(id='initial-sliders-values'),
                dcc.Store(id='current-valuation-calculated'),
                # Current valuation calculated with the current parameters and date
                # Counter that shows if a new dataset has been selected
                dcc.Store(id='last-imported-data'),
                dcc.Store(id='all-companies-information'),  # stores all the companies and the related information
                dcc.Store(id='max-net-margin'),  # stores the max theoretical net margin for the selected company
                dcc.Store(id='hype-score'),  # calculates the company's hype level that is used in the ranking
                html.Div(id='page-load-trigger'),  # Dummy trigger to launch a callback once the page loads
                dcc.Location(id='url', refresh=False)
            ], fluid=True),
        ]),

    return layout