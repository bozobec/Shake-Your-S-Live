import dash_mantine_components as dmc
from dash import Dash, html, dcc, callback, dash_table
import dash_bootstrap_components as dbc

hype_meter_indicator = dmc.Badge("Super hyped", variant="outline", color="red", id="hype-meter-indicator")

line = html.Div(
    style={
        "height": "20px",
        "borderLeft": "2px dotted black",
        "marginLeft": "auto",
        "marginBottom": 0,
        "marginTop": 0
    }
)

line_middle = html.Div(
    style={
        "height": "20px",
        "borderLeft": "2px dotted black",
        "marginRight": "auto",
        "marginBottom": 0,
        "marginTop": 0
    }
)

# Hype meter progress bars
hype_meter_bootstrap = dbc.Progress(
    children=[
        dbc.Progress(value=10, color="#C58400", bar=True, label="N-O Assets", id="hype-meter-noa"),
        dbc.Progress(value=10, color="#953BF6", bar=True, label="Intrinsic value", id="hype-meter-users"),
        dbc.Progress(value=10, color="white", bar=True, animated=True, striped=True, label="Hype", id="hype-meter-hype"),
        dbc.Tooltip("Non-Operating Assets: $3.0B", target="hype-meter-noa", id='hype-tooltip-noa', placement="top"),
        dbc.Tooltip("Intrinsic value: $3.0B", target="hype-meter-users", id='hype-tooltip-users', placement="top"),
    ],
    style={"height": "30px", "borderRadius": "0px"},
)

hype_meter_bootstrap_undervaluation = dbc.Progress(
    children=[
        dbc.Progress(value=91.1025, color="white", bar=True, id="hype-meter-undervaluation-rest"),
        dbc.Progress(value=8.8975, color="#FFD000", bar=True, striped=True, id="hype-meter-undervaluation-hype"),
        dbc.Tooltip("Hype: $4.0B", target="hype-meter-undervaluation-hype", id='hype-tooltip-hype', placement="top"),
    ],
    style={"height": "15px", "borderRadius": "0px"},
)

hype_meter_bootstrap_price = dbc.Progress(
    children=[
        dbc.Progress(value=100, color="#9F9F9E", bar=True, label="Current price", id="hype-meter-price"),
        dbc.Progress(value=0, color="white", bar=True, label="Current price", id="hype-meter-price-rest"),
        dbc.Tooltip("Price: $4.0B", target="hype-meter-price", id='hype-tooltip-price', placement="bottom"),
    ],
    style={"height": "30px", "borderRadius": "0px"},
)

# Valuation message (left side)
valuation_message = dmc.Alert(
    children=[
        dmc.Text(
            "This analysis shows the relationship between market cap, intrinsic value, and hype. "
            "Adjust the parameters to see how they affect the overall valuation.",
            size="sm",
            id="valuation-content"
        ),
        dmc.Space(h="xs"),
        dmc.List(
            [
                dmc.ListItem("Hype score, base case = 0.98", id="hype-score-text"),
                dmc.ListItem("Growth score", id="growth-score-text"),
            ],
            size="sm",
            spacing="xs",
        ),
    ],
    id="valuation-message",
    title="Valuation Overview",
    color="blue",
    variant="light",
    icon=dmc.Text("💡", size={"base": "xs", "sm": "xl"}),
    p={"base": "xs", "sm": "md"},  # ⬅ smaller padding on mobile
    #style={"height": "100%"},
)

# Hype meter visualization (right side)
hype_meter_visualization = dmc.Stack(
    children=[
        dmc.Stack([
            dmc.Text("Overvaluation", size="xs", fw=500, ta="right", id="hype-overvaluation-label", m=0),
            line,
            hype_meter_bootstrap_undervaluation,
            hype_meter_bootstrap,
            hype_meter_bootstrap_price,
            line_middle,
            dmc.Group([
                dmc.Text("Market cap = $10.1B", size="xs", fw=500, ta="left", id="hype-market-cap"),
                html.Img(id='company-logo',
                         src='',
                         style={
                             'height': '20px',  # Fixed height
                             'width': 'auto',  # Width adjusts automatically to maintain aspect ratio
                             'display': 'block',  # Prevents inline spacing issues
                             # 'marginTop': '20px',
                             'maxWidth': '100%',  # Prevents overflow in smaller containers
                             'objectFit': 'contain'  # Ensures the image is scaled inside the box
                         }
                         ),
                ],
                justify="space-between"
            )
        ],
        align="stretch",
        gap="xs"
        )
    ],
    gap="md"
)

# Main card

companies = [
    {'symbol': 'RDDT', 'name': 'Reddit', 'url': '/?company=Reddit', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/2/2f/Reddit_wordmark.svg'},
    {'symbol': 'DASH', 'name': 'Doordash', 'url': '/?company=Doordash', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/6/6a/DoorDash_Logo.svg'},
    {'symbol': 'TSLA', 'name': 'Tesla', 'url': '/?company=Tesla', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/e/e8/Tesla_logo.png'},
    {'symbol': 'SBUX', 'name': 'Starbucks', 'url': '/?company=Starbucks', 'logo': 'https://upload.wikimedia.org/wikipedia/sco/d/d3/Starbucks_Corporation_Logo_2011.svg'},
    {'symbol': 'PYPL', 'name': 'PayPal', 'url': '/?company=Paypal', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/3/39/PayPal_logo.svg'},
    {'symbol': 'CHYM', 'name': 'Chime', 'url': '/?company=Chime', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/f/f6/Chime_company_logo.svg'},
    {'symbol': 'SNAP', 'name': 'Snap Inc.', 'url': '/?company=Snap%20Inc.', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/0/0c/Snap_Inc._logo.svg'},
    {'symbol': 'BMBL', 'name': 'Bumble', 'url': '/?company=Bumble', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/b/ba/Bumble_logo_with_wordmark.svg'},
    {'symbol': 'MSFT', 'name': 'Microsoft', 'url': '/?company=Microsoft', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg'},
    {'symbol': 'SOFI', 'name': 'SoFi', 'url': '/?company=SoFi', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/1/16/SoFi_logo.svg'},
    {'symbol': 'META', 'name': 'Meta', 'url': '/?company=Meta', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/7/7b/Meta_Platforms_Inc._logo.svg'},
    {'symbol': 'LYFT', 'name': 'Lyft', 'url': '/?company=Lyft', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/a/a0/Lyft_logo.svg'},
    {'symbol': 'PTON', 'name': 'Peloton', 'url': '/?company=Peloton', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/4/42/Peloton_%28Unternehmen%29_logo.svg'},
    {'symbol': 'ACN', 'name': 'Accenture', 'url': '/?company=Accenture', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/c/cd/Accenture.svg'},
    {'symbol': 'WEN', 'name': "Wendy's", 'url': '/?company=Wendy%27s', 'logo': 'https://upload.wikimedia.org/wikipedia/en/3/32/Wendy%27s_full_logo_2012.svg'}
]

card_welcome2 = dmc.Stack(
            id='card-welcome2',
            gap='xl',
            align="center",
            children=[
                dmc.Title(
                    "Understand companies' potential",
                    order=4,
                    textWrap="nowrap",
                    #align='center',
                    style={
                        #'fontSize': '2.5rem',
                        #'fontWeight': 700,
                        #'color': 'white',
                        #'marginBottom': '10px',
                        #'textAlign': 'center',
                    }
                ),
                dmc.Group(
                    #position='center',
                    gap='sm',
                    style={'flexWrap': 'wrap'},
                    children=[
                        dmc.Anchor(
                            dmc.Button(
                                html.Div([
                                    html.Img(
                                        src=company['logo'],
                                        style={
                                            'width': '20px',
                                            'height': '20px',
                                            'marginRight': '8px',
                                            'verticalAlign': 'middle'
                                        }
                                    ),
                                    html.Span(
                                        company['symbol'],
                                        style={'verticalAlign': 'middle'}
                                    )
                                ], style={'display': 'flex', 'alignItems': 'center'}),
                                variant='light',
                                color="violet",
                                size='md',
                                style={
                                    #'background': 'rgba(255, 255, 255, 0.1)',
                                    #'border': '1px solid rgba(255, 255, 255, 0.2)',
                                    #'color': 'white',
                                    'fontWeight': 600,
                                    'fontSize': '0.9rem',
                                    'padding': '10px 20px',
                                    'transition': 'all 0.3s ease'
                                }
                            ),
                            href=company['url'],
                            target='_blank',
                            style={'textDecoration': 'none'}
                        )
                        for company in companies
                    ]
                )
            ]
        )

card_dashboard = dmc.Group(
    id='card-dashboard',
    #style={'display': 'none'},
    children=[
        # Title and subtitle at the top
        dmc.Stack(
            [
                dmc.LoadingOverlay(
                    visible=True,
                    id="loading-overlay-welcome",
                    overlayProps={"radius": "sm", "blur": 2},
                    zIndex=10,
                ),
                dmc.Group(
                    [
                        dmc.Title("in short", id="summary-card-title", order=5),
                        hype_meter_indicator,
                    ],
                    justify="space-between",
                    wrap="nowrap",
                ),
                dmc.Text(
                    "Select a dataset first",
                    id="company-info-text",
                    size="xs",
                    c="dimmed",
                    style={
                        "@media (max-width: 768px)": {"display": "none"},  # hides on small screens
                    },
                ),
            ],
            gap="xs",
            #mt="xs",
            mb="xs",
        ),
        # Two-column layout: Alert on left, Hype meter on right
        dmc.Grid(
            children=[
                # Left column: Alert message
                dmc.GridCol(
                    valuation_message,
                    span={"base": 12, "sm": 8, "md": 8},
                ),
                # Right column: Hype meter visualization
                dmc.GridCol(
                    hype_meter_visualization,
                    span={"base": 12, "sm": 4, "md": 4},
                ),
                dmc.Loader(
                    color="red",
                    size="md",
                    variant="oval",
                    style={"display": "none"},
                    id="loader-general",
                ),
            ],
            gutter="lg",
        ),
    ]
)

# Card 1 - Select a Company
card_1 = dmc.Card(
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
                #'fontWeight': 'bold',
                #'marginBottom': '30px',
                #'fontSize': '2.5rem'
            }
        ),
        dmc.Space(h=20),
        dmc.SimpleGrid(
            cols=3,  # number of buttons per row (2 or 3 depending on what you want)
            spacing="xs",
            children=[
                dmc.Anchor(
                    dmc.Button(
                        html.Div([
                            html.Img(
                                src=company["logo"],
                                style={
                                    "width": "18px",
                                    "height": "18px",
                                    "marginRight": "3px",
                                    "verticalAlign": "middle"
                                }
                            ),
                            html.Span(company["symbol"])
                        ], style={"display": "flex", "alignItems": "center"}),
                        variant="outline",
                        size="sm",
                        fullWidth=True,
                        style={
                            #"fontWeight": 600,
                            #"fontSize": "0.7rem",
                            #"padding": "10px 20px"
                        }
                    ),
                    href=company["url"],
                    style={"textDecoration": "none"},
                    #target="_blank"
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

# Card 2 - See the Ranking
card2 = dmc.Card(
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
                #'fontWeight': 'bold',
                #'marginBottom': '30px',
                #'fontSize': '2.5rem'
            }
        ),
        dmc.Text(
            "We rank the most undervalued companies based on our valuations (for members only).",
            size="sm",
            c="dimmed",
            #style={'lineHeight': '1.6', 'marginBottom': '20px'}
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

card_welcome = dmc.Container(
            children=[
                dmc.SimpleGrid(
                    cols={"base": 1, "lg": 2},
                    spacing="xl",
                    children=[
                        card_1,
                        card2],
                    style={'padding': '50px 0'}
                )
            ],
            id='card-welcome',
            size="xl",
            style={
                #'background': 'linear-gradient(to bottom, #f8f9fa, #D5AEFF)',
            }
        )

hype_meter_card = dmc.Card(
        children=[
            card_dashboard
        ],
        id="section-1",
        withBorder=True,
        shadow="sm",
        radius="md",
        p={"base": "sm", "sm": "xl"},  # smaller padding on mobile
        m={"base": 5, "sm": "md"},  # tighter outer margin on mobile
    )