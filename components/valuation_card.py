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

valuation_over_time = html.Div(children=[dcc.Graph(id='valuation-graph', config=config_graph)])

# Graph message
valuation_graph_message = dmc.Alert(
    dmc.Skeleton(height=8, w="70%", radius="xl"),
    id="valuation-graph-message",
    title=dmc.Skeleton(height=8, w="70%", radius="xl"),
    color="blue",
    withCloseButton="True",
    p={"base": "xs", "sm": "md"},  # ⬅ smaller padding on mobile
    radius={"base": "xs", "sm": "md"},   # softer on mobil
)

valuation_card = dmc.Card(
    children=[
        dcc.Loading(children=[
            # Card Title
            dmc.Stack(
                [
                    dmc.Title(dmc.Skeleton(height=8, w="70%", radius="xl"), id="graph-title", order=5, textWrap="nowrap"),
                    html.Div(children=[valuation_graph_message, valuation_over_time])
                ],
                justify="space-between",
                mt={"base": 5, "sm": "md"},  # tighter on mobile
                mb={"base": 5, "sm": "xs"},  # tighter on mobile
            )],
            overlay_style={"visibility": "visible", "filter": "blur(2px)"},
            type="circle",
            color="black"
        ),
    ],
    id="section-3",
    style={'display': 'none'},
    withBorder=True,
    shadow="sm",
    radius="md",
    #p="xl",
    p={"base": "sm", "sm": "xl"},  # smaller padding on mobile
    m={"base": 5, "sm": "md"},  # tighter outer margin on mobile
)