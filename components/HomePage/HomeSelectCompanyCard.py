import dash_mantine_components as dmc
from dash import html


def create(companies):
    """
    Creates the card that lets you select a company from their logos.
    :param companies: Companies you want to display
    :return:
    """
    return dmc.Card(
        id='card-welcome1',
        children=[
            html.Img(
                src='/assets/select_company_illustration.png',
                style={
                    'width': '80px',
                    'height': '80px',
                    'marginBottom': '30px',
                    'borderRadius': '20px'
                }
            ),
            dmc.Title(
                "Explore a company's value",
                order=5,
                style={
                    'fontFamily': 'ABCGravityUprightVariable-Trial, sans-serif',
                }
            ),
            dmc.Space(h=20),
            dmc.SimpleGrid(
                cols=3,  # number of buttons per row (2 or 3 depending on what you want)
                spacing="xs",
                children=[
                    dmc.Anchor(
                        dmc.Button(
                            variant="outline",
                            size="sm",
                            fullWidth=True,
                            justify="center",
                            style={
                                "textDecoration": "none",
                                "paddingRight": "0px",
                                "paddingTop": "2px",
                                "paddingBottom": "2px",
                                "borderWidth": "2px",
                                "borderColor": "#953BF6",
                                "boxShadow": "0 4px 4px -1px rgba(127, 17, 224, 0.3), 0 2px 4px -1px rgba(127, 17, 224, 0.2)",
                            },
                            leftSection=html.Img(
                                src=company["logo"],
                                style={
                                    "maxHeight": "18px",
                                    "maxWidth": "40px",
                                }
                            ),
                        ),
                        href=company.get("url", "") or "#",
                    )
                    for company in companies
                ]
            )
        ],
        withBorder=True,
        shadow="sm",
        radius="xl",
        p="xl",
        style={
            'minHeight': '500px',
            'backgroundColor': 'white'
        }
    )
