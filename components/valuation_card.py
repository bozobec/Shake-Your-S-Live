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
    dmc.Text("About the Current Market Cap"),
    id="valuation-graph-message",
    title="About the Current Market Cap",
    color="blue",
    withCloseButton="True"
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
                    justify="space-between",
                    mt="md",
                    mb="xs",
                ),
        dmc.Group(
            [
                html.Div(children=[valuation_graph_message, valuation_over_time])
            ],
            #justify="space-around",
            mt="md",
            mb="xs",
            wrap=True,
        ),
    ],
    id="section-3",
    #style={'display': 'none'},
    withBorder=True,
    shadow="sm",
    radius="md",
)