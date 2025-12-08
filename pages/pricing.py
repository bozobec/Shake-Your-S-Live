# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
from dash import html
from dash import register_page
import dash_mantine_components as dmc
from dash_iconify import DashIconify


register_page(
    __name__,
    name='Pricing | RAST',
    top_nav=True,
    path='/pricing'
)

pricing_layout = dmc.Container([
    dmc.Grid([
        dmc.GridCol(
            span=8,
            offset=1,  # Centers the 10-column content
            children=[
                dmc.Stack([
                    # Welcome Alert
                    dmc.Alert(
                        title="Ready to support our neutrality?",
                        children=[
                            dmc.Text([
                                "Browse unlimitedly with our ",
                                dmc.Text("Free plan", fw=900, span=True, c="black"),
                                " to see the value of each company separately.",
                                html.Br(),
                                html.Br(),
                                " To access our continuously updated ranking of the most undervalued companies, "
                                "subscribe to the ",
                                dmc.Text("Pro plan", fw=900, span=True, c="violet"),
                                "(you can obviously unsubscribe whenever you want).",
                                html.Br(),
                                html.Br(),
                                "This is how we manage to run the platform ",
                                dmc.Text("neutrally", fw=900, span=True, c="violet"),
                                ", without any sponsor, VC, and therefore without any conflict of interest ;).",
                                html.Br(),
                                html.Br(),
                                "Thank you 🫶!"
                            ])
                        ],
                        color="#953BF6",
                        variant="light",
                        icon=DashIconify(icon="mdi:information-outline", width=24),
                        withCloseButton=True,
                        mb="xl"
                    ),
                    dmc.Title(
                        "Choose Your Plan",
                        order=3,
                        ta="center",  # text-align center
                        mb="xl"  # margin bottom extra-large
                    ),
                    html.Div(id='pricing-table-container')
                ], gap="lg")
            ]
        )
    ], gutter="xl")
], size="xl", px="md")  # xl container, padding x medium

def layout(company=None, **other_unknown_query_strings):
    return pricing_layout  # Empty - cards are in app.py
