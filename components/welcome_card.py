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
        dbc.Progress(value=10, color="#FFD000", bar=True, label="Intrinsic value", id="hype-meter-users"),
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
    style={"height": "10px", "borderRadius": "0px"},
)

hype_meter_bootstrap_price = dbc.Progress(
    children=[
        dbc.Progress(value=100, color="#953AF6", bar=True, label="Current price", id="hype-meter-price"),
        dbc.Progress(value=0, color="white", bar=True, label="Current price", id="hype-meter-price-rest"),
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
    icon=dmc.Text("💡", size="xl"),
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
    {'symbol': 'XOM', 'name': 'Exxon Mobil', 'url': 'https://finance.yahoo.com/quote/XOM', 'logo': 'https://logo.clearbit.com/exxonmobil.com'},
    {'symbol': 'WMT', 'name': 'Walmart', 'url': 'https://finance.yahoo.com/quote/WMT', 'logo': 'https://logo.clearbit.com/walmart.com'},
    {'symbol': 'TSLA', 'name': 'Tesla', 'url': 'https://finance.yahoo.com/quote/TSLA', 'logo': 'https://logo.clearbit.com/tesla.com'},
    {'symbol': 'SBUX', 'name': 'Starbucks', 'url': 'https://finance.yahoo.com/quote/SBUX', 'logo': 'https://logo.clearbit.com/starbucks.com'},
    {'symbol': 'PYPL', 'name': 'PayPal', 'url': 'https://finance.yahoo.com/quote/PYPL', 'logo': 'https://logo.clearbit.com/paypal.com'},
    {'symbol': 'PG', 'name': 'Procter & Gamble', 'url': 'https://finance.yahoo.com/quote/PG', 'logo': 'https://logo.clearbit.com/pg.com'},
    {'symbol': 'ORCL', 'name': 'Oracle', 'url': 'https://finance.yahoo.com/quote/ORCL', 'logo': 'https://logo.clearbit.com/oracle.com'},
    {'symbol': 'NFLX', 'name': 'Netflix', 'url': 'https://finance.yahoo.com/quote/NFLX', 'logo': 'https://logo.clearbit.com/netflix.com'},
    {'symbol': 'MSFT', 'name': 'Microsoft', 'url': 'https://finance.yahoo.com/quote/MSFT', 'logo': 'https://logo.clearbit.com/microsoft.com'},
    {'symbol': 'MMM', 'name': '3M', 'url': 'https://finance.yahoo.com/quote/MMM', 'logo': 'https://logo.clearbit.com/3m.com'},
    {'symbol': 'META', 'name': 'Meta', 'url': 'https://finance.yahoo.com/quote/META', 'logo': 'https://logo.clearbit.com/meta.com'},
    {'symbol': 'KO', 'name': 'Coca-Cola', 'url': 'https://finance.yahoo.com/quote/KO', 'logo': 'https://logo.clearbit.com/coca-cola.com'},
    {'symbol': 'INTC', 'name': 'Intel', 'url': 'https://finance.yahoo.com/quote/INTC', 'logo': 'https://logo.clearbit.com/intel.com'},
    {'symbol': 'GOOGL', 'name': 'Google', 'url': 'https://finance.yahoo.com/quote/GOOGL', 'logo': 'https://logo.clearbit.com/google.com'},
    {'symbol': 'COST', 'name': 'Costco', 'url': 'https://finance.yahoo.com/quote/COST', 'logo': 'https://logo.clearbit.com/costco.com'}
]

card_welcome = dmc.Stack(
            gap='xl',
            children=[
                dmc.Title(
                    children=[
                        'MAKE ',
                        html.Span(
                            'CONFIDENT',
                            style={
                                'background': 'linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%)',
                                'WebkitBackgroundClip': 'text',
                                'WebkitTextFillColor': 'transparent',
                                'backgroundClip': 'text'
                            }
                        ),
                        html.Br(),
                        'INVESTMENT DECISIONS'
                    ],
                    order=1,
                    #align='center',
                    style={
                        'fontSize': '2.5rem',
                        'fontWeight': 700,
                        'color': 'white',
                        'marginBottom': '10px'
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
                                variant='filled',
                                size='md',
                                style={
                                    'background': 'rgba(255, 255, 255, 0.1)',
                                    'border': '1px solid rgba(255, 255, 255, 0.2)',
                                    'color': 'white',
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

welcome_card = dmc.Card(
    children=[card_welcome
    ],
    id="welcome-card",
    withBorder=True,
    shadow="sm",
    radius="md",
    p="xl",
    #style={'display': 'none'}
)