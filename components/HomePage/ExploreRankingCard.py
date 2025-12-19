import dash_mantine_components as dmc
from dash import html, dcc


def create():
    """
    Returns the right card on the main page that tells you to explore the ranking.
    :return:
    """
    return dmc.Card(
        children=[
            html.Img(
                src='/assets/ranking_illustration.png',
                style={
                    'width': '80px',
                    'height': '80px',
                    'marginBottom': '30px',
                    'borderRadius': '20px'
                }
            ),
            dmc.Title(
                "Explore our ranking",
                order=5,
                style={
                    'fontFamily': 'ABCGravityUprightVariable-Trial, sans-serif',
                }
            ),
            dmc.Text(
                "We rank the most undervalued companies based on our valuations (for members only).",
                size="sm",
                c="dimmed",
            ),
            dmc.Space(h=40),
            dcc.Link(
                html.Div(
                    id="clerk-extra-signin",
                    style={
                        'textAlign': 'center',
                    }
                ),
                href="/ranking",
            ),
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
