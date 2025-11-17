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

main_graph = dcc.Graph(id='main-graph1', config=config_graph)


# Graph message
graph_message = dmc.Alert(
    dmc.Text("About the graph"),
    id="graph-message",
    title="Is there more growth ahead?",
    color="primaryPurple",
    #hide="False",
    withCloseButton="True")

source = dmc.Text(
        id="data-source",
        children="Source",
        size="xs",
        c="dimmed",)

growth_card = dmc.Card(
    children=[
        dmc.Group(
            [
                dmc.Title("Growth over time", id='growth-card-title', order=5),
                html.Div(children=[graph_message, main_graph, source],)
            ],
            #justify="space-around",
            #mt="md",
            mb="xs",
            wrap=True,
        ),
    ],
    id="section-3",
    #style={'visibility': 'hidden'},
    style={'display': 'none'},
    withBorder=True,
    shadow="sm",
    radius="md",
    p="xl"
)