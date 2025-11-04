import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dataAPI
import os

# App Layout
IS_PRODUCTION = os.getenv("IS_PRODUCTION") == "true"  # Setup in heroku 'heroku config:set IS_PRODUCTION=true'
labels = dataAPI.get_airtable_labels() or [] if IS_PRODUCTION else ["Airbnb", "Affirm", "Spotify"]

dropdown = dmc.Select(
            # label="Select framework",
            placeholder="Select a company...",
            id="dataset-selection",
            data=labels,
            style={"marginBottom": 10},
            styles={
                    "option": {
                        "color": "black",  # Text color for options
                    },
            },
            nothingFoundMessage="We don't have this company yet!",
            searchable=True,
            #comboboxProps={"transitionProps": {"transition": "pop", "duration": 200}},
        )

selecting_card = dmc.Card(
    children=[
        dmc.Group(
            [
                dmc.Title("Browse", order=5),
            ],
            justify="left",
            mt="md",
            mb="xs",
        ),
        dmc.Text(
            "Select a company (or other dataset) to visualize its historical data and forecast its future growth.",
            size="xs",
            c="dimmed",
        ),
        dmc.Space(h=10),
        dropdown,
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
)