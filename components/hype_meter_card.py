import dash_mantine_components as dmc
from dash import Dash, html, dcc, callback, dash_table
import dash_bootstrap_components as dbc

hype_meter_indicator = dmc.Badge("Super hyped", variant="outline", color="red", id="hype-meter-indicator")

line = html.Div(
    style={
        "height": "20px",
        "borderLeft": "2px dotted black",
        "marginLeft": "auto",
        "marginBottom": 0,
        "marginTop": 0
    }
)

line_middle = html.Div(
    style={
        "height": "20px",
        "borderLeft": "2px dotted black",
        "marginRight": "auto",
        "marginBottom": 0,
        "marginTop": 0
    }
)

# Hype meter progress bars
hype_meter_bootstrap = dbc.Progress(
    children=[
        dbc.Progress(value=10, color="#C58400", bar=True, label="N-O Assets", id="hype-meter-noa"),
        dbc.Progress(value=10, color="#FFD000", bar=True, label="Intrinsic value", id="hype-meter-users"),
        dbc.Progress(value=10, color="white", bar=True, animated=True, striped=True, label="Hype", id="hype-meter-hype"),
        dbc.Tooltip("Non-Operating Assets: $3.0B", target="hype-meter-noa", id='hype-tooltip-noa', placement="top"),
        dbc.Tooltip("Intrinsic value: $3.0B", target="hype-meter-users", id='hype-tooltip-users', placement="top"),
    ],
    style={"height": "30px", "borderRadius": "0px"},
)

hype_meter_bootstrap_undervaluation = dbc.Progress(
    children=[
        dbc.Progress(value=91.1025, color="white", bar=True, id="hype-meter-undervaluation-rest"),
        dbc.Progress(value=8.8975, color="#FFD000", bar=True, striped=True, id="hype-meter-undervaluation-hype"),
        dbc.Tooltip("Hype: $4.0B", target="hype-meter-undervaluation-hype", id='hype-tooltip-hype', placement="top"),
    ],
    style={"height": "10px", "borderRadius": "0px"},
)

hype_meter_bootstrap_price = dbc.Progress(
    children=[
        dbc.Progress(value=100, color="#953AF6", bar=True, label="Current price", id="hype-meter-price"),
        dbc.Progress(value=0, color="white", bar=True, label="Current price", id="hype-meter-price-rest"),
    ],
    style={"height": "30px", "borderRadius": "0px"},
)

# Valuation message (left side)
valuation_message = dmc.Alert(
    children=[
        dmc.Text(
            "This analysis shows the relationship between market cap, intrinsic value, and hype. "
            "Adjust the parameters to see how they affect the overall valuation.",
            size="sm",
            id="valuation-content"
        ),
        dmc.Space(h="xs"),
        dmc.List(
            [
                dmc.ListItem("Hype score, base case = 0.98", id="hype-score-text"),
                dmc.ListItem("Growth score", id="growth-score-text"),
            ],
            size="sm",
            spacing="xs",
        ),
    ],
    id="valuation-message",
    title="Valuation Overview",
    color="blue",
    variant="light",
    icon=dmc.Text("💡", size="xl"),
    #style={"height": "100%"},
)

# Hype meter visualization (right side)
hype_meter_visualization = dmc.Stack(
    children=[
        dmc.Stack([
            dmc.Text("Overvaluation", size="xs", fw=500, ta="right", id="hype-overvaluation-label", m=0),
            line,
            hype_meter_bootstrap_undervaluation,
            hype_meter_bootstrap,
            hype_meter_bootstrap_price,
            line_middle,
            dmc.Group([
                dmc.Text("Market cap = $10.1B", size="xs", fw=500, ta="left", id="hype-market-cap"),
                html.Img(id='company-logo',
                         src='',
                         style={
                             'height': '20px',  # Fixed height
                             'width': 'auto',  # Width adjusts automatically to maintain aspect ratio
                             'display': 'block',  # Prevents inline spacing issues
                             # 'marginTop': '20px',
                             'maxWidth': '100%',  # Prevents overflow in smaller containers
                             'objectFit': 'contain'  # Ensures the image is scaled inside the box
                         }
                         ),
                ],
                justify="space-between"
            )
        ],
        align="stretch",
        gap="xs"
        )
    ],
    gap="md"
)

# Main card

hype_meter_card = dmc.Card(
    children=[
        # Title and subtitle at the top
        dmc.Stack(
            [
                dmc.Group(
                    [
                        dmc.Title("in short", id="summary-card-title", order=5),
                        hype_meter_indicator,
                    ],
                    justify="space-between",
                ),
                dmc.Text(
                    "Select a dataset first",
                    id="company-info-text",
                    size="xs",
                    c="dimmed",
                    style={
                        "@media (max-width: 768px)": {"display": "none"},  # hides on small screens
                    },
                ),
            ],
            gap="xs",
            #mt="xs",
            mb="xs",
        ),
        # Two-column layout: Alert on left, Hype meter on right
        dmc.Grid(
            children=[
                # Left column: Alert message
                dmc.GridCol(
                    valuation_message,
                    span={"base": 12, "sm": 4, "md": 4},
                ),
                # Right column: Hype meter visualization
                dmc.GridCol(
                    hype_meter_visualization,
                    span={"base": 12, "sm": 8, "md": 8},
                ),
            ],
            gutter="lg",
        ),
    ],
    id="section-1",
    withBorder=True,
    shadow="sm",
    radius="md",
    p="xl",
    #style={'display': 'none'}
)