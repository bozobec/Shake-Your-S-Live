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

login_overlay_chart = dmc.Group(
    id="login-overlay-chart",
    children=[
        dmc.Stack(
            [
                dmc.Text(
                    children=[
                        "Are you a ",
                        dmc.Anchor(
                            dmc.Text(
                                "pro",
                                fw=900,
                                span=True,
                            ),
                            target="_blank",
                            underline="not-hover",
                            href="/pricing",
                            c="#FFA8FA",
                        ),
                        " member yet?",
                        html.Br(),
                        "Because if you are, you can access our quadrant mapping all of our companies.",
                    ],
                    fw=700,
                    size="xl",
                    c="white",
                    ta="center",
                    span=False,
                ),
                html.Img(
                    src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDBxOGdmdHVuZW9ybzN6d2dzajJhdnplcj"
                        "UwNHptZ3RkZDZ4Y3BjYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/uyWTOgNGGWfks/giphy.gif",
                    style={
                        "width": "200px",
                        "height": "233px",
                        "margin": "0 auto",
                        "display": "block"
                    }
                ),
            ],
            gap="xl",
            align="center",
            justify="center",
            style={"height": "100%"}
        )
    ],
    style={
        "display": "none",
        "position": "absolute",
        "top": 0,
        "left": 0,
        "width": "100%",
        "height": "100%",
        "backgroundColor": "rgba(0, 0, 0, 0.6)",
        "zIndex": 5,
        "backdropFilter": "blur(2px)",
    },
    align="center",
    justify="center"
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
    dmc.Stack([
        dmc.Title("RAST Quadrant", order=5),
        dmc.Text(
            "The exhaustive list of companies that we analyze, mapped in our magic quadrant. 'Undervalued gems' are the "
            "companies that are undervalued and have growth potential. 'Bubble zone' is the zone to avoid: they are overvalued"
            "and have limited growth potential. 'Hot & Hyped' are overvalued companies that have an strong growth, "
            "meaning that the overvaluation can last for a while.",
            size="xs",
            c="dimmed",
        ),
        ],
        justify="left",
        mt="md",
        mb="xs",
    ),
    dcc.Graph(id='hyped-ranking-graph', config=config_graph_with_toolbar),
    login_overlay_chart,
    ],
    withBorder=True, shadow='lg', radius='md', id='section-9')