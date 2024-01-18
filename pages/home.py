import dash
from dash import html, dcc, callback, Input, Output, register_page
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc



register_page(
    __name__,
    name='Home',
    top_nav=True,
    path='/'
)

first_card = dmc.Card(
    children=[
        dmc.Stack(
            [
                DashIconify(icon="radix-icons:crosshair-2", width=30, flip="horizontal", color='#4dabf7'),
                #dmc.Space(h=20),
                dmc.Title("Pick a company", order=4),
            ],
            #position="apart",
            #mt="md",
            #mb="xs",
        ),
        dmc.Space(h=21),
        dmc.Divider(color='#4dabf7', size="sm", style={'width': 100}),
        dmc.Space(h=21),
        dmc.Text(
            "Choose your favorite tech company from our list of 25+ contenders. We've handpicked the most relevant usage "
            "metrics for you, straight from their quarterly reports!",
            size="sm",
            color="dimmed",
        ),
        dmc.Space(h=21),
        dmc.CardSection(
            #dmc.Image(
            #    src="/assets/companies_selection.svg",
            #    height=180,
            #)
            dmc.Select(
                #label="Select framework",
                placeholder="Netflix",
                #id="framework-select",
                #value="ng",
                data=[
                    {"value": "react", "label": "Netflix"},
                    {"value": "ng", "label": "Spotify"},
                    {"value": "svelte", "label": "Meta"},
                    {"value": "vue", "label": "Dropbox"},
                ],
                style={"marginBottom": 30, "marginLeft": 30, "marginRight": 30},
            ),
        ),
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
    # style={"width": 350},
)

second_card = dmc.Card(
    children=[
        dmc.Stack(
            [
                DashIconify(icon="radix-icons:bar-chart", width=30, flip="horizontal", color='#4dabf7'),
                #dmc.Space(h=20),
                dmc.Title("Predict the Growth", order=4),
            ],
            #position="apart",
            #mt="md",
            #mb="xs",
        ),
        dmc.Space(h=21),
        dmc.Divider(color='#4dabf7', size="sm", style={'width': 100}),
        dmc.Space(h=21),
        dmc.Text(
            "Let GROOWT's engine do the crystal ball work. Predict how the company's user base will flourish in the "
            "upcoming years. Remember, Mo' users, mo' money.",
            size="sm",
            color="dimmed",
        ),
        dmc.Space(h=21),
        dmc.CardSection(
            #dmc.Image(
            #    src="/assets/growth_example.svg",
            #    height=180,
            #)
            dmc.Slider(
                value=26,
                marks=[
                    {"value": 20, "label": "20M"},
                    {"value": 50, "label": "50M"},
                    {"value": 86, "label": "80M"},
                ],
                mb=35,
                radius=0,
            ),
        ),
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
    # style={"width": 350},
)



fourth_card = dmc.Card(
    children=[
        dmc.Stack(
            [
                DashIconify(icon="radix-icons:width", width=30, flip="horizontal", color='#4dabf7'),
                #dmc.Space(h=20),
                dmc.Title("Time Travel with GROOWT", order=4),
            ],
            #position="apart",
            #mt="md",
            #mb="xs",
        ),
        dmc.Space(h=21),
        dmc.Divider(color='#4dabf7', size="sm", style={'width': 100}),
        dmc.Space(h=21),
        dmc.Text(
            "Dive into the past with Groowt's confidence interval magic. See how the market danced to the company's "
            "tune over time. It's like a financial DeLorean, minus the flux capacitor",
            size="sm",
            color="dimmed",
        ),
        dmc.Space(h=21),
        dmc.CardSection(
            dmc.Image(
                src="/assets/past_performance.png",
                height=240,
            ), style={'marginBottom': 10, 'marginLeft': 10, 'marginRight': 10}
        ),
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
    # style={"width": 350},
)

reset_parameters_button_home = dmc.Button(
    id="reset-parameters",
    children="Reset Parameters to Default",
    leftIcon=DashIconify(icon="fluent:arrow-reset-24-filled"),
    size="xs",
    variant="outline",
    disabled="True",
        ),

hype_meter_indicator_home = dmc.Badge("Super hyped", variant="outline", color="red")

hype_meter_bootstrap_home = dbc.Progress(
    children=
        [
            dbc.Progress(value=10.78, color="#228BE6", bar=True, label="N-O Assets", id="hype-meter-noa-home"),
            dbc.Progress(value=110.35, color="#74C0FC", bar=True, label="Customer Equity", id="hype-meter-users-home"),
            #dbc.Progress(value=20, color="#D1D1D1", bar=True, animated=True, striped=True, id="hype-meter-delta"),
            dbc.Progress(value=88.87, color="#D1D1D1", bar=True, animated=True, striped=True, label="Hype", id="hype-meter-hype-home"),
            dbc.Tooltip("Non-Operating Assets: $10.78B", target="hype-meter-noa-home", placement="top"),
            dbc.Tooltip("Customer Equity: $110.35B", target="hype-meter-users-home", placement="top"),
            #dbc.Tooltip("Delta depending on the chosen scenario", target="hype-meter-delta", id="tooltip-equity-text", placement="top"),
            dbc.Tooltip("Hype: $88.87", target="hype-meter-hype-home", placement="top"),
        ],
    style={"height": "30px", "border-radius": "30px"},
)


hype_meter_card_home = dmc.Card(
    children=[
        dmc.Group(
            [
                dmc.Image(src="/assets/Netflix_2014_logo.svg", width=100),
                hype_meter_indicator_home,
            ],
            position="apart",
            mt="md",
            mb="xs",
        ),
        #hype_meter,
        dmc.Stack([
                dmc.Text("Netflix Market Cap: $210.2B", size="xs", weight=500, align="center", id="hype-market-cap"),
                hype_meter_bootstrap_home,
            ],
            align="stretch"
        ),
        dmc.Space(h=20),
        dmc.Text(
            id="hype-meter-text",
            children=["Adjust profit margin, discount rate, and ARPU to evaluate the company's current hype through its "
                     "three components: Non-Operating Assets, Customer Equity, and Hype.",
                        #dmc.Text("Non-Operating Assets represent additional valuable company assets.", color="#228BE6"),
                        #dmc.Text("Customer Equity signifies current and future customer-generated profit,"
                        #         " calculated with the selected parameters with a discounted cashflow "
                        #         "method", color="#74C0FC"),
                        #dmc.Text("Hype reflects the current overvaluation of the company in terms of market "
                        #         "capitalization versus actual value.", color="dimmed"),
                        ]
                      ,
            size="xs",
            color="Black",
            style={'display':'inline-block'}
        ),
        dmc.Space(h=10),
        dmc.Center(reset_parameters_button_home),
    ],
    id="hype-meter-card",
    #style={'display': 'none'},
    withBorder=True,
    shadow="lg",
    radius="lg",
)

third_card = dmc.Card(
    children=[
        dmc.Stack(
            [
                DashIconify(icon="fluent:sparkle-24-regular", width=30, flip="horizontal", color='#4dabf7'),
                #dmc.Space(h=20),
                dmc.Title("Hype-Meter Check", order=4),
            ],
            #position="apart",
            #mt="md",
            #mb="xs",
        ),
        dmc.Space(h=21),
        dmc.Divider(color='#4dabf7', size="sm", style={'width': 100}),
        dmc.Space(h=21),
        dmc.Text(
            "Is the user-generated value way less than the current market hype? If yes, we've got a 'Super Hyped' "
            "situation. Tweak the knobs, play around, and see just how far the company's price "
            "is floating away from reality.",
            size="sm",
            color="dimmed",
        ),
        dmc.Space(h=21),
        dmc.CardSection([
            dmc.Group(
            [
                dmc.Image(src="/assets/dropbox-logo.png", width=100),
                hype_meter_indicator_home,
            ],
            position="apart",
            mt="md",
            mb="xs",
        ),
            #hype_meter,
            dmc.Stack([
                    dmc.Text("Dropbox Market Cap: $210.2B", size="xs", weight=500, align="center", id="hype-market-cap"),
                    hype_meter_bootstrap_home,
                ],
                align="stretch"
            ),
            ],
            style={"marginBottom": 10, "marginLeft": 10, "marginRight": 10},
        ),
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
    # style={"width": 350},
)
def layout():
    layout = html.Div(
        children=[
            dmc.Container([
                dmc.Space(h=150),
                dmc.Grid(
                    #cols=5,
                    children=[
                        dmc.Col(span=2),
                        dmc.Col(dmc.Stack([
                            dmc.Title("STEP UP YOUR TECH INVESTMENT GAME.", order=1, color="black", align="left"),
                            dmc.Text("Whether you are a Tech investor, journalist or simply curious about tech "
                                     "valuation, predict Market Hype by unveiling companies' True Value.", size="xl",
                                     color="dimmed", align="left"),
                            html.A(dmc.Button("Try GROOWT Beta Version", leftIcon=html.Img(src="/assets/Vector_white.svg",
                                                                                    height="15px")), href="/app"),
                        ], align="flex-start"), span=12, sm=4),
                        dmc.Col(span=1),
                        dmc.Col(hype_meter_card_home, span=12, sm=4),
                        dmc.Col(span="auto"),
                        #dmc.Col(),
                    ],
                    ),
                dmc.Space(h=150),
                dmc.Title("Discover Tech Company Hype", order=1, align="center", color="black"),
                dmc.Title("in Just 4 Steps", order=1, align="center",
                          color="black"),
                dmc.Space(h=60),
                dmc.Grid(
                    #cols=4,
                    #spacing="xl",
                    children=[
                        dmc.Col(first_card, span=12, sm=3),
                        dmc.Col(second_card, span=12, sm=3),
                        dmc.Col(third_card, span=12, sm=3),
                        dmc.Col(fourth_card, span=12, sm=3),
                    ],
                )
                ],
                size="xl", fluid=True,
            ),
            dmc.Space(h=300),
        ],
    )
    return layout

