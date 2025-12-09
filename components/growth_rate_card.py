from dash import Dash, html, dcc, callback, dash_table
import dash_mantine_components as dmc

config_graph = {
    'displayModeBar': True,
    'scrollZoom': False,
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

growth_graph = dcc.Graph(id='main-graph2', config=config_graph)


# Graph message growth rate
growth_rate_graph_message = dmc.Alert(
    children=dmc.Text("About the Discrete Growth Rate"),
    id="growth-rate-graph-message",
    title="When will the growth stop?",
    color="blue",
    #hide="False",
    withCloseButton=True,
    p={"base": "xs", "sm": "md"},  # ⬅ smaller padding on mobile
)

growth_rate_card = dmc.Card(
    children=[
        dmc.Stack(
            [
                dmc.Title("Growth rate over time", order=5),
                html.Div(children=[growth_rate_graph_message, growth_graph])
            ],
            #justify="space-around",
            #mt="xs",
            mt={"base": 5, "sm": "md"},  # tighter on mobile
            mb={"base": 5, "sm": "xs"},  # tighter on mobile
        ),
    ],
    id="section-7",
    #style={'visibility': 'hidden'},
    style={'display': 'none'},
    withBorder=True,
    shadow="sm",
    radius="md",
    p={"base": "sm", "sm": "xl"},  # smaller padding on mobile
    m={"base": 5, "sm": "md"},  # tighter outer margin on mobile
)