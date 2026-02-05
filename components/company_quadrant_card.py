from dash import Dash, html, dcc, callback, dash_table
import dash_mantine_components as dmc
from dash_iconify import DashIconify



login_overlay_chart = html.Div(
    #id="login-overlay-chart",
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
        'scrollZoom': False,
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
    'scrollZoom': False,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['zoom', 'zoomIn', 'zoomOut', 'pan', 'lasso', 'select','autoScale', 'resetScale', 'toImage'],
    'toImageButtonOptions': {
            'format': 'svg', # one of png, svg, jpeg, webp
            'filename': 'RAST_Growth',
            'height': 735,
            'width': 1050,
            'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
          },
}

# Quadrant graph message
quadrant_company_message = dmc.Alert(
    children=[
        dmc.Skeleton(height=8, w="70%", radius="xl"),
        dmc.Skeleton(height=8, w="70%", radius="xl"),
    ],
    id="quadrant-company-message",
    title=dmc.Skeleton(height=8, w="70%", radius="xl"),
    withCloseButton="True",
    p={"base": "xs", "sm": "md"},  # ⬅ smaller padding on mobile
)

subtitle = dmc.Text(
            "The exhaustive list of companies that we analyze, mapped in our magic quadrant. 'Undervalued gems' are the "
            "companies that are undervalued and have growth potential. 'Bubble zone' is the zone to avoid: they are overvalued"
            "and have limited growth potential. 'Hot & Hyped' are overvalued companies that have an strong growth, "
            "meaning that the overvaluation can last for a while.",
            size="xs",
            c="dimmed",
        ),

company_quadrant_card = dmc.Card(children=[
    dcc.Loading(
        children=
        [
            dmc.Stack([
                dmc.Group(
                    [
                        dmc.Title("Compared to similar companies", order=5),
                        dcc.Link(
                            dmc.Button(
                                "See all companies",
                                size="sm",
                                #color="black",
                                leftSection=DashIconify(icon="carbon:quadrant-plot"),
                                variant="outline",
                                style={
                                    "borderWidth": "2px",
                                    "borderColor": "#953BF6",
                                    "boxShadow": "0 4px 10px -1px rgba(127, 17, 224, 0.3), 0 2px 10px -1px rgba(127, 17, 224, 0.2)",
                                }
                            ),
                            href="/ranking"
                        )
                    ],
                    justify="space-between",
                    wrap="nowrap",
                ),
                ],
                justify="left",
                mt="sm",
                mb="xs",
            ),
            html.Div(quadrant_company_message),
            dcc.Graph(id='hyped-ranking-graph-company', config=config_graph_with_toolbar, style={'cursor': 'default'}),
            login_overlay_chart,
        ],
        overlay_style={"visibility": "visible", "filter": "blur(2px)"},
        type="circle",
        color="black"),
    ],
    withBorder=True,
    shadow='sm',
    radius='md',
    #style={'display': 'none'},
    id='section-2',
    p = {"base": "sm", "sm": "xl"},  # smaller padding on mobile
    m = {"base": 5, "sm": "md"},  # tighter outer margin on mobile
)