import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from components.base_card import base_card
from dash import html

modal_tutorial = dmc.Container(
    [
        # The Trigger Button
        dmc.Button("Watch Tutorial", id="open-modal-btn"),

        # The Modal
        dmc.Modal(
            title="How to RAST",
            id="video-modal",
            zIndex=10000,
            size="50%",  # Adjust width as needed
            children=[
                html.Iframe(
                    width="100%",
                    height="450px",
                    #allowfullscreen="",
                    src="https://www.youtube.com/embed/I_JZVBTDwyY?si=d4V7utxng3m2RWRb",  # Replace with your ID
                    style={"border": "none"},
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; "
                          "web-share; fullscreen"
                )
            ],
        ),
    ],
    py="xl",
)
