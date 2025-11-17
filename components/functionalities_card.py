from dash import Dash, html, dcc, callback, dash_table
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from datetime import date

# Scenario picker
data_scenarios = ["Worst", "Base", "Best", "Nerd mode"]

# Date picker
today = date.today().isoformat()  # 'YYYY-MM-DD'

scenarios_picker = dmc.SegmentedControl(
        data=data_scenarios,
        value="Base",
        fullWidth=True,
        color="#953AF6",
        radius=20,
        id="scenarios-picker")

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

datepicker = html.Div(
                [
                    dmc.DatePickerInput(
                        id="date-picker",
                        value=today,
                        #minDate=date(2020, 8, 5),
                        #inputFormat="MMMM,YY",
                        #dropdownType="modal",
                        clearable=False,
                    ),
                ]
            )

functionalities_card = dmc.Card(
    children=[
        dmc.Group(
            [
                dmc.Title("Scenarios analysis", order=5),
                dmc.Text(
                    "Toggle between the worst/best case scenarios to see how the valuation evolves, or choose your own"
                    " parameters with the nerd mode.",
                    size="xs",
                    c="dimmed",
                    style={
                        "@media (max-width: 768px)": {"display": "none"},  # hides on small screens
                    },
                ),
            ],
            #justify="space-around",
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

        # Div wrapping all sliders

        html.Div(
            id='all-sliders',
            style={"display": "none"},
            children=[
                html.Div(
                    children=[
                        dmc.Space(h=10),
                        # Plateau slider
                        dmc.Group([
                            dmc.Text(
                                "Growth Forecast",
                                size="sm",
                                fw=700,
                                ),
                            dmc.Tooltip(
                                children=DashIconify(icon="feather:info", width=15),
                                label="Select 'Custom' to move the blue curve and see how well it fits the dataset. "
                                      "The star indicates RAST's best prediction",
                                transitionProps={
                                        "transition": "slide-down",
                                        "duration": 300,
                                    },
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
                            gap="md"),
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
                                    fw=700,
                                    ),
                                dmc.Tooltip(
                                    children=DashIconify(icon="feather:info", width=15),
                                    label="Adjust the profit margin using the slider to observe the impact on the company's "
                                          "annual average revenue per user. Increasing the profit margin increases the company's"
                                          " profit and therefore the company's value. MAX indicates the maximum theoretical"
                                          " net profit margin for this company given its current business model",
                                    transitionProps={
                                            "transition": "slide-down",
                                            "duration": 300,
                                        },
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
                            c="dimmed",
                            ),
                        dmc.Text(
                            "Best annual profit margin ever: 45%",
                            id="best-profit-margin-container",
                            size="sm",
                            c="dimmed",
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
                            fw=700,
                        ),
                        dmc.Tooltip(
                            children=DashIconify(icon="feather:info", width=15),
                            label="Adjust the discount rate with the slider to match the risks in the company and its "
                                  "industry. Kroll research shows that, on average, the discount rate for consumer "
                                  "staples companies was 8.4% in June 2023, and for information technology companies, "
                                  "it was 11.4%. Raising the rate raises future uncertainty and requires a "
                                  "higher average revenue per user.",
                            transitionProps={
                                    "transition": "slide-down",
                                    "duration": 300,
                                },
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
                            fw=700,
                        ),
                        dmc.Tooltip(
                            children=DashIconify(icon="feather:info", width=15),
                            label="Adjust the yearly growth of the Average Revenue Per User for the next years. This"
                                  " changes the projected ARPU and therefore the value of future users",
                            transitionProps={
                                    "transition": "slide-down",
                                    "duration": 300,
                                },
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
                            fw=700,
                        ),
                        dmc.Tooltip(
                            children=DashIconify(icon="feather:info", width=15),
                            label="Depending on the profit margin & discount rate you choose, the required Average "
                                  "Annual Revenue per user (ARPU) is displayed below to justify the current valuation."
                                  "Comparing this to the actual current ARPU gives you a clear indication of whether the"
                                  " stock is over or undervalued.",
                            transitionProps={
                                    "transition": "slide-down",
                                    "duration": 300,
                                },
                            multiline=True,
                        ),
                        dmc.Text(
                            id="arpu-needed",
                            children="456$",
                            size="sm",
                            c="Black",
                        ),
                    ],),
                dmc.Space(h=10),
            ]),

        # Datepicker
        html.Div(
            children=[
                dmc.Tooltip(
                    children=dmc.Group([
                        dmc.Text(
                            "Retrospective Growth",
                            size="sm",
                            fw=700,
                            ),
                        DashIconify(icon="feather:info", width=15)
                        ],
                        gap="md"),
                    label="Pick a date in the past to see how well the current state would have been predicted back then",
                    transitionProps={
                                    "transition": "slide-down",
                                    "duration": 300,
                                },
                    multiline=True,
                ),
                dmc.Space(h=10),
                datepicker,
        ]),
            ]),
    ],
    id="functionalities-card",
    withBorder=True,
    shadow="sm",
    radius="md",
    style={'display': 'none'
           },
    #style={"height": 500},
)