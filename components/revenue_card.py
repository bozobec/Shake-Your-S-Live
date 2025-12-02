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

revenue_graph = dcc.Graph(id='revenue-graph', config=config_graph)


# Graph message
revenue_graph_message = dmc.Alert(
    dmc.Text("About the Average Revenue per Unit"),
    id="revenue-graph-message",
    title="Are they generating more revenue per unit?",
    color="blue",
    #hide="False",
    withCloseButton="True",
    p={"base": "xs", "sm": "md"},  # ⬅ smaller padding on mobile
)

revenue_card = dmc.Card(
    children=[
        dmc.Stack(
            [
                dmc.Title("Revenue over time", order=5, id='revenue-card-title'),
                html.Div(children=[revenue_graph_message, revenue_graph])
            ],
            mt={"base": 5, "sm": "md"},  # tighter on mobile
            mb={"base": 5, "sm": "xs"},  # tighter on mobile
        ),
    ],
    id="section-5",
    #style={'visibility': 'hidden'},
    style={'display': 'none'},
    withBorder=True,
    shadow="sm",
    radius="md",
    p={"base": "sm", "sm": "xl"},  # smaller padding on mobile
    m={"base": 5, "sm": "md"},  # tighter outer margin on mobile
)