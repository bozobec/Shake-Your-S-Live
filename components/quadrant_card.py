from dash import Dash, html, dcc, callback, dash_table
import dash_mantine_components as dmc
from dash_iconify import DashIconify


# Graph message growth rate
ranking_graph_message = dmc.Alert(
    dmc.Text("About the Discrete Growth Rate"),
    id="growth-rate-graph-message",
    title="When will the growth stop?",
    color="blue",
    #hide="False",
    withCloseButton="True")

login_overlay_chart = html.Div(
    id="login-overlay-chart",
    children=[
    dmc.Space(h=60),
    dmc.Text(
        "Log in to view our most undervalued companies.",
        fw=700,
        size="m",
        c="white",
        ta="center",
    )],
    style={
        "display": "none",  # Hidden by default
        "position": "absolute",  # Sit on top
        "top": 0,
        "left": 0,
        "width": "100%",
        "height": "100%",
        "backgroundColor": "rgba(0, 0, 0, 0.6)",
        "zIndex": 5,
        "backdropFilter": "blur(2px)",
    }
)

config_graph_with_toolbar = {
    'displayModeBar': True,
    'scrollZoom': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': [],
    'toImageButtonOptions': {
            'format': 'svg', # one of png, svg, jpeg, webp
            'filename': 'RAST_Growth',
            'height': 735,
            'width': 1050,
            'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
          },
}

quadrant_card = dmc.Card(children=[
    dmc.Group([
        dmc.Title("RAST Quadrant", order=5),
        ],
        justify="left",
        mt="md",
        mb="xs",
    ),
    dcc.Graph(id='hyped-ranking-graph', config=config_graph_with_toolbar),
    login_overlay_chart,
    ],
    withBorder=True, shadow='lg', radius='md', id='section-9')