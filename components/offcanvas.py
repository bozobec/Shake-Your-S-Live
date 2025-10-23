import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from components.base_card import base_card
from dash import html

hype_meter_example = dbc.Progress(
    children=
    [
        dbc.Progress(value=30, color="#953AF6", bar=True, label="N-O Assets", id="hype-meter-noa-ex"),
        dbc.Progress(value=40, color="#F963F1", bar=True, label="Customer Equity", id="hype-meter-users-ex"),
        dbc.Progress(value=30, color="#FFD000", bar=True, animated=True, striped=True, label="Hype",
                     id="hype-meter-hype-ex"),
        dbc.Tooltip("Non-Operating Assets: $3.0B", target="hype-meter-noa-ex", placement="top"),
        dbc.Tooltip("Customer Equity: $3.0B", target="hype-meter-users-ex", placement="top"),
        # dbc.Tooltip("Delta depending on the chosen scenario", target="hype-meter-delta", id="tooltip-equity-text", placement="top"),
        dbc.Tooltip("Hype: $4.0B", target="hype-meter-hype-ex", placement="top"),
    ],
    style={"height": "30px", "borderRadius": "30px"},
)

offcanvas_card_growth_analysis = base_card(
    "Valuation in 3 steps",
    children=[
        dmc.Text(
            children=[
                dmc.List(
                    [
                        dmc.ListItem([
                            dmc.Text("Select your company", fw=500),
                            "Pick one of the available publicly-traded companies. For each company, a key revenue driver "
                            "has been selected (such as Subscribers for Spotify). In cases where no clear revenue driver exists (e.g. Amazon), "
                            "the headcount is used as a proxy.",
                        ]),
                        dmc.ListItem([
                            dmc.Text("The calculation", fw=500),
                            "We predict the key revenue driver's future growth (it follows most of the time a S-curve). "
                            "The cashflow is then obtained by multiplying the key revenue driver by the revenue per user/unit (see tab 'Revenue'). "
                            "Once we have the current and future cashflow, we apply a simple DCF to calculate the company's current value.",
                        ]),
                        dmc.ListItem([
                            dmc.Text("Analyze", fw=500),
                            "The valuation tab shows how we predicted the company's value over time (using always "
                            "the same method, not knowing what happens in the future). You can observe that the market "
                            "cap ends up most of the timecoming back to our confidence interval.",
                        ]),
                    ],
                    size="sm",
                    listStyleType="decimal",
                )
            ],
            size="xs",
            c="Black",
        ),
    ],
)

offcanvas_card_valuation_analysis = base_card(
    title="Methodology & Parameters",
    children=[
        dmc.Text("Hypemeter", size="sm", fw=700),
        dmc.Space(h=5),
        dmc.Text(
            "Get a quick read on a company's hype level. A company is considered Super Hyped when "
            "the hype exceeds 20% of the total value.",
            size="sm",
        ),
        dmc.Space(h=5),
        dmc.Group(
            [
                dmc.Badge("", variant="outline", color="green"),
                dmc.Badge("", variant="outline", color="yellow"),
                dmc.Badge("", variant="outline", color="orange"),
                dmc.Badge("Super Hyped!", variant="filled", color="red"),
            ],
            gap="sm",
        ),
        dmc.Space(h=10),
        dmc.Text(
            "The value of user-dependant companies is tied to the number of users and the revenue each "
            "user generates. The total worth, known as 'Customer Equity', combines current and future "
            "value. To calculate the overall company value, add non-operating assets and subtract debt:",
            size="sm",
        ),
        dmc.Space(h=5),
        dmc.Text(
            "Company Value = Non-Operating Assets + Customer Equity - Debt",
            ta="center",
            size="sm",
            fw=500,
        ),
        dmc.Space(h=5),
        dmc.Text(
            "Comparing this value to the market cap reveals investor sentiments, showing how much "
            "'hope' or 'hype' surrounds the company. In the example below, we observe that the hype "
            "accounts for 30% of the company's current valuation. This suggests that unless there's "
            "a notable enhancement in its business model, there's a high likelihood that the value "
            "may decrease.",
            size="sm",
        ),
        dmc.Space(h=10),
        hype_meter_example,
        dmc.Space(h=15),
        dmc.Text("Parameters", size="sm", fw=700),
        dmc.Space(h=5),
        dmc.Text(
            children=[
                dmc.List(
                    [
                        dmc.ListItem(
                            [
                                dmc.Text("Hypemeter", fw=500),
                                "Get a quick read on a company's hype level...",
                                dmc.Group(
                                    [
                                        dmc.Badge("", variant="outline", color="green"),
                                        dmc.Badge("", variant="outline", color="yellow"),
                                        dmc.Badge("", variant="outline", color="orange"),
                                        dmc.Badge("Super Hyped!", variant="filled", color="red"),
                                    ],
                                    gap="sm",
                                ),
                            ]
                        ),
                        dmc.ListItem(
                            [
                                dmc.Text("Growth Forecast", fw=500),
                                "Slide through different growth scenarios correlating stronger growth "
                                "with higher future value and current valuation.",
                            ]
                        ),
                        dmc.ListItem(
                            [
                                dmc.Text("Profit Margin", fw=500),
                                "Evaluate a company's value by considering its profit margin...",
                            ]
                        ),
                        dmc.ListItem(
                            [
                                dmc.Text("Discount Rate", fw=500),
                                "Factor in future uncertainties with the discount rate...",
                            ]
                        ),
                        dmc.ListItem(
                            [
                                dmc.Text("Revenue (ARPU) Yearly Growth", fw=500),
                                "Influence the customer equity by changing the growth of the annual "
                                "average revenue generated per user (ARPU).",
                            ]
                        ),
                    ],
                    size="sm",
                    listStyleType="decimal",
                )
            ],
            size="xs",
            c="Black",
        ),
    ],
)

# OffCanvas (side panel that opens to give more information)
offcanvas = html.Div(
    [
        #dbc.Button("How it works", id="open-offcanvas", n_clicks=0, color="dark"),
        dmc.Button("How it works", id="open-offcanvas", n_clicks=0, variant="transparent"),
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
            ]
            ),
        ],
            id="offcanvas",
            title="Welcome to RAST",
            is_open=False,
        ),
    ]
)