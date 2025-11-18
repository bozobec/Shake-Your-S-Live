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

product_maturity_graph = dcc.Graph(id='product-maturity-graph', config=config_graph)


# Graph message growth rate
product_maturity_graph_message = dmc.Alert(
    dmc.Text("About the Product Maturity"),
    id="product-maturity-graph-message",
    title="Is the product still improving?",
    color="blue",
    #hide="False",
    withCloseButton=True,
    p={"base": "xs", "sm": "md"},  # ⬅ smaller padding on mobile
)

product_maturity_card = dmc.Card(
    children=[
        dmc.Stack(
            [
                dmc.Title("Product Maturity", order=5),
                html.Div(children=[product_maturity_graph_message, product_maturity_graph])
            ],
            #justify="space-around",
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