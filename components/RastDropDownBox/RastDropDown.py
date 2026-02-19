from dash_iconify import DashIconify
import dash_mantine_components as dmc
from dash import html


def create(labels):
    """
    Will return the Dropdown menu, expects the lables coming from AirTable as input.
    :param labels: Labels coming from Airtable
    :return:
    """
    return html.Div(
        dmc.Select(
            placeholder="Select a company...",
            id="dataset-selection",
            data=labels,
            leftSection=DashIconify(icon="icon-park-outline:search"),
            styles={
                "input": {
                    "backgroundColor": "#1a1b1e",
                    "color": "#ffffff",
                    "border": "1px solid #454547",
                    "fontWeight": "500",

                    "&::placeholder": {
                        "color": "#ffffff",
                        "opacity": "0.7",
                    },
                },
                "dropdown": {
                    "backgroundColor": "#1a1b1e",
                    "border": "1px solid #454547",
                    "fontWeight": "500",
                },
                "option": {
                    "color": "#ffffff",
                    "backgroundColor": "#1a1b1e",
                    "&:hover": {
                        "backgroundColor": "#373A40",
                    },
                    "&[data-selected]": {
                        "backgroundColor": "#5c7cfa",
                        "color": "white",
                    },
                    "fontWeight": "400",
                },
            },
            nothingFoundMessage="We don't have this company yet!",
            searchable=True,
            comboboxProps={"transitionProps": {"transition": "pop", "duration": 200}},
        ),
        className="mantine-select-wrapper"
    )
