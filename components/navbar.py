import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from components.base_card import base_card
from dash import html
from components.offcanvas import offcanvas
import os

# App button for the Navbar
app_button_link = html.Div(
    [
        dbc.Button("APP", id="app-button-link", active=True, n_clicks=0, href="/"),
    ]
)

# Loads the right login script depending on the environment
IS_PRODUCTION = os.getenv("FLASK_ENV") == "production"
clerk_script = "/assets/clerk.prod.js" if IS_PRODUCTION else "/assets/clerk.dev.js"
print("Environment:", IS_PRODUCTION)
print("Clerk script loaded:", clerk_script)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(children=[
            app_button_link
        ]
        ),
        dbc.NavItem(offcanvas),
        #Login
        dbc.NavItem([
            html.Div(id="clerk-header"),  # placeholder for the user button
            html.Script(src=clerk_script),
        ])
    ],
    brand=[html.Img(
                    src="/assets/RAST_Vector_Logo.svg",
                    alt="RAST Logo, user-based company valuation & prediction tool",
                    height="36px"
    )],
    brand_href="https://www.rast.guru",
    sticky="top",  # Uncomment if you want the navbar to always appear at the top on scroll.
    color="primary",  # Change this to change color of the navbar e.g. "primary", "secondary" etc.
    dark=True,  # Change this to change color of text within the navbar (False for dark text)
)