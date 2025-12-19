import dash_mantine_components as dmc
from dash import html, dcc
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
        dbc.Progress(value=10, color="#953BF6", bar=True, label="Intrinsic value", id="hype-meter-users"),
        dbc.Progress(value=10, color="white", bar=True, animated=True, striped=True, label="Hype",
                     id="hype-meter-hype"),
        dbc.Tooltip("Non-Operating Assets: $3.0B", target="hype-meter-noa", id='hype-tooltip-noa', placement="top"),
        dbc.Tooltip("Intrinsic value: $3.0B", target="hype-meter-users", id='hype-tooltip-users', placement="top"),
    ],
    style={"height": "30px", "borderRadius": "0px"},
    className="hype-meter-progress",
)

hype_meter_bootstrap_undervaluation = dbc.Progress(
    children=[
        dbc.Progress(value=91.1025, color="white", bar=True, id="hype-meter-undervaluation-rest"),
        dbc.Progress(value=8.8975, color="#FFD000", bar=True, striped=True, id="hype-meter-undervaluation-hype"),
        dbc.Tooltip("Hype: $4.0B", target="hype-meter-undervaluation-hype", id='hype-tooltip-hype', placement="top"),
    ],
    style={"height": "15px", "borderRadius": "0px"},
    className="hype-meter-progress",
)

hype_meter_bootstrap_price = dbc.Progress(
    children=[
        dbc.Progress(value=100, color="#9F9F9E", bar=True, label="Current price", id="hype-meter-price"),
        dbc.Progress(value=0, color="white", bar=True, label="Current price", id="hype-meter-price-rest"),
        dbc.Tooltip("Price: $4.0B", target="hype-meter-price", id='hype-tooltip-price', placement="bottom"),
    ],
    style={"height": "30px", "borderRadius": "0px"},
    className="hype-meter-progress",
)

config_graph_with_toolbar = {
    'displayModeBar': False,
    'scrollZoom': False,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['zoom', 'zoomIn', 'zoomOut', 'pan', 'lasso', 'select', 'autoScale', 'resetScale'],
    'toImageButtonOptions': {
        'format': 'svg',  # one of png, svg, jpeg, webp
        'filename': 'RAST_Growth',
        'height': 735,
        'width': 1050,
        'scale': 1  # Multiply title/legend/axis/canvas sizes by this factor
    },
}

# Valuation message (left side)
valuation_message = dmc.Alert(
    children=[
        dmc.Text(
            dmc.Skeleton(height=8, radius="xl"),
            size="sm",
            id="valuation-content"
        ),
        dmc.Space(h="xs"),
        dmc.List(
            [
                dmc.ListItem(dmc.Skeleton(height=8, w="70%", radius="xl"), id="hype-score-text"),
                dmc.ListItem(dmc.Skeleton(height=8, w="70%", radius="xl"), id="growth-score-text"),
            ],
            size="sm",
            spacing="xs",
        ),
        dmc.Space(h="xs"),
        dmc.Text(
            dmc.Skeleton(height=8, w="70%", radius="xl"),
            size="sm",
            id="growth-content"
        )
    ],
    id="valuation-message",
    title=dmc.Skeleton(height=8, w="70%", radius="xl"),
    color="blue",
    variant="light",
    icon=dmc.Text("💡", size={"base": "xs", "sm": "xl"}),
    p={"base": "xs", "sm": "md"},  # ⬅ smaller padding on mobile
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

card_dashboard = dmc.Group(
    id='card-dashboard',
    # style={'display': 'none'},
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
                    wrap="nowrap",
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
            mb="xs",
        ),
        # Two-column layout: Alert on left, Hype meter on right
        dmc.Grid(
            children=[
                # Left column: Alert message
                dmc.GridCol(
                    valuation_message,
                    span={"base": 12, "sm": 8, "md": 8},
                ),
                # Right column: Hype meter visualization
                dmc.GridCol(
                    hype_meter_visualization,
                    span={"base": 12, "sm": 4, "md": 4},
                ),
                dmc.Loader(
                    color="red",
                    size="md",
                    variant="oval",
                    style={"display": "none"},
                    id="loader-general",
                ),
            ],
            gutter="lg",
        ),
    ]
)

# Card containing the welcome components when no company is selected

hype_meter_card = dmc.Card(
    children=[
        dcc.Loading(card_dashboard,
                    overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                    type="circle",
                    color="black"
                    ),
    ],
    id="section-1",
    withBorder=True,
    shadow="sm",
    radius="md",
    p={"base": "sm", "sm": "xl"},  # smaller padding on mobile
    m={"base": 5, "sm": "md"},  # tighter outer margin on mobile
)
