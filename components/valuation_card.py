from dash import Dash, html, dcc, callback, dash_table
import dash_mantine_components as dmc

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

valuation_over_time = html.Div(children=[dcc.Graph(id='valuation-graph', config=config_graph)])

# Graph message
valuation_graph_message = dmc.Alert(
    dmc.Text(
        "About the Current Market Cap",
        #size={"base": "8px", "sm": "sm"}   # smaller text on mobile
    ),
    id="valuation-graph-message",
    title="About the Current Market Cap",
    color="blue",
    withCloseButton="True",
    p={"base": "xs", "sm": "md"},  # ⬅ smaller padding on mobile
    radius={"base": "xs", "sm": "md"},   # softer on mobil
)

valuation_card = dmc.Card(
    children=[
        dmc.LoadingOverlay(
                visible=False,
                id="loading-overlay",
                overlayProps={"radius": "sm", "blur": 2},
                zIndex=10,
        ),
        # Card Title
        dmc.Stack(
            [
                dmc.Title("Welcome to RAST", id="graph-title", order=5, textWrap="nowrap"),
                html.Div(children=[valuation_graph_message, valuation_over_time])
            ],
            justify="space-between",
            mt={"base": 5, "sm": "md"},  # tighter on mobile
            mb={"base": 5, "sm": "xs"},  # tighter on mobile
        )
    ],
    id="section-2",
    style={'display': 'none'},
    withBorder=True,
    shadow="sm",
    radius="md",
    #p="xl",
    p={"base": "sm", "sm": "xl"},  # smaller padding on mobile
    m={"base": 5, "sm": "md"},  # tighter outer margin on mobile
)