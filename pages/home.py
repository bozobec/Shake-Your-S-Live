import dash
from dash import html, dcc, callback, Input, Output, register_page
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import main
from datetime import datetime, timedelta, date
from pages.dashboard import table_hype



register_page(
    __name__,
    name='RAST | Value Customer-Based Companies',
    top_nav=True,
    path='/'
)

first_card = dmc.Card(
    children=[
        dmc.Stack(
            [
                DashIconify(icon="radix-icons:crosshair-2", width=30, flip="horizontal", color='#4dabf7'),
                #dmc.Space(h=20),
                dmc.Title("1.Pick a company", order=4),
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
                placeholder="Dropbox",
                disabled=True,
                #id="framework-select",
                #value="ng",
                #data=[
                #    {"value": "react", "label": "Netflix"},
                #    {"value": "ng", "label": "Spotify"},
                #    {"value": "svelte", "label": "Meta"},
                #    {"value": "vue", "label": "Dropbox"},
                #],
                data=[
                    {"group": 'Frontend', "value": 'React', "label": 'React'},
                    {"group": 'Frontend', "value": 'Angular', "label": 'Angular'},
                    {"group": 'Backend', "value": ['Express', 'Django'], "label": ['Express', 'Django']},
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
                dmc.Title("2.Predict the Growth", order=4),
            ],
            #position="apart",
            #mt="md",
            #mb="xs",
        ),
        dmc.Space(h=21),
        dmc.Divider(color='#4dabf7', size="sm", style={'width': 100}),
        dmc.Space(h=21),
        dmc.Text(
            "Let RAST's engine do the crystal ball work. Predict how the company's user base will flourish in the "
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
            dmc.Container([
            dmc.Slider(
                id="slider-example",
                min=20,
                max=86,
                value=30,
                marks=[
                    {"value": 20, "label": "20M"},
                    {"value": 50, "label": "50M"},
                    {"value": 86, "label": "80M"},
                ],
                mb=35,
                radius=180,
            )]),
        ),
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
    # style={"width": 350},
)

layout_example_graph = go.Layout(
    # title="User Evolution",
    plot_bgcolor="White",
    margin=go.layout.Margin(
        l=0,  # left margin
        r=0,  # right margin
        b=0,  # bottom margin
        t=20,  # top margin
    ),
    xaxis=dict(
        # title="Timeline",
        linecolor="Grey",
        # hoverformat=".0f",
    ),
    yaxis=dict(
        title="Users",
        linecolor="Grey",
        gridwidth=1,
        gridcolor='#e3e1e1',
        # hoverformat='{y/1e6:.0f} M'
    ),
)

graph_example_figure = go.Figure(layout=layout_example_graph)
graph_example_container = dcc.Graph(id='graph-example', config={'displayModeBar': False, 'scrollZoom': False, 'staticPlot': True},
                                    figure=graph_example_figure)
dates_raw = np.array([
    '2011-09-30', '2011-12-31', '2012-03-31', '2012-06-30', '2012-09-30',
    '2012-12-31', '2013-03-31', '2013-06-30', '2013-09-30', '2013-12-31',
    '2014-03-31', '2014-06-30', '2014-09-30', '2014-12-31', '2015-03-31',
    '2015-06-30', '2015-09-30', '2015-12-31', '2016-03-31', '2016-06-30',
    '2016-09-30', '2016-12-31', '2017-03-31', '2017-06-30', '2017-09-30',
    '2017-12-31', '2018-03-31', '2018-06-30', '2018-09-30', '2018-12-31',
    '2019-03-31', '2019-06-30', '2019-09-30', '2019-12-31', '2020-03-31',
    '2020-06-30', '2020-09-30', '2020-12-31', '2021-03-31', '2021-06-30',
    '2021-09-30', '2021-12-31', '2022-03-31', '2022-06-30', '2022-09-30',
    '2022-12-31', '2023-03-31', '2023-06-30', '2023-09-30', '2023-12-31'
])

#dates_datetime = np.array([datetime.strptime(date, '%Y-%m-%d') for date in dates_raw])

users = values = np.array([
    20.00000000, 21.00000000, 22.00000000, 23.00000000, 25.00000000,
    28.00000000, 34.24000000, 35.64000000, 38.01000000, 41.43000000,
    46.13000000, 47.99000000, 50.65000000, 54.48000000, 59.62000000,
    62.08000000, 66.02000000, 70.84000000, 77.71000000, 79.90000000,
    83.28000000, 89.09000000, 94.36000000, 99.04000000, 104.02000000,
    110.64000000, 118.90000000, 124.35000000, 130.42000000, 139.26000000,
    148.86000000, 151.56000000, 158.33000000, 167.09000000, 182.86000000,
    192.95000000, 195.15000000, 203.66000000, 207.64000000, 209.18000000,
    213.56000000, 221.84000000, 221.64000000, 220.67000000, 223.09000000,
    230.75000000, 232.50000000, 238.39000000, 247.15000000, 260.28000000
])
users = users * 1e6

k_scenarios, r_scenarios, p0_scenarios = 260053641.47054195, 0.5261256701309138, 0.0018119516983738132
x_scenarios = np.array([
    54.00, 54.25, 54.50, 54.75, 55.00, 55.25, 55.50, 55.75, 56.00, 56.25,
    56.50, 56.75, 57.00, 57.25, 57.50, 57.75, 58.00, 58.25, 58.50, 58.75,
    59.00, 59.25, 59.50, 59.75, 60.00, 60.25, 60.50, 60.75, 61.00, 61.25,
    61.50, 61.75, 62.00, 62.25, 62.50, 62.75, 63.00, 63.25, 63.50, 63.75,
    64.00, 64.25, 64.50, 64.75, 65.00, 65.25, 65.50, 65.75, 66.00, 66.25
])
low_scenario = np.array([
    2.43997054e+08, 2.45868052e+08, 2.47532219e+08, 2.49009926e+08,
    2.50320100e+08, 2.51480192e+08, 2.52506188e+08, 2.53412643e+08,
    2.54212751e+08, 2.54918416e+08, 2.55540339e+08, 2.56088113e+08,
    2.56570311e+08, 2.56994576e+08, 2.57367706e+08, 2.57695742e+08,
    2.57984036e+08, 2.58237330e+08, 2.58459815e+08, 2.58655195e+08,
    2.58826738e+08, 2.58977326e+08, 2.59109498e+08, 2.59225492e+08,
    2.59327275e+08, 2.59416579e+08, 2.59494927e+08, 2.59563658e+08,
    2.59623948e+08, 2.59676830e+08, 2.59723212e+08, 2.59763892e+08,
    2.59799568e+08, 2.59830855e+08, 2.59858293e+08, 2.59882353e+08,
    2.59903452e+08, 2.59921953e+08, 2.59938176e+08, 2.59952402e+08,
    2.59964875e+08, 2.59975812e+08, 2.59985402e+08, 2.59993810e+08,
    2.60001183e+08, 2.60007647e+08, 2.60013315e+08, 2.60018285e+08,
    2.60022642e+08, 2.60026462e+08
])
high_scenario = np.array([
    2.51846049e+08, 2.55718773e+08, 2.59394662e+08, 2.62877011e+08,
    2.66170000e+08, 2.69278562e+08, 2.72208252e+08, 2.74965129e+08,
    2.77555644e+08, 2.79986535e+08, 2.82264737e+08, 2.84397293e+08,
    2.86391285e+08, 2.88253771e+08, 2.89991727e+08, 2.91612004e+08,
    2.93121287e+08, 2.94526070e+08, 2.95832625e+08, 2.97046990e+08,
    2.98174951e+08, 2.99222038e+08, 3.00193515e+08, 3.01094384e+08,
    3.01929383e+08, 3.02702989e+08, 3.03419425e+08, 3.04082668e+08,
    3.04696454e+08, 3.05264287e+08, 3.05789452e+08, 3.06275022e+08,
    3.06723867e+08, 3.07138668e+08, 3.07521923e+08, 3.07875960e+08,
    3.08202947e+08, 3.08504897e+08, 3.08783685e+08, 3.09041049e+08,
    3.09278603e+08, 3.09497845e+08, 3.09700164e+08, 3.09886846e+08,
    3.10059082e+08, 3.10217976e+08, 3.10364550e+08, 3.10499748e+08,
    3.10624444e+08, 3.10739447e+08
])
datetime_list = [
    datetime(2023, 12, 31, 0, 0), datetime(2024, 3, 31, 8, 48, 58, 775510),
    datetime(2024, 6, 30, 16, 37, 57, 551020), datetime(2024, 9, 30, 0, 26, 56, 326531),
    datetime(2024, 12, 30, 7, 15, 55, 102041), datetime(2025, 3, 31, 16, 4, 53, 877551),
    datetime(2025, 6, 30, 23, 53, 52, 653061), datetime(2025, 9, 30, 7, 42, 51, 428571),
    datetime(2025, 12, 30, 14, 31, 50, 204082), datetime(2026, 3, 31, 23, 20, 48, 979592),
    datetime(2026, 7, 1, 7, 9, 47, 755102), datetime(2026, 9, 30, 14, 58, 46, 530612),
    datetime(2026, 12, 30, 21, 47, 45, 306123), datetime(2027, 4, 1, 6, 36, 44, 81633),
    datetime(2027, 7, 1, 14, 25, 42, 857143), datetime(2027, 9, 30, 22, 14, 41, 632653),
    datetime(2027, 12, 31, 5, 3, 40, 408163), datetime(2028, 3, 31, 13, 52, 39, 183673),
    datetime(2028, 6, 30, 21, 41, 37, 959184), datetime(2028, 9, 30, 5, 30, 36, 734694),
    datetime(2028, 12, 30, 12, 19, 35, 510204), datetime(2029, 3, 31, 21, 8, 34, 285714),
    datetime(2029, 7, 1, 4, 57, 33, 61224), datetime(2029, 9, 30, 12, 46, 31, 836735),
    datetime(2029, 12, 30, 19, 35, 30, 612245), datetime(2030, 4, 1, 4, 24, 29, 387755),
    datetime(2030, 7, 1, 12, 13, 28, 163265), datetime(2030, 9, 30, 20, 2, 26, 938776),
    datetime(2030, 12, 31, 2, 51, 25, 714286), datetime(2031, 4, 1, 11, 40, 24, 489796),
    datetime(2031, 7, 1, 19, 29, 23, 265306), datetime(2031, 10, 1, 3, 18, 22, 40816),
    datetime(2031, 12, 31, 10, 7, 20, 816327), datetime(2032, 3, 31, 18, 56, 19, 591837),
    datetime(2032, 7, 1, 2, 45, 18, 367347), datetime(2032, 9, 30, 10, 34, 17, 142857),
    datetime(2032, 12, 30, 17, 23, 15, 918367), datetime(2033, 4, 1, 2, 12, 14, 693878),
    datetime(2033, 7, 1, 10, 1, 13, 469388), datetime(2033, 9, 30, 17, 50, 12, 244898),
    datetime(2033, 12, 31, 0, 39, 11, 20408), datetime(2034, 4, 1, 9, 28, 9, 795918),
    datetime(2034, 7, 1, 17, 17, 8, 571429), datetime(2034, 10, 1, 1, 6, 7, 346939),
    datetime(2034, 12, 31, 7, 55, 6, 122449), datetime(2035, 4, 1, 16, 44, 4, 897959),
    datetime(2035, 7, 2, 0, 33, 3, 673469), datetime(2035, 10, 1, 8, 22, 2, 448980),
    datetime(2035, 12, 31, 15, 11, 1, 224490), datetime(2036, 4, 1, 0, 0)
]
datetime_values = np.array(datetime_list)

x_area = np.append(datetime_values, np.flip(datetime_values))
y_area_low = low_scenario
y_area_high = np.flip(high_scenario)
y_area = np.append(y_area_low, y_area_high)
hovertemplate_maingraph = "%{text}"

#formatted_y_values = [f"{y / 1e6:.1f} M" if y < 1e9 else f"{y / 1e9:.2f} B" for y in y_trace]
graph_example_figure.add_trace(go.Scatter(name="Low growth", x=datetime_values,
                              y=low_scenario,
                              mode='lines',
                              line=dict(color='LightGrey', width=0.5), showlegend=False,))
graph_example_figure.add_trace(go.Scatter(name="High growth", x=datetime_values,
                              y=high_scenario,
                              mode='lines',
                              line=dict(color='LightGrey', width=0.5), showlegend=False,))
graph_example_figure.add_trace(go.Scatter(x=x_area,
                                  y=y_area,
                                  fill='toself',
                                  line_color='LightGrey',
                                  fillcolor='LightGrey',
                                  opacity=0.2,
                                  hoverinfo='none',
                                  showlegend=False,
                                  )
                       )
graph_example_figure.add_trace(go.Bar(name="Dataset", x=dates_raw, y=users, marker_color="Black", showlegend=False,
                                      ))
graph_example_card = dmc.Card(
    children=[
        dmc.Group(
            [
                dmc.Image(src="/assets/Netflix_2014_logo.svg",
                          alt="Netflix Logo for RAST, the user-based company valuation & prediction tool",
                          width=100),
            ],
            position="apart",
            mt="md",
            mb="xs",
        ),
        graph_example_container,
        dmc.Space(h=10),
    ],
    id="graph-example-card",
    withBorder=True,
    shadow="lg",
    radius="lg",
)


fourth_card = dmc.Card(
    children=[
        dmc.Stack(
            [
                DashIconify(icon="radix-icons:width", width=30, flip="horizontal", color='#4dabf7'),
                #dmc.Space(h=20),
                dmc.Title("4.Time Travel with RAST", order=4),
            ],
            #position="apart",
            #mt="md",
            #mb="xs",
        ),
        dmc.Space(h=21),
        dmc.Divider(color='#4dabf7', size="sm", style={'width': 100}),
        dmc.Space(h=21),
        dmc.Text(
            "Skeptical about our methodology? Dive into the past with RAST's confidence interval magic. See how the market danced to the company's "
            "tune over time. And nope, we don't adjust our method to make old data fit.",
            size="sm",
            color="dimmed",
        ),
        dmc.Space(h=21),
        dmc.CardSection(
            dmc.Image(
                src="/assets/past_performance.png",
                alt="Use RAST to visualize past publicly traded tech companies valuation",
                height=240,
            ), style={'marginBottom': 10, 'marginLeft': 10, 'marginRight': 10}
        ),
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
    # style={"width": 350},
)

reset_parameters_button_home = dcc.Link(
    href="/app",
    children=dmc.Button(
        id="reset-parameters-home",
        children="Show me the Netflix Data",
        leftIcon=DashIconify(icon="fluent:arrow-reset-24-filled"),
        size="xs",
        variant="outline",
        #disabled="False",
        color="primaryPurple",
        )
),

hype_meter_indicator_home = dmc.Badge("Super hyped", variant="outline", color="red", id="hype-indicator-home-example")

hype_meter_bootstrap_home = dbc.Progress(
    children=
        [
            dbc.Progress(value=10.78, color="#953AF6", bar=True, label="", id="hype-meter-noa-home"),
            dbc.Progress(value=50, color="#F963F1", bar=True, label="Cust. Equity", id="hype-meter-users-home"),
            dbc.Progress(value=149.22, color="#FFD000", bar=True, animated=True, striped=True, label="Hype", id="hype-meter-hype-home"),
            dbc.Tooltip("Non-Operating Assets: $10.78B", target="hype-meter-noa-home", placement="top"),
            dbc.Tooltip("Customer Equity: $110.35B", target="hype-meter-users-home", placement="top"),
            #dbc.Tooltip("Delta depending on the chosen scenario", target="hype-meter-delta", id="tooltip-equity-text", placement="top"),
            dbc.Tooltip("Hype: $88.87", target="hype-meter-hype-home", placement="top"),
        ],
    style={"height": "30px", "borderRadius": "30px"},
)


hype_meter_card_home = dmc.Card(
    children=[
        dmc.Group(
            [
                dmc.Image(src="/assets/Netflix_2014_logo.svg",
                          alt="Use RAST to calculate Netflix's or Dropbox's valuation and compare it to the market cap.",
                          width=100),
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
                dmc.Title("3.Hype-Meter Check", order=4),
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
                dmc.Image(src="/assets/dropbox-logo.png",
                          alt="Use RAST to calculate user-based company valuation such as Dropbox",
                          width=80),
                hype_meter_indicator_home,
            ],
            position="apart",
            mt="md",
            mb="xs",
            noWrap=True,
        ),
            #hype_meter,
            dmc.Stack([
                    dmc.Text("Dropbox Market Cap: $11.25B", size="xs", weight=500, align="center", id="hype-market-cap"),
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

section_conclusion = dmc.Stack([
                            dmc.Title("THE COMPANY VALUE CALCULATOR",
                                      order=1,
                                      color="black",
                                      align="left"),
                            dmc.Text("RAST predicts user growth to calculate the company's valuation. "
                                     "Does the market agree? Not always—human psychology, or what we call Hype, "
                                     "plays a role. Hype can persist, but we focus on the cold, hard facts.",
                                     size="xl",
                                     color="dimmed",
                                     align="left"),
                            html.A(dmc.Button("Try RAST - It's Free",
                                              leftIcon=html.Img(src="/assets/Vector_white.svg",
                                                                alt="RAST Logo, user-based company valuation & prediction tool",
                                                                height="15px")),
                                   href="/app"),
    ], align="flex-start")

section_introduction = dmc.Stack([
                        dmc.Title("WE CALCULATE COMPANIES VALUATION BY IDENTIFYING ONE CORE METRIC", order=1, color="black",
                                  align="left"),
                        dmc.Text("Starting with the company's core business model (e.g., Netflix's subscribers), "
                                     "we predict future cash flow to determine the current valuation",
                                 size="xl",
                                 color="dimmed", align="left"),
                        html.A(dmc.Button("Try RAST for free", leftIcon=html.Img(src="/assets/Vector_white.svg", alt="RAST Logo, user-based company valuation & prediction tool",
                                                                                     height="15px")), href="/app"),
                    ], align="flex-start")

section_ranking = dmc.Stack([
                            dmc.Title("THE HYPE CHART",
                                      order=1,
                                      color="black",
                                      align="left"),
                            dmc.Text("These are the companies everyone’s buzzing about. "
                                     "Updated regularly, because hype never sleeps.",
                                     size="xl",
                                     color="dimmed",
                                     align="left"),
                            html.A(dmc.Button("Try RAST - It's Free",
                                              leftIcon=html.Img(src="/assets/Vector_white.svg",
                                                                alt="RAST Logo, user-based company valuation & prediction tool",
                                                                height="15px")),
                                   href="/app"),
    ], align="flex-start")

def layout():
    layout = html.Div(
        children=[
            dmc.Container([
                dmc.Space(h=150),
                dmc.Grid(
                    children=[
                        dmc.Col(span=2),
                        dmc.Col(section_conclusion, span=12, sm=4),
                        dmc.Col(span=1),
                        dmc.Col(hype_meter_card_home, span=12, sm=4),
                        dmc.Col(span="auto"),
                    ],
                    ),
                dmc.Space(h=150),
                dmc.Title("How does it work?", order=1, align="center", color="black"),
                dmc.Title("Valuation in 4 Steps", order=1, align="center",
                          color="black"),
                dmc.Space(h=60),
                dmc.Grid(
                    #cols=4,
                    #spacing="xl",
                    children=[
                        dmc.Col(span=1, sm=1),
                        dmc.Col(first_card, span=12, sm=2.5),
                        dmc.Col(second_card, span=12, sm=2.5),
                        dmc.Col(third_card, span=12, sm=2.5),
                        dmc.Col(fourth_card, span=12, sm=2.5),
                        dmc.Col(span=1, sm=1),
                    ],
                )
                ],
                size="xl", fluid=True,
            ),
            dmc.Space(h=150),
            dmc.Grid(
                # cols=5,
                children=[
                    dmc.Col(span=2),
                    dmc.Col(graph_example_card, span=12, sm=4),
                    dmc.Col(span=1),
                    dmc.Col(section_introduction, span=12, sm=4),
                    dmc.Col(span="auto"),
                    # dmc.Col(),
                ],
            ),
            dmc.Space(h=60),
            dmc.Grid(
                children=[
                    dmc.Col(span=2),
                    dmc.Col(section_ranking, span=12, sm=4),
                    dmc.Col(span=1),
                    dmc.Col(table_hype, span=12, sm=4),
                    dmc.Col(span="auto"),
                ],
            ),
            #dmc.Space(h=300),
        ],
    )
    return layout

