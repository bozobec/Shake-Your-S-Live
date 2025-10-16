# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import dash
import dash_mantine_components as dmc
from dash import Dash, html, dcc, register_page, callback_context, no_update
from dash import callback
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dataAPI
import main
import dash_bootstrap_components as dbc
# import datetime
from datetime import datetime, timedelta, date
import math
from plotly.subplots import make_subplots
from dash_iconify import DashIconify
import time
from dash.exceptions import PreventUpdate
import urllib.parse
import plotly.io as pio
import io
from flask import send_file, request, jsonify
import base64
from dateutil.relativedelta import relativedelta
from scipy.stats import mstats
from posthog import Posthog
import random
import jwt
import requests
import os
from dotenv import load_dotenv
import stripe
import json
from components.navbar import navbar
from components.graph_layouts import layout_main_graph, layout_revenue_graph, layout_growth_rate_graph, \
    layout_product_maturity_graph

t1 = time.perf_counter(), time.process_time()

# Load environment variables from .env file
load_dotenv()



# Retrieve secrets
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
print("Airtable key loaded:", bool(AIRTABLE_API_KEY))
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
print("Stripe key loaded:", bool(stripe.api_key))

pd.set_option('display.max_rows', 200)
APP_TITLE = "RAST"

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.LUX],
                #external_stylesheets=[dbc.themes.MORPH], Nice stylesheet
                title=APP_TITLE,
                use_pages=True,
                url_base_pathname="/"
                )

# Posthog settings
posthog = Posthog(
  project_api_key='phc_b1l76bi8dgph2LI23vhWTdSNkiL34y2dkholjYEC7gw',
  host='https://eu.i.posthog.com'
)

# Load index template from external file
with open("index_template.html") as f:
    app.index_string = f.read()

# ---------------------------------------------------------------------------

# Constants for the calculation
YEAR_OFFSET = 1970  # The year "zero" for all the calculations
MIN_DATE_INDEX = 5  # Defines the minimum year below which no date can be picked in the datepicker
YEARS_DCF = 15  # Amount of years taken into account for DCF calculation

# ----------------------------------------------------------------------------------
# App Layout

layout_page_standard = dmc.AppShell(
    zIndex=100,
    header=navbar,
    children=[
            #dcc.Location(id='url', refresh=False),
        dcc.Location(id='url-input', refresh=False),
        dcc.Location(id='url-output', refresh=False),
        dcc.Store(id="login-state", storage_type="session"),
        dcc.Store(id="user-id", storage_type="session"),
        html.Div(id="login-state-bridge", children="", style={"display": "none"}),
        dcc.Download(id="download-chart"),  # Component to handle file download

            dmc.Container(fluid=True, children=[
                dmc.Grid([
                    dmc.Col([
                        dmc.LoadingOverlay(
                            # graph_card
                        ),
                        # valuation_over_time_card  # Comment this line to remove the analysis graphs
                    ], span=12, lg=6, orderXs=3, orderSm=3, orderLg=2),
                ],
                    gutter="xl",
                    justify="space-around",
                ),
            ]),
            dash.page_container
    ],
)

app.layout = dmc.MantineProvider(
theme={
        "colors": {
            "primaryPurple": [
                  "#F5F2F8",
                  "#DED2EB",
                  "#CAB2E3",
                  "#B78EE1",
                  "#A567E7",
                  "#953AF6",
                  "#8633DF",
                  "#7933C3",
                  "#6D3BA3",
                  "#633E89",
                  "#593F75",
                  "#503D64"
                ],
            "primaryGreen": [
                  "#E0F0E0",
                  "#BFE6C1",
                  "#9DE39F",
                  "#77E67A",
                  "#4BF250",
                  "#41DC46",
                  "#3AC73E",
                  "#40A743",
                  "#438D45",
                  "#437845",
                  "#416742"
                ]
            },
        "primaryColor": "primaryPurple",
        "fontFamily": "'Basel', sans-serif",
        "headings": {
            "fontFamily": "'ABCGravityVariable-Trial', sans-serif",
        },
    },
    children=layout_page_standard)

# Clerk domain (e.g., "your-app.clerk.accounts.dev")

# Pick the right url depending on the environment (first one is prod, stored on heroku, second is dev)
CLERK_JWKS_URL = os.getenv("https://clerk.rast.guru/.well-known/jwks.json", "https://happy-skylark-73.clerk.accounts.dev/.well-known/jwks.json")
print("clerk jwks")
print(CLERK_JWKS_URL)
jwks = requests.get(CLERK_JWKS_URL).json()

server = app.server

# ----------------------------------------------------------------------------------
# Login flow

# --- Verify Clerk JWT ---
def verify_token(token):
    jwks = requests.get(CLERK_JWKS_URL).json()
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = next(
        (
            {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
            for key in jwks["keys"]
            if key["kid"] == unverified_header["kid"]
        ),
        None,
    )
    if rsa_key:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience="app.rast.guru",
            issuer="https://clerk.rast.guru",
        )
        return payload
    return None


@server.before_request
def check_auth():
    # Let static files and assets load
    if request.path.startswith("/_dash") or request.path.startswith("/assets"):
        return None

    # Skip auth for homepage
    if request.path == "/":
        return None

    # Get Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header.split(" ")[1]
    claims = verify_token(token)
    if not claims:
        return jsonify({"error": "Invalid token"}), 401

    request.user = claims  # attach user info

    # attach plan info for convenience
    request.user_plan = claims.get("public_metadata", {}).get("plan", "free")

# Stores login state & user data and avoids update if login state has not changed
@app.callback(
    Output('login-state', 'data'),
    Output('user-id', 'data'),
    Input("login-state-bridge", "children"),
    prevent_initial_call=True,  # optional: avoid firing on page load if empty
)
def update_login_state(bridge_content):
    if not bridge_content:
        return no_update  # nothing to do

    try:
        state = json.loads(bridge_content)
    except json.JSONDecodeError:
        print("Failed to parse login-state-bridge content:", bridge_content)
        return no_update

    # Extract logged_in and user_id
    logged_in = state.get("logged_in", False)
    user_id = state.get("user_id", None)

    # Store the new state as a dict
    new_data = {"logged_in": logged_in, "user_id": user_id}

    # Access previous value if available to avoid unnecessary updates
    triggered = callback_context.triggered
    if triggered:
        # check previous value
        ctx = callback_context
        prev_value = ctx.states.get("login-state.data")
        if prev_value == new_data:
            return no_update

    print("Updating login-state to:", logged_in, user_id)
    return logged_in, user_id

@app.callback(
    Output("login-overlay-table", "style"),
    Output("login-overlay-chart", "style"),
    Input("login-state", "data"),
)
def toggle_overlay(logged_in):
    if not logged_in:  # False or None:
        style = {"display": "block",
                "position": "absolute",
                "top": 0,
                "left": 0,
                "width": "100%",
                "height": "100%",
                "backgroundColor": "rgba(0,0,0,0.6)",
                "zIndex": 5,
                "backdropFilter": "blur(2px)"}
        return style, style
    return {"display": "none"}, {"display": "none"}



# ----------------------------------------------------------------------------------
# Callback behaviours and interaction
# Callback loading and storing the company information
@app.callback(
    Output('all-companies-information', 'data'),
    Output(component_id='hyped-ranking-graph', component_property='figure'),  # Update graph 1
    Output(component_id='hyped-table-industry', component_property='data'),  # Update graph 1
    Input('url', 'pathname'), # Triggered once when the page is loaded
)
def initialize_data(href):
    # ---- Performance assessment
    t2 = time.perf_counter(), time.process_time()
    print(f" Time to launch the app (before the first callback")
    print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
    print("Loading company information")


    # Load or compute data
    df_all_companies_information = dataAPI.get_hyped_companies_data()
    all_companies_information_store = df_all_companies_information.to_dict('records')

    # Create the list of industries for the ranking dropdown
    # Initialize label_list
    df_list = df_all_companies_information.copy()
    df_list.drop_duplicates(subset='Industry', inplace=True)
    industry_list = []
    for index, row in df_list.iterrows():
        industry = row['Industry']
        industry_list.append({
            "value": industry,
            "label": f"{industry}",
        })
    print("List of industries")
    print(industry_list)
    # Creates the graph mapping companies
    # Example company data
    #companies = ["Company A", "Company B", "Company C", "Company D"]
    companies = df_all_companies_information["Company Name"].tolist()
    growth_score = df_all_companies_information["Growth Score"].tolist()
    hype_score = df_all_companies_information["Hype Score"]


    # Shift to make all positive, then log
    hype_score_log = np.log1p(hype_score + 2)  # +2 shifts so -1 becomes 1


    # Create figure
    fig = go.Figure()


    # Midpoints for quadrants (here using 0.5, adjust if needed, 1.386 for y because log1p(1+2)
    x_mid, y_mid = 0.5, 1.386
    y1= max(hype_score_log)

    # Add quadrant lines
    fig.add_shape(type="line", x0=x_mid, x1=x_mid, y0=0, y1=y1,
                  line=dict(dash="dash", width=2, color="black"))
    fig.add_shape(type="line", x0=0, x1=1, y0=y_mid, y1=y_mid,
                  line=dict(dash="dash", width=2, color="black"))

    # Optional: Add shaded quadrants
    fig.add_shape(type="rect", x0=x_mid, x1=1, y0=y_mid, y1=y1,
                  fillcolor="lightgray", opacity=0.2, line_width=0)
    fig.add_shape(type="rect", x0=0, x1=x_mid, y0=y_mid, y1=y1,
                  fillcolor="white", opacity=0.2, line_width=0)
    fig.add_shape(type="rect", x0=0, x1=x_mid, y0=0, y1=y_mid,
                  fillcolor="lightgray", opacity=0.2, line_width=0)
    fig.add_shape(type="rect", x0=x_mid, x1=1, y0=0, y1=y_mid,
                  fillcolor="#FFD000", opacity=0.2, line_width=0)

    # Add quadrant labels
    fig.add_annotation(x=0.75, y=y1-0.05, text="Hot & hyped", showarrow=False, font=dict(size=10), bgcolor="white")
    fig.add_annotation(x=0.25, y=y1-0.05, text="Bubble zone", showarrow=False, font=dict(size=10), bgcolor="white")
    fig.add_annotation(x=0.25, y=0.05, text="Steady, Forgotten", showarrow=False, font=dict(size=10), bgcolor="white")
    fig.add_annotation(x=0.75, y=0.05, text="Undervalued gems", showarrow=False, font=dict(size=10), bgcolor="white")

    # Marking points as gold and bolded if in the "undervalued gems", otherwise as purple
    marker_colors = [
        "#C58400" if (x > x_mid and y < y_mid) else "#953AF6"
        for x, y in zip(growth_score, hype_score_log)
    ]

    text_font = [
        dict(size=8, weight="bold") if (x > x_mid and y < y_mid) else dict(size=8)
        for x, y in zip(growth_score, hype_score_log)
    ]

    # Alternate text positions to try to limit overlapping
    text_positions = ['top center' if i % 2 == 0 else 'bottom center' for i in range(len(growth_score))]


    # Add scatter points with labels
    fig.add_trace(go.Scatter(
        x=growth_score,
        y=hype_score_log,
        mode="markers+text",
        text=companies,
        textposition=text_positions,
        textfont=dict(size=8),
        marker=dict(
            size=10,
            color=marker_colors,
            line=dict(width=2, color="white")
        )
    ))

    # Layout tweaks
    fig.update_layout(
        #title="Hype-Growth quadrant",
        xaxis=dict(title="Growth potential", range=[0, 1], fixedrange=True),
        yaxis=dict(
            title="Hype level",
            fixedrange=True,
            #type="log",  # 🔹 log scale
            #autorange=True  # auto-fit the range
        ),
        plot_bgcolor="white",
        dragmode=False,
        clickmode=None,
        #config = {'scrollZoom': False},
        margin=go.layout.Margin(
            l=0,  # left margin
            r=0,  # right margin
            b=0,  # bottom margin
            t=20,  # top margin
        ),
        #width=700, height=600
    )

    return all_companies_information_store, fig, industry_list

# Callback to enable the slider if "Custom" is selected
@app.callback(
    Output("range-slider-k", "disabled"),
    Output("range-arpu-growth", "disabled"),
    Output("range-discount-rate", "disabled"),
    Output("range-profit-margin", "disabled"),

    [Input("dataset-selection", "value"),
    Input("scenarios-picker", "value")])
def enable_slider(selection, scenario_value):
    if scenario_value == "Custom":
        return False, False, False, False
    else:
        return True, True, True, True

# Callback to update the URL based on the dropdown selection and track the dataset selected via posthog
@app.callback(
    Output('url-input', 'pathname'),
    Input("dataset-selection", "value"),
    State("url-input", "search")
)
def update_url(data_selection, current_pathname):
    """
    Updates the URL pathname based on dropdown selection.
    """
    if not data_selection:
        # No update if no data selection is made
        return dash.no_update

        # Parse the current pathname and extract query parameters
    parsed_url = urllib.parse.urlparse(current_pathname)
    current_query_params = urllib.parse.parse_qs(parsed_url.query)
    current_company = current_query_params.get('company', [None])[0]
    # No update if the current company matches the dropdown selection
    if current_company == data_selection:
        return dash.no_update
    # Update the pathname with the selected dataset


    return f"/?company={urllib.parse.quote(data_selection)}"

# Callback to update the dropdown selection based on the URL.
@app.callback(
    [Output('dataset-selection', 'value'),
     Output('dataset-selected-url', 'data')],
    [Input('url-input', 'search')],
    [State('dataset-selection', 'value')]
)
def update_select_based_on_url(url_search, current_selected_dataset):
    """
    Synchronizes the dropdown selection with the current URL.
    """
    if not url_search:
        # No update if the URL search part is empty
        return dash.no_update, dash.no_update

    # Parse the query string from the URL
    query_params = urllib.parse.parse_qs(url_search.lstrip('?'))
    dataset_url = query_params.get('company', [None])[0]  # Get the 'company' parameter from the URL

    # No update if the dropdown already matches the URL or the URL value is invalid
    if dataset_url == current_selected_dataset or not dataset_url:
        return dash.no_update, dash.no_update

    # Update the dropdown value and clear the persistent URL dataset data
    return dataset_url, None
# Callback to change the Graph's title, enable the analysis buttons
@app.callback([
    #Output("accordion-growth", "disabled"),
    Output("accordion-plateau", "disabled"),
    Output("accordion-valuation", "disabled"),
    Output("accordion-correlation", "disabled"),
    Output("accordion-product-maturity", "disabled"),
    Output("loader-general", "style"),

    Input("dataset-selection", "value"),
], prevent_initial_call=True)
def select_value(value):
    title = value
    subtitle = "Explore " + str(
        value) + "'s Future Outlook to assess its current valuation and explore RAST's past valuations. Customize " \
                 "Predictions with the Slider in the 'Valuation Drivers' Section and Adjust " \
                 "the Forecast Start Date Using the Datepicker. Use the 'Past performance' section " \
                 "to see RAST's calculated hype over time."
    show_loader = {'display': 'block'}
    return False, False, False, False, show_loader


# Callback defining the minimum and the maximum date of the datepicker and loading the dataset
@app.callback([
    Output(component_id='date-picker', component_property='minDate'),  # Calculate the min of the new history slider
    Output(component_id='date-picker', component_property='maxDate'),  # Calculate the min of the new history slider
    Output(component_id='date-picker', component_property='value'),
    # Resets the date to the last available date of the dataset
    Output(component_id='users-dates-raw', component_property='data'),  # Stores the users + dates data
    Output(component_id='users-dates-formatted', component_property='data'),
    # Stores the users + dates formatted for computation
    Output(component_id='graph-unit', component_property='data'),  # Stores the graph unit (y axis legend)
    Output("graph-title", "children"),
    Output("graph-subtitle", "children"),
    Output(component_id='profit-margin', component_property='style'),  # Show/hide depending on company or not
    Output(component_id='discount-rate', component_property='style'),  # Show/hide depending on company or not
    Output(component_id='hype-meter-card', component_property='style'),  # Show/hide depending on company or not
    Output(component_id='arpu-growth', component_property='style'),  # Show/hide depending on company or not
    Output(component_id='profit-margin-container', component_property='children'),
    Output(component_id='best-profit-margin-container', component_property='children'),
    # Change the text below the profit margin slider
    Output(component_id='range-profit-margin', component_property='marks'),
    # Adds a mark to the slider if the profit margin > 0
    #Output(component_id='range-profit-margin', component_property='value'),
    # Sets the value to the current profit margin
    Output(component_id='total-assets', component_property='data'),  # Stores the current assets
    Output(component_id='users-revenue-correlation', component_property='data'),  # Stores the correlation between
    #Output(component_id='range-discount-rate', component_property='value'),
    Output(component_id='initial-sliders-values', component_property='data'),  # Stores the default slider values
    Output(component_id='data-source', component_property='children'),  # Stores the source of the data shown
    Output(component_id='data-selection-counter', component_property='data'),  # Flags that the data has changed
    Output("loader-general", "style", allow_duplicate=True),
    Output(component_id='market-cap-tab', component_property='style'),  # Hides Market cap tab if other data is selected
    Output(component_id='symbol-dataset', component_property='data'),  # Hides Market cap tab if other data is selected
    Output(component_id='max-net-margin', component_property='data'),  # Stores the max net margin opf the selected company
    Output('company-logo', 'src'),
    Output('tabs-component', 'value'),  # Tab selected 'value' -> 2 for the growth tab, 1 for the valuation

    # the chosen KPI and the revenue

    Input(component_id='dataset-selection', component_property='value'),  # Take dropdown value
    Input(component_id='last-imported-data', component_property='data')],  # Take dropdown value
    Input(component_id='all-companies-information', component_property='data'),  # Take information about all companies
    # [State('main-plot-container', 'figure')],
    prevent_initial_call=True,
)
def set_history_size(dropdown_value, imported_df, df_all_companies):
    t1 = time.perf_counter(), time.process_time()
    """
    Posthog event
    """
    posthog.capture(
        distinct_id='user_or_session_id',  # replace with real user/session ID
        event='dash_select_changed',
        properties={
            'location': 'dash_app',
            'selected_value': dropdown_value
        }
    )
    try:
        # Fetch dataset from API
        df = dataAPI.get_airtable_data(dropdown_value)
        if df.empty:
            dropdown_value = "Imported Data"
            df = pd.DataFrame(imported_df)
            key_unit = df.columns[1]
            data_source = "Import"
            df.columns = ['Date', 'Users'] # Renaming the columns the same way as Airtable
            symbol_company = "N/A" # By default, imported data are not "Financial" data
            df['Revenue'] = 0
        else:
            key_unit = df.loc[0, 'Unit']
            data_source = df.loc[0, 'Source']
            symbol_company = df.loc[0, 'Symbol']

        # Creating the title & subtitle for the graph
        if symbol_company != "N/A":
            title = dropdown_value + " (" + symbol_company + ")"
        else:
            title = dropdown_value

        title_image = dmc.Group([dropdown_value, dmc.Image(
            src="https://upload.wikimedia.org/wikipedia/commons/6/69/Airbnb_Logo_B%C3%A9lo.svg", height=10)])
        subtitle = "Explore " + str(dropdown_value) + "'s Historical " + key_unit + " data (Bars) used to calculate the valuation and future growth " \
                                                                                    "projections. Customize " \
                                                                                    "predictions with the slider in the 'Valuation Drivers' section and adjust " \
                                                                                    "the forecast start date using the datepicker."

        # Creating the source string for the graph
        if data_source == "Financial Report":
            source_string = "Data Source: " + dropdown_value + " Quarterly " + str(data_source) + " | Forecast: rast.guru"
        else:
            source_string = "Data Source: " + str(data_source)

        # Transforming it to a dictionary to be stored
        users_dates_dict = df.to_dict(orient='records')

        # Process & format df. The dates in a panda serie of format YYYY-MM-DD are transformed to a decimal yearly array
        dates = np.array(main.date_formatting(df["Date"]))
        dates_formatted = dates + YEAR_OFFSET
        dates_unformatted = np.array(df["Date"])
        users_formatted = np.array(df["Users"]).astype(float) * 1000000

        # Fetches Max net Margin and stores it
        # max_net_margin = df_all_companies.loc[df_all_companies["Company Name"] == dropdown_value, "Max Net Margin"]
        max_net_margin = None
        company_logo_link_src = None

        # Ugly "if" statement making sure that the information are loaded, because it can happen that the initial callback is not triggered
        if not df_all_companies:
            df_all_companies_information = dataAPI.get_hyped_companies_data()
            df_all_companies = df_all_companies_information.to_dict('records')
        for company in df_all_companies:
            if company['Company Name'].lower() == dropdown_value.lower():
                max_net_margin = company['Max Net Margin']
                company_logo_link_src = company['Company Logo']
                break

        print("Basisnetmargin")
        print(type(max_net_margin))
        print(max_net_margin)

        # Logic to be used when implementing changing the ARPU depending on the date picked
        # date_last_quarter = main.previous_quarter_calculation().strftime("%Y-%m-%d")
        # closest_index = main.find_closest_date(date_last_quarter,dates_unformatted)

        # Check whether it is a public company: Market cap fetching & displaying profit margin,
        # discount rate and arpu for Companies
        if symbol_company != "N/A":
            hide_loader = {'display': ''} # keep on showing the loader
            show_company_functionalities = {'display': ''}  # Style component showing the fin. function.
            tab_selected = "1"  # show the first tab i.e. the valuation one
            try:
                # Ugly if to create exceptions for companies that have weird assets
                if dropdown_value == "Centene Corporation":
                    total_assets = 0
                else:
                    yearly_revenue, total_assets = dataAPI.get_previous_quarter_revenue(symbol_company)  # Getting with API
                print("Latest yearly revenue & total assets fetched")
            except Exception as e:
                print("Error fetching revenue & total assets, standard value assigned")
                total_assets = 1000
            filtered_revenue_df = df[df["Revenue"] != 0]  # Getting rid of the revenue != 0
            quarterly_revenue = np.array(filtered_revenue_df["Revenue"]) * 1_000_000  # Getting in database
            # Regression between Users and revenue
            # Sorting the users in ascending order and reflecting it to the revenue
            users_correlation = users_formatted[-len(quarterly_revenue):]
            revenue_correlation = quarterly_revenue
            sorted_indices = np.argsort(users_correlation)
            users_correlation_sorted = users_correlation[sorted_indices]
            revenue_correlation_sorted = revenue_correlation[sorted_indices]
            users_revenue_regression = main.linear_regression(users_correlation_sorted,
                                                              revenue_correlation_sorted)

            # Profit margin text and marks
            profit_margin_array = np.array(df["Profit Margin"])

            current_annual_profit_margin = profit_margin_array[-1]
            max_annual_profit_margin = max(profit_margin_array)
            text_max_profit_margin = "Max theoretical profit margin: " + str(max_net_margin) + "%"
            text_best_profit_margin = "Best recorded profit margin ever: " + str(max_annual_profit_margin) + "%"
            if current_annual_profit_margin > 1:
                value_profit_margin_slider = float(current_annual_profit_margin)
                marks_profit_margin_slider = [
                    {"value": 2, "label": "2%"},
                    {"value": max_net_margin, "label": "MAX"},
                    {"value": 50, "label": "50%"},
                ]
                text_profit_margin = "Latest annual profit margin: " + str(current_annual_profit_margin) + "% 🤩"

            else:
                marks_profit_margin_slider = [
                    {"value": 2, "label": "2%"},
                    {"value": max_net_margin, "label": "MAX"},
                    {"value": 50, "label": "50%"},
                ]
                value_profit_margin_slider = max_net_margin
                text_profit_margin = "Latest annual profit margin: " + str(current_annual_profit_margin) + "% 😰"

        else:
            hide_loader = {'display': 'none'}
            total_assets = 0
            show_company_functionalities = {'display': 'none'}
            tab_selected = "2" # show the second tab i.e. the Growth one
            users_revenue_regression = 0
            text_profit_margin = ""
            value_profit_margin_slider = 5.0
            marks_profit_margin_slider = [
                {"value": 2, "label": "2%"},
                {"value": 10, "label": "10%"},
                {"value": 20, "label": "20%"},
                {"value": 50, "label": "50%"},
            ]
            text_best_profit_margin = ""
            max_net_margin = 0.0

        df_formatted = df
        df_formatted["Date"] = dates_formatted

        # Final DF containing dates, users, Units, Symbols & Quarterly revenue
        users_dates_formatted_dict = df_formatted.to_dict(orient='records')

        min_history_datepicker = str(dates_unformatted[MIN_DATE_INDEX])  # Minimum date that can be picked
        max_dataset_date = datetime.strptime(dates_unformatted[-1], "%Y-%m-%d")  # Fetching the last date of the dataset
        max_history_datepicker_date = max_dataset_date + timedelta(
            days=6)  # Adding one day to the max, to include all dates
        #max_history_datepicker = max_history_datepicker_date.strftime("%Y-%m-%d")
        current_date = datetime.now()
        max_history_datepicker = current_date.date()
        date_value_datepicker = max_history_datepicker  # Sets the value of the datepicker as the max date
        # current_date = dates_formatted[-1]
        print("Other data", min_history_datepicker, max_dataset_date, max_history_datepicker_date,
              max_history_datepicker, date_value_datepicker)

        # Discount Rate
        value_discount_rate_slider = 5

        # Graph creation
        hovertemplate_maingraph = "%{text}"
        y_legend_title = key_unit

        # Initial_sliders_values
        initial_sliders_values = {'slider_profit_margin': value_profit_margin_slider,
                                  'slider_discount_rate': value_discount_rate_slider}

        t2 = time.perf_counter(), time.process_time()
        print(f" Calculation of the different sliders")
        print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
        print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
        return min_history_datepicker, max_history_datepicker, date_value_datepicker, users_dates_dict, \
            users_dates_formatted_dict, y_legend_title, title, subtitle, \
            show_company_functionalities, show_company_functionalities, show_company_functionalities, \
            show_company_functionalities, text_profit_margin, text_best_profit_margin, marks_profit_margin_slider, \
            total_assets, users_revenue_regression, \
            initial_sliders_values, source_string, True, hide_loader, show_company_functionalities, symbol_company, max_net_margin, company_logo_link_src, tab_selected
    except Exception as e:
        print(f"Error fetching or processing dataset: {str(e)}")
        raise PreventUpdate


@app.callback(
    # Output("loading-component", "loading"),
    Output(component_id='initial-sliders-values', component_property='data', allow_duplicate=True),
    Output(component_id="accordion-main", component_property="value"),
    Output(component_id="plateau-message", component_property="title"),
    Output(component_id="plateau-message", component_property="children"),
    Output(component_id="plateau-message", component_property="color"),
    Output(component_id="accordion-plateau", component_property="icon"),
    Output(component_id="correlation-message", component_property="title"),
    Output(component_id="correlation-message", component_property="children"),
    Output(component_id="correlation-message", component_property="color"),
    Output(component_id="accordion-correlation", component_property="icon"),
    Output(component_id="product-maturity-message", component_property="title"),
    Output(component_id="product-maturity-message", component_property="children"),
    Output(component_id="product-maturity-message", component_property="color"),
    Output(component_id="accordion-product-maturity", component_property="icon"),
    Output(component_id='scenarios-sorted', component_property='data'),
    Output(component_id='range-slider-k', component_property='max'),
    Output(component_id='range-slider-k', component_property='marks'),
    Output(component_id='current-arpu-stored', component_property='data'),  # Stores the current arpu
    Output(component_id='hype-market-cap', component_property='children'),  # Stores the current arpu
    Output(component_id='current-market-cap', component_property='data'),  # Stores the company market cap
    Output(component_id='latest-market-cap', component_property='data'),  # Stores the current (now) company market cap
    Output(component_id='growth-rate-graph-message', component_property='children'),
    Output(component_id='growth-rate-graph-message', component_property='color'),
    Output(component_id='product-maturity-graph-message', component_property='children'),
    Output(component_id='product-maturity-graph-message', component_property='color'),
    Output(component_id='revenue-graph-message', component_property='children'),  # Prints the revenue graph message
    Output(component_id='revenue-graph-message', component_property='color'),  # Prints the revenue graph message color
    Output(component_id='range-slider-k', component_property='value'),  # Reset slider value to the best value
    Output("range-arpu-growth", "value", allow_duplicate=True),
    Output("range-discount-rate", "value", allow_duplicate=True),
    Output("range-profit-margin", "value", allow_duplicate=True),

    Input(component_id='dataset-selection', component_property='value'),  # Take dropdown value
    Input(component_id='date-picker', component_property='value'),  # Take date-picker date
    Input("scenarios-picker", "value"),  # Input the scenario to reset the position of the slider to the best scenario
    Input(component_id='users-dates-formatted', component_property='data'),
    Input(component_id='users-revenue-correlation', component_property='data'),
    Input(component_id='graph-unit', component_property='data'),  # Getting the Unit used
    Input(component_id='users-dates-raw', component_property='data'),
    Input(component_id='initial-sliders-values', component_property='data'),
    State(component_id='symbol-dataset', component_property='data'),
    State(component_id='max-net-margin', component_property='data'), # Max net margin opf the selected company
    prevent_initial_call=True)
# Analysis to load the different scenarios (low & high) when a dropdown value is selected
def load_data(dropdown_value, date_picked, scenario_value, df_dataset_dict,
              users_revenue_correlation, key_unit, df_raw, initial_slider_values, symbol_dataset, max_net_margin):
    print("Starting scenarios calculation")
    t1 = time.perf_counter(), time.process_time()
    date_picked_formatted = main.date_formatting_from_string(date_picked)
    print("datedate")
    df_dataset = pd.DataFrame(df_dataset_dict)
    print("DF_dataset_first", df_dataset)
    # Dates array definition from dictionary
    dates_raw = np.array([entry['Date'] for entry in df_raw])
    dates_new = np.array([entry['Date'] for entry in df_dataset_dict])
    dates = dates_new - 1970
    data_len = len(main.get_earlier_dates(dates, date_picked_formatted - 1970))
    # Users are taken from the database and multiply by a million
    users_new = np.array([entry['Users'] for entry in df_dataset_dict])
    users_original = users_new.astype(float) * 1000000
    closest_index = data_len - 1  # Index of the last data matching the date selected
    current_annual_profit_margin = df_dataset.loc[closest_index, 'Profit Margin']
    current_revenue_array = np.array(df_dataset['Revenue'])
    current_revenue_array = current_revenue_array[:closest_index + 1]
    research_and_development = np.array(df_dataset['Research_And_Development'])
    current_research_and_development = research_and_development[:closest_index + 1]
    share_research_and_development = current_research_and_development/current_revenue_array * 100


    users = users_original
    # Resizing of the dataset taking into account the date picked
    history_value_formatted = date_picked_formatted - 1970  # New slider: Puts back the historical value to the format for computations
    dates_actual = main.get_earlier_dates(dates, history_value_formatted)
    current_users_array = users_new * 1e6
    current_users = current_users_array[closest_index]

    # All parameters are calculated by ignoring data 1 by 1, taking the history reference as the end point
    df_full = main.parameters_dataframe(dates[0:data_len],
                                        users[0:data_len])  # Dataframe containing all parameters with all data ignored
    print("df_full", df_full)
    df_sorted = main.parameters_dataframe_cleaning(df_full, users[
                                                            0:data_len])  # Dataframe where inadequate scenarios are eliminated
    print("df_sorted", df_sorted)

    if df_sorted.empty:
        print("No good scenario could be calculated")
        df_sorted = main.parameters_dataframe_cleaning_minimal(df_full, users[0:data_len])
    else:
        print("Successful scenarios exist")
    print("df_sorted", df_sorted)
    df_sorted_dict = df_sorted.to_dict(orient='records')  # Transforming it to dict to be stored
    if dropdown_value is None:  # Exception for when dropdown is not selected yet, initializing df
        df = df_full
        current_valuation = 100
    if date_picked_formatted:
        if df_sorted.empty:
            state_alert = True
        else:
            state_alert = False

    # Best scenario definition ---> Index of the row containing the highest R^Square
    highest_r2_index = df_sorted['R Squared'].idxmax()

    # Scenario analysis
    # Growth: for the best growth scenario (highest R^2),
    #   First rule:
    #           if the difference between the log R^2 and the linear R^2
    #           is <0.1, then that means the growth is stabilizing and a classical logistic growth is to be expeced
    #           if it is > 0.1 then it means that the dataset is still in its exponential growth and the probability
    #           for exponential growth is high
    #   Second rule:
    #           if either K or r are < 0 in the last 4 iterations, that means that there is a potential for high growth

    diff_r2lin_log = df_sorted.at[highest_r2_index, 'Lin/Log Diff']

    # Plateau definition & time to 90% of the plateau

    k_scenarios = np.array(df_sorted['K'])
    r_scenarios = np.array(df_sorted['r'])
    p0_scenarios = np.array(df_sorted['p0'])

    k_full = np.array(df_full['K'])
    r_full = np.array(df_full['r'])

    # Growth score calculation, around (a) how fast the company is growing today, and (b) how much headroom they still have.
    # Per-capita (normalized) growth today: g = r(1−u); penetration: u=N/K - (N(t) = current users (or your key driver))
    # For the calculation, we take the best potential growth scenario, not the most probable one
    # g is high if the company has speed (high r) and headroom (low u)
    u = users[-1]/k_scenarios[-1]

    # Core, stage-aware momentum (dimensionless)
    g = r_scenarios[-1]*(1-u)

    # Headroom (dimensionless) - captures how far they are from saturation regardless of speed
    h = 1-u

    # Calculation of a reference r, by winsorizing at 5 - 95 pct -> it should be done across ALL companies
    #r_wins = mstats.winsorize(r_scenarios, limits=[0.05, 0.05])  # returns numpy masked array
    r_ref_global = 0.4

    # Growth score calculation (early rocket: low u, high r): BIG GS | tired incumbent (high u, low r): low GS
    # Here we take a simple 0.5 weight, different weight could be given to the headroom or core
    GS = 0.5*g/r_ref_global+0.5*h

    print("GS")
    print(GS)

    # Growth Rate
    rd = main.discrete_growth_rate(users[0:data_len], dates[0:data_len] + 1970)
    average_rd = sum(rd[-3:])/3

    # Growth Rate Graph message
    if average_rd < 0.1:
        growth_rate_graph_message1 = "The discrete growth rate indicates where " + dropdown_value + " is along its S-curve. " \
                                     "When it reaches 0, growth of its " + key_unit + " ends. The flatter the regression line (purple) " \
                                     "the longer the growth phase.\n" \
                                      "For " + dropdown_value + ", the average annual discrete " \
                                     "growth rate is approaching 0 (" + f"{average_rd:.1f}"+ \
                                     "), indicating an approaching end of the growth."
        growth_rate_graph_color= "yellow"
        if any(r < 0 for r in r_full[-5:]):
            growth_rate_graph_message1 = growth_rate_graph_message1 + " However, the latest growth rates vary substantially," \
                                                                      "  which could lead to a prolonged growth."
    else:
        growth_rate_graph_message1 = "The discrete growth rate indicates where " + dropdown_value + " is along its S-curve. " \
                                     "When it reaches 0, growth of its " + key_unit + " has ended. The flatter the regression line (purple) " \
                                     "the longer the growth phase.\n" \
                                      "For " + dropdown_value + ", the line is still far away from zero, " \
                                                                "indicating a substantial growth ahead."

        growth_rate_graph_color = "green"

    # Revenue Graph Message
    revenue_graph_message = "The graph shows revenue per " + key_unit + " (purple bars) and profit margin (pink line).\n" \
                            " The dotted line represents projected revenue growth, adjustable with the Revenue slider.\n" \
                            " The max net margin indicates the theoretical maximum margin for " + dropdown_value + "."
    revenue_graph_message_color = "primaryPurple"

    # Product Maturity Graph Message
    if np.all(share_research_and_development == 0):
        product_maturity_graph_message = "No R&D data available at the moment for " + str(dropdown_value) + " 🫣"
        product_maturity_graph_message_color = "gray"
        product_maturity_accordion_title = "No Data Available 🫣"
        product_maturity_accordion_body = "At the moment no data is available for " + str(dropdown_value) + " 🫣"
        product_maturity_accordion_color = "gray"
        product_maturity_accordion_icon_color = DashIconify(icon="fluent-mdl2:product-release",
                                                            color=dmc.theme.DEFAULT_COLORS["gray"][6],
                                                            width=20)
    elif share_research_and_development[-1] > 30:
        product_maturity_graph_message = "Tech companies often invest a large share of their revenue in R&D, " \
                                         "and decrease it as their products mature. Currently, " \
                                         + dropdown_value +" is investing heavily in development: a sign that " \
                                                           "its revenue & profit margin could grow significantly in the future."
        product_maturity_graph_message_color = "green"
        product_maturity_accordion_title = "The Product is Growing!"
        product_maturity_accordion_body = "At the moment, " + str(dropdown_value) + \
                                         " is heavily investing in its product, indicating " \
                                         "that the revenue & profit margin may strongly grow in the future."
        product_maturity_accordion_color = "green"
        product_maturity_accordion_icon_color = DashIconify(icon="fluent-mdl2:product-release", color=dmc.theme.DEFAULT_COLORS["green"][6],
                                             width=20)

    elif share_research_and_development[-1] > 10:
        product_maturity_graph_message = "Tech companies often invest a large share of their revenue in R&D. " \
                                            "Currently, " + str(dropdown_value) + " is limiting its investment in " \
                                          "its product, indicating that the product is on its way to being mature and " \
                                                                                  "limited profit margin improvements should be expected."
        product_maturity_graph_message_color = "yellow"
        product_maturity_accordion_title = "The Product is Maturing"
        product_maturity_accordion_body = "At the moment, " + str(dropdown_value) + \
                                         " is limiting its investment in its product, indicating that the revenue and " \
                                         "profit margin should stabilize."
        product_maturity_accordion_color = "yellow"
        product_maturity_accordion_icon_color = DashIconify(icon="fluent-mdl2:product-release",
                                                            color=dmc.theme.DEFAULT_COLORS["yellow"][6],
                                                            width=20)
    else:
        product_maturity_graph_message = "At the moment, " + str(
            dropdown_value) + " is heavily limiting its product investment, indicating" \
                              " that limited improvement on profit margin is to be expected"
        product_maturity_graph_message_color = "red"
        product_maturity_accordion_title = "The Product is Mature"
        product_maturity_accordion_body = "At the moment, " + str(dropdown_value) + \
                                          " is heavily limiting its investment in its product, indicating that " \
                                          "limited improvement on the profit margin is to be expected"
        product_maturity_accordion_color = "red"
        product_maturity_accordion_icon_color = DashIconify(icon="fluent-mdl2:product-release",
                                                            color=dmc.theme.DEFAULT_COLORS["red"][6],
                                                            width=20)

    # Growth Accordion
    # Promising Growth
    if diff_r2lin_log > 0.1 or any(k < 0 for k in k_full[-7:-4]) or any(r < 0 for r in r_full[-7:-4] if r > 0.1):
        growth_message_title = "Promising Exponential Growth Ahead!"
        growth_message_body = "Rast's model predicts a strong likelihood of exponential growth in the foreseeable " \
                              "future, surpassing the best-case scenario displayed."
        growth_message_color = "green"
        growth_icon_color = DashIconify(icon="uit:chart-growth", color=dmc.theme.DEFAULT_COLORS["green"][6], width=20)

    # Stable Growth
    else:
        growth_message_title = "Consistent and Predictable Growth!"
        growth_message_body = "Rast's model suggests a high probability that the dataset has transitioned into a " \
                              "stable growth pattern, aligning closely with our best-case scenario."
        growth_message_color = "yellow"
        growth_icon_color = DashIconify(icon="uit:chart-growth", color=dmc.theme.DEFAULT_COLORS["yellow"][6], width=20)

    # High Growth
    if k_scenarios[-1] < 1e9:
        plateau_high_growth = f"{k_scenarios[-1] / 1e6:.1f} M"
    else:
        plateau_high_growth = f"{k_scenarios[-1] / 1e9:.1f} B"
    time_high_growth = main.time_to_population(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1],
                                               k_scenarios[-1] * 0.9) + 1970
    # Low Growth
    if k_scenarios[0] < 1e9:
        plateau_low_growth = f"{k_scenarios[0] / 1e6:.1f} M"
    else:
        plateau_low_growth = f"{k_scenarios[0] / 1e9:.1f} B"
    time_high_growth = main.time_to_population(k_scenarios[0], r_scenarios[0], p0_scenarios[0],
                                               k_scenarios[0] * 0.9) + 1970
    # Best Growth
    if k_scenarios[highest_r2_index] < 1e9:
        plateau_best_growth = f"{k_scenarios[highest_r2_index] / 1e6:.1f} M"
    else:
        plateau_best_growth = f"{k_scenarios[highest_r2_index] / 1e9:.1f} B"

    time_best_growth = main.time_to_population(k_scenarios[highest_r2_index],
                                               r_scenarios[highest_r2_index],
                                               p0_scenarios[highest_r2_index],
                                               k_scenarios[highest_r2_index] * 0.95) + 1970

    # Plateau Accordion
    if diff_r2lin_log > 0.1:
        plateau_message_title = "The revenue is unlikely to stop growing before " + \
                                main.string_formatting_to_date(time_high_growth)
        plateau_message_body = "Given the likelihood of exponential growth in the foreseeable " \
                               "future, the high growth scenario is likely with 95% of its plateau at " + \
                               str(plateau_high_growth) + " users which should happen in " + main.string_formatting_to_date(
            time_high_growth) + ". If overvalued, the company's hype can remain a while until the revenue stop growing."
    else:
        plateau_message_title = "Plateau could be reached in " + main.string_formatting_to_date(time_best_growth) \
                                + " with " + str(plateau_best_growth) + " users"
        plateau_message_body = "Given the likelihood of a stable growth in the foreseeable " \
                               "future, the best growth scenario is likely to reach 95% of its plateau in " \
                               + main.string_formatting_to_date(time_best_growth) + " with " + str(
            plateau_best_growth) + " users"
    # Plateau message color
    if time_best_growth < date_picked_formatted:
        plateau_message_color = "red"
        plateau_icon_color = DashIconify(icon="simple-icons:futurelearn", color=dmc.theme.DEFAULT_COLORS["red"][6], width=20)
    else:
        plateau_message_color = "green"
        plateau_icon_color = DashIconify(icon="simple-icons:futurelearn", color=dmc.theme.DEFAULT_COLORS["green"][6], width=20)


    # Formatting of the displayed correlation message

    formatted_correlation = f"{users_revenue_correlation * 100:.2f}"  # Formatting the displayed r^2:
    if users_revenue_correlation >= 0.6:
        correlation_message_title = str(key_unit) + " is a great revenue indicator"
        correlation_message_body = "We use " + str(key_unit) + " as a key revenue driver" \
                                                            " to estimate the valuation, because " + str(key_unit) + \
                                   " account for " + str(formatted_correlation) + "% of the revenue variability."
        correlation_message_color = "primaryGreen"
        correlation_icon_color = DashIconify(icon="lineicons:target-revenue", color=dmc.theme.DEFAULT_COLORS["green"][6],
                                         width=20)
    elif users_revenue_correlation > 0:
        correlation_message_title = "Take it with a grain of salt"
        correlation_message_body = str(key_unit) + " do not have a strong correlation with the revenue over time. " \
                                                   "We are looking into alternative metrics to estimate this " \
                                                   "company's valuation, since only " + str(formatted_correlation) + \
                                   "% of the revenue variability is explained by this metric."
        correlation_message_color = "yellow"
        correlation_icon_color = DashIconify(icon="lineicons:target-revenue", color=dmc.theme.DEFAULT_COLORS["yellow"][6],
                                             width=20)

    else:
        correlation_message_title = "Correlation not applicable"
        correlation_message_body = "The correlation information is only relevant for companies"
        correlation_message_color = "gray"
        correlation_icon_color = DashIconify(icon="lineicons:target-revenue", color=dmc.theme.DEFAULT_COLORS["gray"][6],
                                             width=20)

    # Slider definition
    df_scenarios = df_sorted
    data_ignored_array = df_scenarios.index.to_numpy()
    slider_max_value = data_ignored_array[-1]

    # Defining the upper/lower limit after which the star is displayed right next to the label
    percentage_limit_label = 0.1
    max_limit_slider_label = data_ignored_array[int(len(data_ignored_array) * (1-percentage_limit_label))]
    min_limit_slider_label = data_ignored_array[int(len(data_ignored_array)*percentage_limit_label)]
    print(max_limit_slider_label)
    print(min_limit_slider_label)
    print(highest_r2_index)
    # Slider max definition
    if k_scenarios[-1] >= 1_000_000_000:  # If the max value of the slider is over 1 B
        if highest_r2_index >= max_limit_slider_label:  # If the best = max, then display them side by side
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000000000:.1f}B"},
                {"value": highest_r2_index},
                {"value": data_ignored_array[-1], "label": f"★{k_scenarios[-1] / 1000000000:.1f}B"},
            ]
        elif highest_r2_index <= min_limit_slider_label:  # If the best = min, then display them side by side
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000000000:.1f}B ★"},
                {"value": highest_r2_index},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1] / 1000000000:.1f}B"},
            ]
        else:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000000000:.1f}B"},
                {"value": highest_r2_index, "label": "★"},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1] / 1000000000:.1f}B"},
            ]
    elif k_scenarios[-1] >= 1_000_000:
        if highest_r2_index >= max_limit_slider_label:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000000:.0f}M"},
                {"value": data_ignored_array[-1], "label": f"★{k_scenarios[-1] / 1000000:.0f}M"},
            ]
        elif highest_r2_index <= min_limit_slider_label:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000000:.0f}M ★"},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1] / 1000000:.0f}M"},
            ]
        else:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000000:.0f}M"},
                {"value": highest_r2_index, "label": "★"},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1] / 1000000:.0f}M"},
            ]

    else:  # If K max smaller than 1 million
        if highest_r2_index >= max_limit_slider_label:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000:.0f}K"},
                {"value": data_ignored_array[-1], "label": f"★{k_scenarios[-1] / 1000:.0f}K"},
            ]
        elif highest_r2_index <= min_limit_slider_label:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000:.0f}K ★"},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1] / 1000:.0f}K"},
            ]
        else:
            marks_slider = [
                {"value": data_ignored_array[0], "label": f"{k_scenarios[0] / 1000:.0f}K"},
                {"value": highest_r2_index, "label": "★"},
                {"value": data_ignored_array[-1], "label": f"{k_scenarios[-1] / 1000:.0f}K"},
            ]


    # Financial Values Calculation

    # Calculating the date picked (removing one day that is added previously
    date_str = date_picked
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')

    # Remove one day
    new_date_obj = date_obj - timedelta(days=1)

    # Convert back to string
    new_date_str = new_date_obj.strftime('%Y-%m-%d')

    # Check whether it is a public company: Market cap fetching & displaying profit margin,
    # discount rate and arpu for Companies
    symbol_company = symbol_dataset
    if symbol_company != "N/A":
        # If the date picked is the latest, then API call
        try:
            latest_market_cap = dataAPI.get_marketcap(symbol_company)
            if latest_market_cap is None:
                raise ValueError("Market cap returned None")
            print("Latest_market_cap", latest_market_cap)
        except Exception as e:
            print("Couldn't fetch latest market cap, assigning DB value")
            latest_market_cap = df_dataset.loc[closest_index, 'Market Cap'] * 1e3
        if new_date_str == dates_raw[-1]:
            current_market_cap = latest_market_cap  # Sets valuation if symbol exists
        # Otherwise, the market cap of the last quarter is picked
        else:
            current_market_cap = df_dataset.loc[closest_index, 'Market Cap'] * 1e3
        filtered_revenue = current_revenue_array[current_revenue_array != 0]
        hype_market_cap = f"Market Cap = ${latest_market_cap / 1000:.2f}B"  # Formatted text for hype meter
        quarterly_revenue = filtered_revenue * 1_000_000  # Getting in database
        yearly_revenue_quarters = sum(quarterly_revenue[-4:])
        average_users_past_year = (current_users + current_users_array[closest_index - 4]) / 2
        #current_arpu = yearly_revenue_quarters / average_users_past_year
        current_arpu = sum(quarterly_revenue[-4:] / current_users_array[closest_index-4:closest_index])
        printed_current_arpu = f"{current_arpu:.0f} $ (current arpu)"  # formatting
        first_arpu = quarterly_revenue[0] / current_users_array[0]
        print("FirstARPU", first_arpu)
        #arpu_growth_calculated = current_arpu/(first_arpu * (dates[data_len] - dates[3]))
        marks_profit_margin_slider = []
        if current_annual_profit_margin > 1:
            value_profit_margin_slider = float(current_annual_profit_margin)
            text_profit_margin = "Latest annual profit margin: " + str(current_annual_profit_margin) + "% 🤩",

        else:

            text_profit_margin = "Latest annual profit margin: " + str(current_annual_profit_margin) + "% 😰",

    else:
        current_market_cap = 0.0  # Otherwise, market_cap = zero
        current_arpu = 0.0
        total_assets = 0.0
        hype_market_cap = ""
        show_company_functionalities = {'display': 'none'}
        users_revenue_regression = 0.0
        printed_current_arpu = 0.0
        text_profit_margin = ""
        latest_market_cap = 0.0

    # Plateau Accordion
    arpu_needed = main.arpu_for_valuation(k_scenarios[highest_r2_index], r_scenarios[highest_r2_index],
                                          p0_scenarios[highest_r2_index], 0.2, 0.05, 10,
                                          current_market_cap * 1000000)
    # Formating the displayed market cap:
    if current_market_cap >= 1000:
        formatted_market_cap = f"{current_market_cap / 1000:.2f} B$"
    else:
        formatted_market_cap = f"{current_market_cap} mio$"
    if current_market_cap != 0:
        valuation_message_title = "Current market cap is " + str(formatted_market_cap)
        valuation_message_body = "Given the projected user growth, " + str(dropdown_value) + " should make " + \
                                 f"{arpu_needed:.0f} $" + " per user and per year to justify the current market cap " \
                                                          "(assuming a 20% profit margin & a 5% discount rate). They are" \
                                                          " currently making " + f"{current_arpu:.0f} $" + " per user" \
                                                                                                           " and have a " + f"{current_annual_profit_margin:.1f} % " + "" \
                                                                                                                                                                       "net profit margin."
        valuation_message_color = "green"
        valuation_icon_color = DashIconify(icon="radix-icons:rocket", color=dmc.theme.DEFAULT_COLORS["green"][6],
                                         width=20)
    else:
        valuation_message_title = "Valuation not applicable"
        valuation_message_body = "The valuation information is only relevant for companies"
        valuation_message_color = "gray"
        valuation_icon_color = DashIconify(icon="radix-icons:rocket", color=dmc.theme.DEFAULT_COLORS["gray"][6],
                                           width=20)


    # Initial ARPU Growth definition
    arpu_growth = 5

    # Initial slider k value
    initial_slider_values['slider_k'] = highest_r2_index
    initial_slider_values['slider_arpu'] = arpu_growth

    # Growth for each scenario
    best_growth = df_sorted['K'].idxmax()
    worst_growth = df_sorted['K'].idxmin()
    base_growth = highest_r2_index

    # Profit margin for each scenario - Important note: same function used for the valuation graph. If changes are made
    # here, they should be reflected there

    profit_margin_array = np.array(df_dataset['Profit Margin'])
    profit_margin_previous_year = profit_margin_array[-4:]
    average_profit_margin = sum(profit_margin_previous_year) / 4
    if average_profit_margin <= 0:
        # min_profit_margin = 0.01
        min_profit_margin = max_net_margin * 0.8  # Taking 80% of the max profit margin as a lower scenario
        # max_profit_margin = 0.1
        max_profit_margin = max_net_margin
    else:
        # min_profit_margin = average_profit_margin
        min_profit_margin = max_net_margin * 0.8
        # max_profit_margin = average_profit_margin + 0.05
        # max_profit_margin = max(profit_margin_valuation) + 0.05
        max_profit_margin = max_net_margin  # High scenario taking the max theoretical profit margin

    best_profit_margin = max_profit_margin
    worst_profit_margin = min_profit_margin
    base_profit_margin = (min_profit_margin + max_profit_margin) / 2

    # ARPU growth for each scenario

    worst_arpu_growth = 1  # Low scenario
    best_arpu_growth = 5  # High scenario
    base_arpu_growth = 3

    # Discount rate for each scenario --> set as 10%
    discount_rate_slider_value = 10

    if scenario_value == "Worst":
        profit_margin_slider_value = worst_profit_margin
        arpu_growth_slider_value = worst_arpu_growth
        growth_slider_value = worst_growth
    elif scenario_value == "Base":
        profit_margin_slider_value = base_profit_margin
        arpu_growth_slider_value = base_arpu_growth
        growth_slider_value = base_growth
    elif scenario_value == "Best":
        profit_margin_slider_value = best_profit_margin
        arpu_growth_slider_value = best_arpu_growth
        growth_slider_value = best_growth
    else:
        profit_margin_slider_value = no_update
        arpu_growth_slider_value = no_update
        growth_slider_value = no_update

    t2 = time.perf_counter(), time.process_time()
    print(f" Definition of the messages in analysis and above the graphs")
    print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
    return initial_slider_values, \
        ["valuation"], plateau_message_title, plateau_message_body, plateau_message_color, plateau_icon_color, \
        correlation_message_title, correlation_message_body, \
        correlation_message_color, correlation_icon_color, product_maturity_accordion_title, product_maturity_accordion_body,\
        product_maturity_accordion_color, product_maturity_accordion_icon_color, df_sorted_dict, slider_max_value, marks_slider, current_arpu, hype_market_cap, \
        current_market_cap, latest_market_cap, growth_rate_graph_message1, growth_rate_graph_color, \
        product_maturity_graph_message, product_maturity_graph_message_color, revenue_graph_message, \
        revenue_graph_message_color, growth_slider_value, arpu_growth_slider_value, discount_rate_slider_value, profit_margin_slider_value


@app.callback([
    Output(component_id='main-graph1', component_property='figure'),  # Update graph 1
    Output(component_id='revenue-graph', component_property='figure'),  # Update graph 1
    Output(component_id='main-graph2', component_property='figure'),  # Update graph 2 about regression
    Output(component_id='product-maturity-graph', component_property='figure'),  # Update graph 2 about regression
    # Output(component_id='main-graph3', component_property='figure'),  # Update graph 3
    # Output(component_id='carrying-capacity', component_property='children'),  # Update the carrying capacity
    Output(component_id='r2-ring-progress', component_property='sections'),  # Update regression
    # Output(component_id='range-slider-k', component_property='max'),
    # Output(component_id='range-slider-k', component_property='marks'),
    # Output(component_id='graph-message', component_property='hide'),
    Output(component_id='graph-message', component_property='children'),
],

    [
        Input(component_id='range-slider-k', component_property='value'),  # Take user slider value
        Input(component_id='date-picker', component_property='value'),  # Take date-picker date
        Input(component_id='users-dates-formatted', component_property='data'),
        Input(component_id='scenarios-sorted', component_property='data'),
        Input(component_id='graph-unit', component_property='data'),  # Stores the graph unit (y axis legend)
        Input(component_id='users-dates-raw', component_property='data'),
        Input(component_id='range-arpu-growth', component_property='value'),
        Input(component_id='current-arpu-stored', component_property='data'),
        State(component_id='symbol-dataset', component_property='data'),
        State(component_id='dataset-selection', component_property='value'),  # Take dropdown value
        State(component_id='max-net-margin', component_property='data'),  # Take dropdown value
    ], prevent_initial_call=True)
def graph_update(data_slider, date_picked_formatted_original, df_dataset_dict, df_scenarios_dict, graph_unit, df_raw,
                 arpu_growth, current_arpu, symbol_dataset, dropdown_value, max_net_margin):
    # --------- Data Loading
    t1 = time.perf_counter(), time.process_time()
    # Data prepared earlier is fetched here
    # Dates array definition from dictionary
    dates = np.array([entry['Date'] for entry in df_dataset_dict])
    dates_raw = np.array([entry['Date'] for entry in df_raw])
    users_raw = np.array([entry['Users'] for entry in df_raw]) * 1e6
    dates = dates - 1970
    # Users are taken from the database and multiply by a million
    users = np.array([entry['Users'] for entry in df_dataset_dict])
    users = users.astype(float) * 1000000
    arpu_growth = arpu_growth / 100

    # R&D
    research_and_development = np.array([entry['Research_And_Development'] for entry in df_dataset_dict]) * 1_000_000

    # Profit Margin Array
    profit_margin_array = np.array([entry['Profit Margin'] for entry in df_dataset_dict])
    print("ProfitMargin", profit_margin_array)

    # Gets the date selected from the new date picker
    date_picked_formatted = main.date_formatting_from_string(date_picked_formatted_original)
    history_value = date_picked_formatted
    history_value_graph = datetime.strptime(date_picked_formatted_original, "%Y-%m-%d")
    # Extract the x-coordinate for the vertical line
    x_coordinate = history_value_graph

    # Calculating the length of historical values to be considered in the plots
    # history_value_formatted = history_value[0] - 1970  # Puts back the historical value to the format for computations
    history_value_formatted = date_picked_formatted - 1970  # New slider: Puts back the historical value to the format for computations
    dates_actual = main.get_earlier_dates(dates, history_value_formatted)
    data_len = len(dates_actual)  # length of the dataset to consider for retrofitting
    users_actual = users[0:data_len]

    print("Selected date", date_picked_formatted)
    print(graph_unit)

    # If selecting all possible scenarios,  Creation of the arrays of parameters
    k_scenarios = np.array([entry['K'] for entry in df_scenarios_dict])
    r_scenarios = np.array([entry['r'] for entry in df_scenarios_dict])
    p0_scenarios = np.array([entry['p0'] for entry in df_scenarios_dict])
    rsquared_scenarios = np.array([entry['R Squared'] for entry in df_scenarios_dict])
    moving_average_scenarios = np.array([entry['Moving Average'] for entry in df_scenarios_dict])
    number_ignored_data_scenarios = np.array([entry['Data Ignored'] for entry in df_scenarios_dict])

    # Based on the slider's value, the related row of parameters is selected
    row_selected = data_slider
    # Parameters definition
    k = k_scenarios[row_selected]
    r = r_scenarios[row_selected]
    p0 = p0_scenarios[row_selected]
    moving_average = moving_average_scenarios[row_selected]
    print("movingaverage", moving_average)
    r_squared_showed = np.round(rsquared_scenarios[row_selected], 3)
    number_ignored_data = int(number_ignored_data_scenarios[row_selected])

    # R^2 Ring progress definition of the selected prediction line
    value_section = r_squared_showed * 100
    if r_squared_showed > 0.9:
        sections = [
            {"value": value_section, "color": "Green", "tooltip": "Very Good Trend Fit"},
        ]
    elif 0.6 < r_squared_showed <= 0.9:
        sections = [
            {"value": value_section, "color": "LightGreen", "tooltip": "Good Trend Fit"},
        ]

    elif 0.4 < r_squared_showed <= 0.6:
        sections = [
            {"value": value_section, "color": "Yellow", "tooltip": "Medium Trend Fit"},
        ]

    elif r_squared_showed <= 0.4:
        sections = [
            {"value": value_section, "color": "Red", "tooltip": "Inaccurate Trend Fit"},
        ]

    else:
        sections = [
            {"value": value_section, "color": "LightGrey", "tooltip": "Computation issue"},
        ]

    print("Value Ring", value_section, r_squared_showed)

    highest_r2_index = np.argmax(rsquared_scenarios)
    print("HIGHEST", highest_r2_index)

    # Graph message

    # Selected Growth
    if k_scenarios[data_slider] < 1e6:
        plateau_selected_growth = f"{k_scenarios[data_slider]:.0f}"
    elif k_scenarios[data_slider] < 1e9:
        plateau_selected_growth = f"{k_scenarios[data_slider] / 1e6:.1f} M"
    else:
        plateau_selected_growth = f"{k_scenarios[data_slider] / 1e9:.1f} B"
    time_selected_growth = main.time_to_population(k_scenarios[data_slider],
                                                   r_scenarios[data_slider],
                                                   p0_scenarios[data_slider],
                                                   k_scenarios[data_slider] * 0.9) + 1970

    graph_message = "The pink bars show how "+ dropdown_value +"’s " + graph_unit + " (the key revenue driver) have " \
                   "grown over time. The yellow zone is our forecast range, " \
                     "showing how this driver should evolve in the future. These drivers follow an S-curve: " \
                    "fast growth at first, then a gradual slowdown.\n" \
                    " With the selected growth, the plateau will be approaching as of " \
                    + main.string_formatting_to_date(time_selected_growth) + ", projected at " \
                    + str(plateau_selected_growth) + " " + str(graph_unit)

    # Build Main Chart
    # ---------------------
    hovertemplate_maingraph = "%{text}"
    fig_main = go.Figure(layout=layout_main_graph)

    x_axis = [dates[0] + 1970, dates[-1] * 2 - dates[0] + 1970]
    # fig_main.update_xaxes(range=x_axis)  # Fixing the size of the X axis with users max + 10%
    # Historical data
    # Highlight points considered for the approximation
    fig_main.add_trace(go.Bar(name="Dataset", x=dates_raw[number_ignored_data:data_len],
                              y=users[number_ignored_data:data_len],
                              marker_color='#FFA8FB',
                              showlegend=False,
                              hoverinfo='none'
                              ))
    y_predicted = users
    formatted_y_values = [
        f"{y:.3f}" if y < 1e6 else f"{y / 1e6:.3f} M" if y < 1e9 else f"{y / 1e9:.3f} B"
        for y in y_predicted
    ]
    # Line linking the historical data for smoothing the legend hover
    fig_main.add_trace(go.Scatter(name="Historical data", x=dates_raw,
                                  y=y_predicted, mode='lines', opacity=0,
                                  marker_color='#FFA8FB', text=formatted_y_values, hovertemplate=hovertemplate_maingraph))
    # Highlight points not considered for the approximation
    fig_main.add_trace(
        go.Bar(name="Data omitted", x=dates_raw[0:number_ignored_data], y=users[0:number_ignored_data],
               marker_color="#FFA8FB", hoverinfo='none', showlegend=False))
    # Highlight points past the current date
    fig_main.add_trace(go.Bar(name="Future data", x=dates_raw[data_len:],
                              y=users[data_len:],
                              marker_color='#e6ecf5', hoverinfo='none', ))

    # Add vertical line indicating the year of the prediction for retrofitting
    # fig_main.add_vline(x=history_value_graph, line_width=1, line_dash="dot",
    # opacity=0.5, annotation_text="   Forecast")
    fig_main.add_shape(
        go.layout.Shape(
            type="line",
            x0=x_coordinate,
            x1=x_coordinate,
            y0=0,
            y1=k_scenarios[-1],
            line=dict(color="gray", width=1, dash="dot"),
        )
    )
    # Update layout to customize the annotation
    if k_scenarios[-1] > users_raw[-1]:
        range_y = [0, main.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1], [60])[0] * 1.5]
    else:
        range_y = [0, users_raw[-1] * 1.2]

    print("range_y", range_y)
    fig_main.update_layout(
        hovermode="x unified",
        annotations=[
            dict(
                x=(x_coordinate + relativedelta(months=9)).strftime("%Y-%m-%d"),
                y=0.9 * k_scenarios[-1],
                text="F O R E C A S T",
                showarrow=False,
                font=dict(size=8, color="black"),
                opacity=0.5,
            )
        ],
        yaxis=dict(
            title=graph_unit,
        ),
        margin=dict(t=40, b=10, l=5, r=5),
    )

    # Prediction, S-Curves

    date_a = datetime.strptime(dates_raw[0], "%Y-%m-%d")
    #date_b = datetime.strptime(dates_raw[-1], "%Y-%m-%d")
    date_b = datetime.strptime(dates_raw[len(dates_actual)-1], "%Y-%m-%d")

    #date_b_actual = history_value_graph  # Date including the datepicker
    date_b_actual = dates_actual[-1]

    # Calculate date_end using the formula date_b + 2 * (date_b - date_a)
    date_end = date_b + (date_b - date_a)

    date_end_formatted = main.date_formatting_from_string(date_end.strftime("%Y-%m-%d"))

    # Add S-curve - S-Curve the user can play with
    x = np.linspace(dates[0], float(date_end_formatted) - 1970, num=50)


    x_scenarios = np.linspace(dates_actual[-1], float(date_end_formatted) - 1970, num=50) # changed
    y_predicted = main.logisticfunction(k, r, p0, x_scenarios)
    # Generate x_dates array
    x_dates = np.linspace(date_a.timestamp(), date_end.timestamp(), num=50)
    x_dates_scenarios = np.linspace(date_b.timestamp(), date_end.timestamp(), num=50) # changed
    x_dates = [datetime.fromtimestamp(timestamp) for timestamp in x_dates]
    x_dates_scenarios = [datetime.fromtimestamp(timestamp) for timestamp in x_dates_scenarios]



    formatted_y_values = [
        f"{y:.3f}" if y < 1e6 else f"{y / 1e6:.3f} M" if y < 1e9 else f"{y / 1e9:.3f} B"
        for y in y_predicted
    ]

    # Growth forecast line
    fig_main.add_trace(go.Scatter(name="Growth Forecast", x=x_dates_scenarios, y=y_predicted,
                                  mode="lines", line=dict(color='#FFD000', width=2), opacity=0.8,
                                  text=formatted_y_values, hovertemplate=hovertemplate_maingraph))
    # Add 3 scenarios
    x0 = np.linspace(dates_actual[-1] + 0.25, dates_actual[-1] * 2 - dates_actual[0],
                     num=10)  # Creates a future timeline the size of the data

    # Low growth scenario
    # x = np.linspace(dates[-1], dates[-1] * 2 - dates[0], num=50)
    y_trace = main.logisticfunction(k_scenarios[0], r_scenarios[0], p0_scenarios[0], x_scenarios)
    formatted_y_values = [
        f"{y:.3f}" if y < 1e6 else f"{y / 1e6:.3f} M" if y < 1e9 else f"{y / 1e9:.3f} B"
        for y in y_trace
    ]
    fig_main.add_trace(go.Scatter(name="Low Growth", x=x_dates_scenarios,
                                  y=main.logisticfunction(k_scenarios[0], r_scenarios[0], p0_scenarios[0], x_scenarios),
                                  mode='lines',
                                  line=dict(color='#C58400', width=0.5), showlegend=False, text=formatted_y_values,
                                  hovertemplate=hovertemplate_maingraph)),
    # fig.add_trace(go.Line(name="Predicted S Curve", x=x + 1970,
    # y=main.logisticfunction(k_scenarios[1], r_scenarios[1], p0_scenarios[1], x), mode="lines"))
    y_trace = main.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1], x_scenarios)
    formatted_y_values = [
        f"{y:.3f}" if y < 1e6 else f"{y / 1e6:.3f} M" if y < 1e9 else f"{y / 1e9:.3f} B"
        for y in y_trace
    ]
    # High growth scenario, if existent
    if len(k_scenarios) > 1:
        fig_main.add_trace(go.Scatter(name="High Growth", x=x_dates_scenarios,
                                      y=y_trace, mode='lines',
                                      line=dict(color='#C58400', width=0.5),
                                      textposition="top left", textfont_size=6, showlegend=False,
                                      text=formatted_y_values, hovertemplate=hovertemplate_maingraph))
    years_future_users = list(range(2023 - 1970, 2039 - 1970))

    # Filling the area of possible scenarios
    x_area = np.append(x, np.flip(x))  # Creating one array made of two Xs
    y_area_low = main.logisticfunction(k_scenarios[0], r_scenarios[0], p0_scenarios[0], x_scenarios)  # Low growth array
    y_area_high = main.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1],
                                        np.flip(x_scenarios))  # High growth array
    y_area = np.append(y_area_low, y_area_high)
    dates_area = np.append(x_dates_scenarios, np.flip(x_dates_scenarios))
    fig_main.add_trace(go.Scatter(x=dates_area,
                                  y=y_area,
                                  fill='toself',
                                  line_color='#C58400',
                                  fillcolor='#FFD000',
                                  opacity=0.1,
                                  hoverinfo='none',
                                  showlegend=False,
                                  )
                       )

    # Adding RAST logo
    fig_main.add_layout_image(
        dict(
            source="/assets/RAST_Vector_Logo_black.svg",  # Replace with your image URL or base64-encoded image
            xref="paper",  # Reference the image to the plot area
            yref="paper",
            x=1.0,  # Position the image at the bottom-right corner (1.0 means the right edge of the figure)
            y=0.01,  # Position the image at the bottom (0.0 means the bottom edge of the figure)
            xanchor="right",  # Align the image to the right
            yanchor="bottom",  # Align the image to the bottom
            sizex=0.1,  # Adjust the width of the image
            sizey=0.1,  # Adjust the height of the image
            layer="above"  # Place the image above the plot elements
        )
    )
    print("Userbase Graph printed")
    print("Image created")

    x1 = np.linspace(dates[-1] + 0.25, dates[-1] + 10, num=10)
    # Add predicted bars
    # marker_color='White', marker_line_color='Black'))

    # Build second chart containing the discrete growth rates & Regressions
    # -------------------------------------------------------

    fig_second = go.Figure(layout=layout_growth_rate_graph)
    fig_second.update_xaxes(range=[0, users[-1] * 1.1], title=graph_unit)  # Fixing the size of the X axis with users max + 10%
    dates_moved, users_moved = main.moving_average_smoothing(dates, users, moving_average)

    #Defining the min as zero or less if the minimum is negative
    if min(main.discrete_growth_rate(users_moved, dates_moved + 1970)-0.05) > 0:
        fig_second.update_yaxes(range=[0,
                                       max(main.discrete_growth_rate(users_moved, dates_moved + 1970)+0.05)])
    else:
        fig_second.update_yaxes(range=[min(main.discrete_growth_rate(users_moved, dates_moved + 1970) - 0.05),
                                       max(main.discrete_growth_rate(users_moved, dates_moved + 1970) + 0.05)])
    fig_second.add_trace(
        go.Scatter(name="Discrete Growth Rate Smoothened by moving average: " + str(moving_average),
                x = main.discrete_user_interval(users_moved),
                y = main.discrete_growth_rate(users_moved, dates_moved + 1970), mode = "markers", line = dict(color='#F963F1')
                   ))
    print(users, dates + 1970)
    print(main.discrete_growth_rate(users, dates + 1970))
    # Add trace of the regression
    fig_second.add_trace(
        go.Scatter(name="Regression", x=main.discrete_user_interval(users),
                   y=-r / k * main.discrete_user_interval(users) + r, mode="lines", line=dict(color='#953AF6')))

    if number_ignored_data > 0:
        fig_second.add_trace(
            go.Scatter(name="Ignored Data Points", x=main.discrete_user_interval(users_moved[0:number_ignored_data]),
                       y=main.discrete_growth_rate(users_moved[0:number_ignored_data], dates_moved[0:number_ignored_data] + 1970),
                       mode="markers", line=dict(color='#808080')))

    # Changes the color of the scatters after the date considered
    if data_len < len(dates):
        fig_second.add_trace(
            go.Scatter(name="Discrete Growth Rate", x=main.discrete_user_interval(users[data_len:]),
                       y=main.discrete_growth_rate(users[data_len:], dates[data_len:] + 1970),
                       mode="markers", line=dict(color='#e6ecf5')))

    # Adding RAST logo
    fig_second.add_layout_image(
        dict(
            source="/assets/RAST_Vector_Logo_black.svg",  # Replace with your image URL or base64-encoded image
            xref="paper",  # Reference the image to the plot area
            yref="paper",
            x=0.99,  # Position the image at the bottom-right corner (1.0 means the right edge of the figure)
            y=0.9,  # Position the image at the bottom (0.0 means the bottom edge of the figure)
            xanchor="right",  # Align the image to the right
            yanchor="bottom",  # Align the image to the bottom
            sizex=0.1,  # Adjust the width of the image
            sizey=0.1,  # Adjust the height of the image
            layer="above"  # Place the image above the plot elements
        )
    )
    fig_second.add_shape(
        type="line",
        x0=0,
        x1=users[-1]*1.1,
        y0=0,
        y1=0,
        line=dict(color="black", width=1, dash="dot")
    )
    fig_second.update_layout(
        annotations=[
            dict(
                x=users[0],
                y=0.01,
                text="G R O W T H  E N D",
                showarrow=True,
                font=dict(size=8, color="black"),
                opacity=0.5,
            )
        ]
    )

    # Carrying capacity to be printed
    k_printed = int(np.rint(k) / pow(10, 6))
    k_printed = "{:,} M".format(k_printed)
    # PLATEAU: Time when the plateau is reached, assuming the plateau is "reached" when p(t)=95%*K
    print(p0)
    if p0 > 2.192572e-11:
        t_plateau = main.time_to_population(k, r, p0, 0.95 * k) + 1970
        month_plateau = math.ceil((t_plateau - int(t_plateau)) * 12)
        year_plateau = int(np.round(t_plateau, 0))
        date_plateau = datetime(year_plateau, month_plateau, 1).date()
        date_plateau_displayed = date_plateau.strftime("%b, %Y")
        t_plateau_displayed = 'Year {:.1f}'.format(t_plateau)
        print("Plateau calculated correctly")
    else:
        date_plateau_displayed = "Plateau could not be calculated"

    # Build chart containing the ARPU evolution chart

    # All subsequent graphs are relevant to companies with revenue
    # For now, it is assumed that two categories exist: publically traded companies and any other dataset
    # For 'any other dataset', no revenue is printed

    symbol_company = symbol_dataset
    if symbol_company != "N/A":

        # REVENUE Lines
        revenue = np.array([entry['Revenue'] for entry in df_dataset_dict]) * 1_000_000
        # Find the indices where cells in the second array are not equal to "N/A"
        valid_indices = np.where(revenue != 0)

        years = 6
        current_date = datetime.now()
        future_arpu = [current_arpu * (1 + arpu_growth) ** year for year in range(years)]
        future_arpu_dates = [datetime.strptime(date_picked_formatted_original, '%Y-%m-%d') + timedelta(days=365 * year)
                             for
                             year in range(years)]
        fig_revenue = make_subplots(specs=[[{"secondary_y": True}]])


        # Filter rows based on valid indices
        dates_revenue = dates_raw[valid_indices]
        users_revenue = users[valid_indices]
        dates_revenue_actual = main.get_earlier_dates(dates[valid_indices], history_value_formatted)
        # users_revenue_actual = main.get_earlier_dates(users_revenue, history_value_formatted)
        data_len_revenue_array = dates_raw[data_len:]
        revenue = revenue[valid_indices]
        research_and_development = research_and_development[valid_indices]
        dates_research_and_development = dates_raw[valid_indices]
        if len(revenue) > 0:
            annual_revenue_per_user = revenue * 4 / users_revenue
            x_revenue = dates_revenue
            y_revenue = annual_revenue_per_user
            formatted_y_values = [f"${y:.1f}" if y < 1000 else f"${y / 1e3:.2f} K" for y in y_revenue]
            # Past revenue outline to increase the contrast
            fig_revenue.add_trace(go.Bar(
                name="Annual Revenue per User (arpu)",
                x=x_revenue,
                y=y_revenue,
                #mode='lines',
                marker_color='#953AF6',
                opacity=0.8,
                #showlegend=False,
                # text=formatted_y_values,
                # hovertemplate=hovertemplate_maingraph
            ),
                #secondary_y=True,
            )
            fig_revenue.add_trace(go.Scatter(
                name="Future Annual Revenue per User (arpu)",
                x=future_arpu_dates,
                y=future_arpu,
                mode='lines',
                line_dash="dot",
                marker=dict(color='#FFD000', size=4),
                showlegend=True,
                text=formatted_y_values,
                hovertemplate=hovertemplate_maingraph),
                #secondary_y=True,
            )
            # Revenue past the selected date that are known [data_len:]
            fig_revenue.add_trace(go.Scatter(
                name="Annual Revenue per User or Unit (ARPU)",
                x=x_revenue[len(dates_revenue_actual):],
                y=y_revenue[len(dates_revenue_actual):],
                mode='lines',
                line=dict(color='Gray', width=1),
                showlegend=False,
                # text=formatted_y_values, #
                hovertemplate=hovertemplate_maingraph),
                #secondary_y=True,
            )
            fig_revenue.update_yaxes(range=[min(annual_revenue_per_user) * 0.9, max(annual_revenue_per_user) * 1.5],
                                  title="Annual Revenue per " + graph_unit + " [$]",
                                  color="#953AF6")
            fig_revenue.add_trace(go.Scatter(
                name="Profit Margin",
                x=x_revenue,
                y=profit_margin_array[valid_indices],
                mode='lines',
                #line_dash="dot",
                marker=dict(color='#F963F1', size=4),
                showlegend=True,
                #text=formatted_y_values,
                #hovertemplate=hovertemplate_maingraph
            ),
                secondary_y=True,
            )
            # adding max net margin horizontal line
            fig_revenue.add_shape(
                type="line",
                x0=x_revenue[0],
                x1=future_arpu_dates[-1],
                y0=max_net_margin,
                y1=max_net_margin,
                xref="x",  # link to x-axis
                yref="y2",  # link to secondary y-axis
                line=dict(color="pink", width=1, dash="dot"),
            )
            fig_revenue.update_layout(
                layout_revenue_graph,
                annotations=[
                    dict(
                        x=future_arpu_dates[3],
                        y=max_net_margin,
                        text="M A X  N E T  M A R G I N",
                        showarrow=False,
                        font=dict(size=8, color="#46052A"),
                        opacity=0.5,
                        yref="y2"
                    )
                ]
            )

            fig_revenue.update_yaxes(range=[min(profit_margin_array)-abs(min(profit_margin_array)) * 0.1,
                                            max_net_margin*1.2],
                                  title_text="Profit Margin [%]",
                                  color="#F963F1",
                                  secondary_y=True,
                                fixedrange=True,
                                     )
            print("Fig Revenue Printed")

            # Adding RAST logo
            fig_revenue.add_layout_image(
                dict(
                    source="/assets/RAST_Vector_Logo_black.svg",  # Replace with your image URL or base64-encoded image
                    xref="paper",  # Reference the image to the plot area
                    yref="paper",
                    x=0.93,  # Position the image at the bottom-right corner (1.0 means the right edge of the figure)
                    y=0.01,  # Position the image at the bottom (0.0 means the bottom edge of the figure)
                    xanchor="right",  # Align the image to the right
                    yanchor="bottom",  # Align the image to the bottom
                    sizex=0.1,  # Adjust the width of the image
                    sizey=0.1,  # Adjust the height of the image
                    layer="above"  # Place the image above the plot elements
                )
            )

        else:
            print("No revenue to be added to the graph")
    else:
        fig_revenue = fig_main


    if symbol_company != "N/A":
        # Build chart containing the product maturity chart
        # -------------------------------------------------------
        dates_research_and_development = pd.to_datetime(dates_research_and_development)
        share_research_and_development = research_and_development / revenue * 100
        fig_product_maturity = go.Figure(layout=layout_product_maturity_graph)
        fig_product_maturity.update_yaxes(range=[0, 100])  # Fixing the size of the X axis with users max + 10%

        # Add horizontal lines delimitating the different phases:
        # 1) Early-stage product >20% 2) Growth-Stage [10-20%] 3) Mature-Stage [<10%]
        # Mature company
        fig_product_maturity.add_shape(
            go.layout.Shape(
                type="rect",
                x0=(dates_research_and_development[0]-pd.DateOffset(months=6)).strftime('%Y-%m-%d'),
                x1=(dates_research_and_development[-1]+pd.DateOffset(months=6)).strftime('%Y-%m-%d'),
                y0=0,
                y1=10,
                #xref="paper", yref="y",
                fillcolor="#4946F2",
                opacity=0.3,
                layer="below",
                line_width=0,
            )
        )
        # Add the annotation
        fig_product_maturity.add_annotation(
            x=(dates_research_and_development[0] - pd.DateOffset(months=6)).strftime('%Y-%m-%d'),
            # Align left within the rectangle
            y=(0 + 10) / 2,  # Center vertically within the rectangle
            xref="x",
            yref="y",
            text="  Mature Product",
            showarrow=False,
            font=dict(color="#4946F2", size=12),
            align="left",
            xanchor="left",
            # bgcolor="rgba(231, 245, 255, 0.8)"  # Matching background color for better visibility
        )

        # Growth company
        fig_product_maturity.add_shape(
            go.layout.Shape(
                type="rect",
                x0=(dates_research_and_development[0] - pd.DateOffset(months=6)).strftime('%Y-%m-%d'),
                x1=(dates_research_and_development[-1] + pd.DateOffset(months=6)).strftime('%Y-%m-%d'),
                y0=10,
                y1=30,
                # xref="paper", yref="y",
                fillcolor="#4946F2",
                opacity=0.2,
                layer="below",
                line_width=0,
            )
        )
        # Add the annotation
        fig_product_maturity.add_annotation(
            x=(dates_research_and_development[0] - pd.DateOffset(months=6)).strftime('%Y-%m-%d'),
            # Align left within the rectangle
            y=(10 + 30) / 2,  # Center vertically within the rectangle
            xref="x",
            yref="y",
            text="  Product Stabilization",
            showarrow=False,
            font=dict(color="#4946F2", size=12),
            align="left",
            xanchor="left",
            # bgcolor="rgba(231, 245, 255, 0.8)"  # Matching background color for better visibility
        )

        # High growth company
        fig_product_maturity.add_shape(
            go.layout.Shape(
                type="rect",
                x0=(dates_research_and_development[0] - pd.DateOffset(months=6)).strftime('%Y-%m-%d'),
                x1=(dates_research_and_development[-1] + pd.DateOffset(months=6)).strftime('%Y-%m-%d'),
                y0=30,
                y1=100,
                # xref="paper", yref="y",
                fillcolor="#4946F2",
                opacity=0.1,
                layer="below",
                line_width=0,
            )
        )
        # Add the annotation
        fig_product_maturity.add_annotation(
            x=(dates_research_and_development[0] - pd.DateOffset(months=6)).strftime('%Y-%m-%d'),  # Align left within the rectangle
            y=(30 + 100) / 2,  # Center vertically within the rectangle
            xref="x",
            yref="y",
            text="  Heavy Product Investments",
            showarrow=False,
            font=dict(color="#4946F2", size=12),
            align="left",
            xanchor="left",
            #bgcolor="rgba(231, 245, 255, 0.8)"  # Matching background color for better visibility
        )
        # Add graph line
        formatted_y_values = [
            f"{y:.2f}%"for y in share_research_and_development
        ]
        fig_product_maturity.add_trace(
            go.Scatter(name="R&D Share of Revenue [%]",
                       x=dates_research_and_development,
                       y=share_research_and_development,
                       text=formatted_y_values,
                       hovertemplate=hovertemplate_maingraph,
                       mode="markers",
                       marker=dict(
                            color="#FFD000",       # Fill color with some transparency (tomato color here)
                            size=10,                              # Size of the markers
                            line=dict(
                                color="#C58400",         # Outline color (black in this example)
                                width=1                           # Width of the outline
                            )
                        )
                       ))
        # Adding RAST logo
        fig_product_maturity.add_layout_image(
            dict(
                source="/assets/RAST_Vector_Logo_black.svg",  # Replace with your image URL or base64-encoded image
                xref="paper",  # Reference the image to the plot area
                yref="paper",
                x=0.99,  # Position the image at the bottom-right corner (1.0 means the right edge of the figure)
                y=0.9,  # Position the image at the bottom (0.0 means the bottom edge of the figure)
                xanchor="right",  # Align the image to the right
                yanchor="bottom",  # Align the image to the bottom
                sizex=0.1,  # Adjust the width of the image
                sizey=0.1,  # Adjust the height of the image
                layer="above"  # Place the image above the plot elements
            )
        )
    else:
        fig_product_maturity = fig_main



    print("2. CALLBACK END")
    t2 = time.perf_counter(), time.process_time()
    print(f" Creating graph")
    print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
    return fig_main, fig_revenue, fig_second, fig_product_maturity, sections, graph_message


# Callback displaying the functionalities & graph cards, and hiding the text
@app.callback(
    Output(component_id="graph-card-content", component_property='style'),
    Output(component_id='functionalities-card', component_property='style'),
    Output(component_id='welcome-timeline', component_property='style'),
    Output(component_id='launch-counter', component_property='data'),
    Input(component_id='dataset-selection', component_property='value'),
    [State('launch-counter', 'data')]
    , prevent_initial_call=True
)
def show_cards(data, launch_counter):
    if launch_counter['flag'] is not True:
        launch_counter['flag'] = True
        show_graph_card = {'display': 'block'}
        hide_graph_card = {'display': 'none'}
        print("Displaying the graph hihi")
        return show_graph_card, show_graph_card, hide_graph_card, launch_counter

    else:
        print("Card already displayed", launch_counter)
        raise PreventUpdate


# Callback calculating the ARPU needed depending on the chosen scenario
@app.callback(
    Output(component_id="arpu-needed", component_property="children"),
    [
        Input(component_id='scenarios-sorted', component_property='data'),
        Input("range-profit-margin", "value"),
        Input("range-discount-rate", "value"),
        Input("range-slider-k", "value"),
        Input(component_id='current-market-cap', component_property='data'),
        Input(component_id='current-arpu-stored', component_property='data'),
    ], prevent_initial_call=True
)
def calculate_arpu(df_sorted, profit_margin, discount_rate, row_index, current_market_cap, current_arpu):
    # The entire callback is skipped if the current market cap = 0, i.e. if it is not a public company
    t1 = time.perf_counter(), time.process_time()

    if current_market_cap == 0:
        raise PreventUpdate
    k_selected = df_sorted[row_index]['K']
    r_selected = df_sorted[row_index]['r']
    p0_selected = df_sorted[row_index]['p0']
    profit_margin = profit_margin / 100
    discount_rate = discount_rate / 100
    YEARS_DCF = 10
    current_market_cap = current_market_cap * 1000000
    # Ignored to avoid calculating this. Can be discommented to reuse this function
    # arpu_needed = main.arpu_for_valuation(k_selected, r_selected, p0_selected, profit_margin, discount_rate, YEARS_DCF, current_market_cap)
    arpu_needed = 0
    arpu_difference = arpu_needed / current_arpu
    printed_arpu = f"{arpu_needed:.0f} $. The current arpu " + f"({current_arpu:.0f} $)" + " should be multiplied by " + f"{arpu_difference:.2f}!"  # formatting

    t2 = time.perf_counter(), time.process_time()
    print(f" Performance of the valuation over time")
    print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")

    return printed_arpu


# Callback Adapting the Hype-meter
@app.callback(
    Output(component_id="hype-meter-noa", component_property="value"),
    Output(component_id="hype-tooltip-noa", component_property="children"),
    Output(component_id="hype-meter-users", component_property="value"),
    Output(component_id="hype-tooltip-users", component_property="children"),
    Output(component_id="hype-meter-hype", component_property="value"),
    Output(component_id="hype-tooltip-hype", component_property="children"),
    Output(component_id="hype-meter-indicator", component_property="color"),
    Output(component_id="hype-meter-indicator", component_property="children"),
    Output(component_id="current-valuation-calculated", component_property="data"),
    Output(component_id="hype-meter-undervaluation-hype", component_property="value"),  # Progress 1 colored value (hype)
    Output(component_id="hype-meter-undervaluation-hype", component_property="color"),  # Progress 1 color
    Output(component_id="hype-meter-undervaluation-rest", component_property="value"), # Progress 1 white part
    Output(component_id="hype-meter-price", component_property="value"),
    Output(component_id="hype-meter-price-rest", component_property="value"),
    Output(component_id="hype-overvaluation-label", component_property="children"),
    [
        Input(component_id='scenarios-sorted', component_property='data'),
        Input("range-profit-margin", "value"),
        Input("range-discount-rate", "value"),
        Input("range-slider-k", "value"),
        Input("range-arpu-growth", "value"),
        Input(component_id='current-market-cap', component_property='data'),
        Input(component_id='latest-market-cap', component_property='data'),
        Input(component_id='current-arpu-stored', component_property='data'),
        Input(component_id='total-assets', component_property='data'),
        Input(component_id='users-dates-formatted', component_property='data'),
        State(component_id='graph-unit', component_property='data')
    ], prevent_initial_call=True
)
def calculate_arpu(df_sorted, profit_margin, discount_rate, row_index, arpu_growth, current_market_cap, latest_market_cap, current_arpu,
                   total_assets, df_dataset_dict, graph_unit):
    t1 = time.perf_counter(), time.process_time()
    # The entire callback is skipped if the current market cap = 0, i.e. if it is not a public company
    if current_market_cap == 0:
        raise PreventUpdate
    # Parameters definition
    users = np.array([entry['Users'] for entry in df_dataset_dict]) * 1_000_000
    k_selected = df_sorted[row_index]['K']
    r_selected = df_sorted[row_index]['r']
    p0_selected = df_sorted[row_index]['p0']
    profit_margin = profit_margin / 100
    discount_rate = discount_rate / 100
    arpu_growth = arpu_growth / 100
    current_market_cap = latest_market_cap * 1000000
    graph_unit_text = str(graph_unit)

    # Equity calculation
    current_customer_equity = users[-1] * current_arpu * profit_margin
    future_customer_equity = main.net_present_value_arpu_growth(k_selected, r_selected, p0_selected, current_arpu,
                                                                arpu_growth, profit_margin, discount_rate, YEARS_DCF)
    total_customer_equity = current_customer_equity + future_customer_equity
    non_operating_assets = total_assets

    current_valuation = total_customer_equity + non_operating_assets
    hype_total = current_market_cap - total_customer_equity - non_operating_assets

    # Calculating the values of the hype meter
    non_operating_assets_ratio = non_operating_assets / current_market_cap * 100
    noa_tooltip = f"Non-Operating Assets: ${total_assets / 1e9:.2f} B. \n They represent additional valuable company " \
                  f"assets, such as Goodwill"
    customer_equity_ratio = total_customer_equity / current_market_cap * 100
    customer_equity_tooltip = f"Intrinsic value: ${total_customer_equity / 1e9:.2f} B. The value attributed to the " \
                              f"'{graph_unit_text}', " \
                              f"computed using a DCF approach."
    # 3 Progress bars are displayed
    # Progress 1: hype_ratio & hype_ratio_rest bar
    # -> under_valuation shows hype/overvaluation, under_valuation_rest is the white part on the left
    # Progress 2: intrinsic_value bar
    # -> non_operating_assets_ratio, customer_equity_ratio (colored) & intrinsic_value_rest (white)
    # Progress 3: price (market cap) bar
    # -> only shows price if hype > 0, shows price and the price_rest_ratio if hype < 0
    hype_ratio = hype_total / current_market_cap * 100
    hype_ratio_absolute = abs(hype_ratio)

    if hype_total >= 0.0:
        # Progress 1
        hype_ratio_progress = hype_ratio_absolute
        hype_ratio_rest = 100 - hype_ratio_absolute
        hype_color_indicator = "#fa5252"    # red
        # Progress 2
        intrinsic_value_ratio_rest = 100 - (non_operating_assets_ratio + customer_equity_ratio)   # white part of the intrinsic value bar
        # Progress 3
        price_rest_ratio = 0.0
        current_market_cap_ratio = 100  # the price bar is full if hype is positive
        text_overvaluation = "Overvaluation"
    # if hype is negative
    else:
        # Progress 1
        hype_ratio_progress = hype_ratio_absolute
        hype_ratio_rest = 100 - hype_ratio_absolute
        hype_color_indicator = "#40c057"    # green
        # Progress 2
        intrinsic_value_ratio_rest = 0.0
        # Progress 3
        current_market_cap_ratio = hype_ratio_rest
        price_rest_ratio = 100 - current_market_cap_ratio
        text_overvaluation = "Undervaluation"

    hype_tooltip = f"Hype: ${hype_total / 1e9:.2f} B.  It reflects the current overvaluation of the company in terms " \
                   f"of market capitalization versus actual value."
    hype_indicator_color, hype_indicator_text = main.hype_meter_indicator_values(hype_ratio / 100)
    t2 = time.perf_counter(), time.process_time()
    print(f" Performance of the valuation over time")
    print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")

    return non_operating_assets_ratio, noa_tooltip, customer_equity_ratio, customer_equity_tooltip, intrinsic_value_ratio_rest, \
        hype_tooltip, hype_indicator_color, hype_indicator_text, current_valuation, hype_ratio_progress, hype_indicator_color, hype_ratio_rest, \
        current_market_cap_ratio, price_rest_ratio, text_overvaluation


# Callback calculating the valuation over time and displaying the functionalities & graph cards, and hiding the text
@app.callback(
    Output(component_id='data-selection-counter', component_property='data', allow_duplicate=True),
    Output(component_id='valuation-over-time', component_property='data'),
    Output("loader-general", "style", allow_duplicate=True),
    # Input(component_id='date-picker', component_property='value'),  # Take date-picker date
    Input(component_id='users-dates-formatted', component_property='data'),
    Input(component_id='total-assets', component_property='data'),
    Input(component_id='users-dates-raw', component_property='data'),
    Input(component_id='latest-market-cap', component_property='data'),  # Stores the current (now) company market cap
    # State(component_id='valuation-over-time', component_property='data'),
    State(component_id='max-net-margin', component_property='data'),
    [State('data-selection-counter', 'data')]
    , prevent_initial_call=True
)
def historical_valuation_calculation(df_formatted, total_assets, df_raw, latest_market_cap, max_net_margin,
                                     df_rawdataset_counter):
    print("Dataset Flag")
    print(max_net_margin)
    print(type(max_net_margin))
    print(df_rawdataset_counter)
    max_net_margin = max_net_margin/100
    # The entire callback is skipped if the current market cap = 0, i.e. if it is not a public company OR
    # if it was already calculated
    if latest_market_cap == 0 or df_rawdataset_counter == False:
        raise PreventUpdate
    t1 = time.perf_counter(), time.process_time()
    dates_raw = np.array([entry['Date'] for entry in df_raw])
    dates_new = np.array([entry['Date'] for entry in df_formatted])
    revenue_df = np.array([entry['Revenue'] for entry in df_formatted])
    profit_margin_df = np.array([entry['Profit Margin'] for entry in df_formatted])
    profit_margin_original = profit_margin_df / 100
    market_cap_df = np.array([entry['Market Cap'] for entry in df_formatted])
    market_cap_original = market_cap_df*1e9
    dates_original = dates_new - 1970
    # Users are taken from the database and multiplied by a million
    users_new = np.array([entry['Users'] for entry in df_formatted])
    users_original = users_new.astype(float) * 1_000_000
    MIN_REVENUE_INDEX = MIN_DATE_INDEX

    # Iteration range for valuation calculation
    iteration_range = [MIN_DATE_INDEX,
                       len(dates_original)]  # Range for calculating all the valuations, starting from the 4th date
    # Dataframe creation for all the valuation over time

    # Valuation calculation
    non_operating_assets = total_assets
    # df_valuation_over_time = pd.DataFrame(columns=columns)
    valuation_data = []
    print("Iteration range", iteration_range)
    if df_rawdataset_counter:  # calculates the historic of valuation only if the dataset has been updated
        for i in range(iteration_range[0], iteration_range[1]):
            dates_valuation = dates_original[:i]
            users_valuation = users_original[:i]
            quarterly_revenue = revenue_df * 1_000_000  # Getting in database
            revenue_valuation = quarterly_revenue[:i]
            market_cap_valuation = market_cap_original[i]

            profit_margin_valuation = profit_margin_original[:i]

            # Smoothing the data
            #dates, users = main.moving_average_smoothing(dates_valuation, users_valuation, 1)
            dates = dates_valuation
            users = users_valuation

            # All parameters are calculated by ignoring data 1 by 1, taking the history reference as the end point
            df_full = main.parameters_dataframe(dates,
                                                users)  # Dataframe containing all parameters with all data ignored
            df_sorted = main.parameters_dataframe_cleaning(df_full,
                                                           users)  # Dataframe where inadequate scenarios are eliminated

            if df_sorted.empty: # Smoothening data for cases where it doesn't work
                # Smoothing the data
                #dates1, users1 = main.moving_average_smoothing(dates_valuation, users_valuation, 4)
                dates = dates_valuation
                users = users_valuation

                # All parameters are calculated by ignoring data 1 by 1, taking the history reference as the end point
                df_full1 = main.parameters_dataframe(dates,
                                                    users)  # Dataframe containing all parameters with all data ignored
                df_sorted = main.parameters_dataframe_cleaning(df_full1,
                                                               users)  # Dataframe where inadequate scenarios are eliminated
                if df_sorted.empty:
                    print("Cleaning it minimally")
                    df_sorted = main.parameters_dataframe_cleaning_minimal(df_full, users)
                    print("df_sorted_minimally", df_sorted)
                    if df_sorted.empty:
                        print("No scenario could be calculated")
                    #continue
            else:
                print("Successful scenarios exist")
            # Number of scenarios to store
            i -= MIN_DATE_INDEX

            # Profit margin assessment
            profit_margin = np.empty(2)
            profit_margin_previous_year = profit_margin_valuation[-4:]
            average_profit_margin = sum(profit_margin_previous_year) / 4
            if average_profit_margin <= 0:
                #min_profit_margin = 0.01
                min_profit_margin = max_net_margin * 0.8  # Taking 80% of the max profit margin as a lower scenario
                #max_profit_margin = 0.1
                max_profit_margin = max_net_margin
            else:
                #min_profit_margin = average_profit_margin
                min_profit_margin = max_net_margin*0.8
                #max_profit_margin = average_profit_margin + 0.05
                #max_profit_margin = max(profit_margin_valuation) + 0.05
                max_profit_margin = max_net_margin # High scenario taking the max theoretical profit margin
            profit_margin[0] = min_profit_margin  # Low scenario
            profit_margin[1] = max_profit_margin  # High scenario taking the max seen profit margin

            # Discount Rate assessment
            discount_rate = np.empty(2)
            discount_rate[0] = 0.1  # Low scenario
            discount_rate[1] = 0.1  # High scenario

            # Arpu growth assessment
            arpu_growth = np.empty(2)
            arpu_growth[0] = 0.01  # Low scenario
            arpu_growth[1] = 0.05  # High scenario

            # Current ARPU calculation
            yearly_revenue_quarters = sum(revenue_valuation[-4:])
            average_users_past_year = (users_valuation[-1] + users_valuation[-5]) / 2
            current_arpu = yearly_revenue_quarters / average_users_past_year
            num_iterations = 2
            print("averageprofit")
            # Storing the data of two scenarios for a given date
            for j in range(num_iterations):
                # If no scenario is found, 0 is appended. Later the 0 is transformed in the last known valuation
                if df_sorted.empty:
                    valuation_data.append([
                        dates_new[i + MIN_DATE_INDEX],
                        dates_raw[i + MIN_DATE_INDEX],
                        0, 0, 0, 0, 0, 0, 0
                    ])
                else:
                    k_selected = df_sorted.at[j * (len(df_sorted) - 1), 'K']
                    r_selected = df_sorted.at[j * (len(df_sorted) - 1), 'r']
                    p0_selected = df_sorted.at[j * (len(df_sorted) - 1), 'p0']
                    future_customer_equity = main.net_present_value_arpu_growth(k_selected, r_selected, p0_selected,
                                                                                current_arpu, arpu_growth[j],
                                                                                profit_margin[j], discount_rate[j],
                                                                                YEARS_DCF)
                    current_customer_equity = users_valuation[-1] * current_arpu * profit_margin[j]
                    valuation_data.append([
                        dates_new[i + MIN_DATE_INDEX],
                        dates_raw[i + MIN_DATE_INDEX],
                        k_selected,
                        r_selected,
                        p0_selected,
                        profit_margin[j],
                        current_arpu,
                        future_customer_equity + current_customer_equity + non_operating_assets,
                        market_cap_valuation
                    ])
    # Convert the list to a DataFrame
    columns = ['Date', 'Date Raw', 'K', 'r', 'p0', 'Profit Margin', 'ARPU', 'Valuation', 'Market Cap']
    df_valuation_over_time = pd.DataFrame(valuation_data, columns=columns)
    df_valuation_over_time_dict = df_valuation_over_time.to_dict(orient='records')

    print("DF Valuation over time")
    print(df_valuation_over_time)
    hide_loader = {'display': 'none'}

    print("DF Valuation over time")
    print(df_valuation_over_time)
    # print(df_valuation_over_time2)
    t2 = time.perf_counter(), time.process_time()
    print(f" Performance of the valuation over time")
    print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
    return False, df_valuation_over_time_dict, hide_loader


@app.callback(
    # Output(component_id='data-selection-counter', component_property='data', allow_duplicate=True),
    Output(component_id='valuation-graph', component_property='figure', allow_duplicate=True),  # Update valuation graph
    Output(component_id='valuation-graph-message', component_property='children'),
    Output(component_id='valuation-graph-message', component_property='color'),
    Output(component_id='valuation-graph-message', component_property='title'),
    Output(component_id="valuation-message", component_property="title"),
    Output(component_id="valuation-message", component_property="children"),
    Output(component_id="valuation-message", component_property="color"),
    Output(component_id="accordion-valuation", component_property="icon"),
    Output(component_id="hype-score", component_property="data"), # hype score storage
    Output(component_id="hype-score-text", component_property="children"), #hype score text

    Input(component_id='valuation-over-time', component_property='data'),
    State(component_id='date-picker', component_property='value'),  # Take date-picker date
    State(component_id='users-dates-formatted', component_property='data'),
    State(component_id='total-assets', component_property='data'),
    State(component_id='users-dates-raw', component_property='data'),
    State(component_id='latest-market-cap', component_property='data'),  # Stores the current (now) company market cap
    State(component_id='scenarios-sorted', component_property='data'),  # Stores the calculated growth scenarios
    State(component_id='current-arpu-stored', component_property='data'),  # Stores the current arpu
    State(component_id='dataset-selection', component_property='value'),  # Stores the name of the dataset selected
    Input(component_id="current-valuation-calculated", component_property="data"),
    State(component_id='max-net-margin', component_property='data'),
    prevent_initial_call=True,
)
def graph_valuation_over_time(valuation_over_time_dict, date_picked, df_formatted, total_assets, df_raw,
                              latest_market_cap, df_sorted, current_arpu, company_sign, current_valuation, max_net_margin):
    if latest_market_cap == 0:
        raise PreventUpdate
    print("Graph Valuation Start")
    t1 = time.perf_counter(), time.process_time()
    dates_raw = np.array([entry['Date'] for entry in df_raw])
    dates_new = np.array([entry['Date'] for entry in df_formatted])
    revenue_df = np.array([entry['Revenue'] for entry in df_formatted])
    profit_margin_df = np.array([entry['Profit Margin'] for entry in df_formatted])
    company_symbol = str(company_sign)

    # Valuation calculation
    non_operating_assets = total_assets
    df_valuation_over_time = pd.DataFrame(valuation_over_time_dict)
    print("Df valuation")
    print(latest_market_cap)
    print(df_valuation_over_time)
    # Graph creation

    # Creating the plot of the market cap - valuations
    dates_valuation_graph = df_valuation_over_time['Date Raw'].values
    valuation_values = df_valuation_over_time['Valuation'].values

    # Separate scenarios (odd and even rows)
    low_scenario_valuation = valuation_values[::2]  # Start from index 0, step by 2
    high_scenario_valuation = valuation_values[1::2]  # Start from index 1, step by 2
    dates_valuation_graph = dates_valuation_graph[::2]

    # Create market cap array
    market_cap_array = np.array([entry['Market Cap'] for entry in df_formatted]) * 1e9
    market_cap_array = market_cap_array[MIN_DATE_INDEX:]

    # Calculates the hype level ratio HypeScore(HS)= (HV−LV) / (MC−LV)
    # If HS < 0 → Market is below your conservative estimate (undervalued).
    # If HS = 0.5 → Market is right in the middle of your valuation range.
    # If HS > 1 → Market exceeds even your optimistic case (potential hype).

    hype_score = (latest_market_cap*1e6 - low_scenario_valuation[-1]) / \
                 (high_scenario_valuation[-1] - low_scenario_valuation[-1])
    print("hype score calculation")
    print(hype_score)
    print(latest_market_cap)
    print(low_scenario_valuation[-1])
    print(high_scenario_valuation[-1])
    hype_score_text = f"Hype score: {hype_score:.2f}"  # Formatted text for hype meter
    # Append today's date and latest market cap
    today_date = date.today()
    market_cap_array = np.append(market_cap_array, latest_market_cap * 1e6)
    dates_raw_market_cap = np.append(dates_raw, today_date)
    low_scenario_valuation = np.append(low_scenario_valuation, low_scenario_valuation[-1])
    high_scenario_valuation = np.append(high_scenario_valuation, high_scenario_valuation[-1])
    # today_date_formatted = main.date_formatting_from_string(today_date)

    fig_valuation = go.Figure(layout=layout_main_graph)

    # Hype interval
    # Filling the area of hype, between the market cap and the highest valuation
    dates_until_today = np.append(dates_valuation_graph, today_date)
    y_area_low = market_cap_array  # Low growth array
    y_area_high = np.flip(high_scenario_valuation)  # High growth array
    y_area = np.append(y_area_low, y_area_high)
    dates_area = np.append(dates_until_today, np.flip(dates_until_today))

    # Hype Area
    fig_valuation.add_trace(go.Scatter(x=dates_area,
                                       y=y_area,
                                       fill='toself',
                                       line_color='#953AF6',
                                       #fillcolor='#C92A2A',
                                       fillpattern={#'shape': '/',
                                                    'bgcolor': 'white',
                                                    'fgcolor': '#953AF6'},
                                       opacity=0.2,
                                       hoverinfo='none',
                                       showlegend=True,
                                       name='Hype',
                                       )
                            )


    # Confidence Interval
    # Filling the area of possible scenarios
    y_area_low = low_scenario_valuation # Low growth array
    y_area_high = np.flip(high_scenario_valuation)  # High growth array
    y_area = np.append(y_area_low, y_area_high)
    dates_area = np.append(dates_until_today, np.flip(dates_until_today))
    fig_valuation.add_trace(go.Scatter(x=dates_area,
                                       y=y_area,
                                       fill='toself',
                                       line_color='rgba(255,255,255,0)',
                                       fillcolor='#FFF6CC',
                                       # opacity=0.3,
                                       hoverinfo='none',
                                       showlegend=True,
                                       name='Confidence Interval',
                                       )
                            )

    hovertemplate_maingraph = "%{text}"
    # Low Valuation
    formatted_y_values = [
        f"${y:.0f}" if y < 1e6 else f"${y / 1e6:.1f} M" if y < 1e9 else f"${y / 1e9:.2f} B"
        for y in low_scenario_valuation
    ]
    fig_valuation.add_trace(go.Scatter(name="Low Valuation",
                                       x=dates_until_today,
                                       y=low_scenario_valuation,
                                       mode="lines",
                                       line=dict(color='#C58400', width=1, dash="dash"),
                                       text=formatted_y_values,
                                       hovertemplate=hovertemplate_maingraph)
                            )

    # High Valuation
    formatted_y_values = [
        f"${y:.0f}" if y < 1e6 else f"${y / 1e6:.1f} M" if y < 1e9 else f"${y / 1e9:.2f} B"
        for y in high_scenario_valuation
        ]
    fig_valuation.add_trace(go.Scatter(name="High Valuation", x=dates_until_today, y=high_scenario_valuation,
                                       mode="lines", line=dict(color="#C58400", width=1, dash="dash"),
                                       text=formatted_y_values, hovertemplate=hovertemplate_maingraph, showlegend=False))
    # Market Cap
    formatted_y_values = [f"${y / 1e6:.1f} M" if y < 1e9 else f"${y / 1e9:.2f} B" for y in market_cap_array]
    fig_valuation.add_trace(go.Scatter(name="Market Cap", x=dates_raw_market_cap[MIN_DATE_INDEX:], y=market_cap_array,
                                       mode="lines", line=dict(color="#953AF6", width=2), text=formatted_y_values,
                                       hovertemplate=hovertemplate_maingraph))

    # Current valuation
    #print("Datata", date_picked, type(date_picked))
    # date_obj = datetime.strptime(date_picked, '%Y-%m-%d')
    if current_valuation > high_scenario_valuation[-1]:
        color_dot = "#300541"
    else:
        color_dot = "#FBC53C"

    formatted_y_values = [f"${current_valuation / 1e6:.1f} M" if current_valuation < 1e9
                          else f"${current_valuation / 1e9:.2f} B"]

    fig_valuation.add_scatter(name="Calculated Valuation", x=[date_picked], y=[current_valuation],
                              marker=dict(
                                  color=color_dot,
                                  size=10
                              ), text=formatted_y_values, hovertemplate=hovertemplate_maingraph)

    # Current Date - Vertical line
    # Defining the max y value
    if max(market_cap_array) > max(high_scenario_valuation):
        y_max = max(market_cap_array) * 1.1
    else:
        y_max = max(high_scenario_valuation) * 1.1

    fig_valuation.add_shape(
        go.layout.Shape(
            type="line",
            x0=date_picked,
            x1=date_picked,
            y0=0,
            y1=y_max,
            line=dict(color="gray", width=1, dash="dot"),
            opacity=0.6
        )
    )
    mid_id_valuation = len(dates_until_today) // 2
    mid_id_marketcap = len(market_cap_array) // 2
    # Update Layout
    fig_valuation.update_layout(
        hovermode="x unified",
        yaxis=dict(
            # range=[0, k_scenarios[-1] * 1.1],
            title="Valuation & Market Cap [$B]",
            #minallowed=0,
            # maxallowed=k_scenarios[-1] * 1.5,
        ),
        annotations=[
            dict(
                x=date_picked,
                y=y_max * 1.02,  # Adjust the y-position as needed
                text="Picked Date",
                showarrow=False,
                font=dict(
                    size=8,  # Adjust the size as needed
                    color="black",  # Text color
                    # letter=5,
                ),
                opacity=0.3  # Set the opacity
            ),
            # Low valuation arrow
            dict(
                x=dates_until_today[mid_id_valuation-1],
                y=low_scenario_valuation[mid_id_valuation-1],
                text="Worst scenario",
                showarrow=True,
                arrowhead=2,
                arrowcolor="#433001",
                ax=0,  # offset of arrow tail
                ay=40,  # offset of arrow tail
                font=dict(size=8, color="#433001"),
                opacity=0.5,
            ),
            # High valuation arrow
            dict(
                x=dates_until_today[mid_id_valuation+1],
                y=high_scenario_valuation[mid_id_valuation+1],
                text="Best scenario",
                showarrow=True,
                arrowhead=2,
                arrowcolor="#433001",
                ax=0,  # offset of arrow tail
                ay=-40,  # offset of arrow tail
                font=dict(size=8, color="#433001"),
                opacity=0.5,
            ),
            # Market cap arrow
            dict(
                x=dates_raw_market_cap[-3],
                y=market_cap_array[-3],
                text="Market cap",
                showarrow=True,
                arrowhead=2,
                arrowcolor="#300541",
                ax=0,  # offset of arrow tail
                ay=-60,  # offset of arrow tail
                font=dict(size=8, color="#300541"),
                opacity=0.5,
            ),
        ],
    )

    # Adding RAST logo
    fig_valuation.add_layout_image(
        dict(
            source="/assets/RAST_Vector_Logo_black.svg",  # Replace with your image URL or base64-encoded image
            xref="paper",  # Reference the image to the plot area
            yref="paper",
            x=1,  # Position the image in the bottom-right corner (1.0 means the right edge of the figure)
            y=0.01,  # Position the image at the bottom (0.0 means the bottom edge of the figure)
            xanchor="right",  # Align the image to the right
            yanchor="bottom",  # Align the image to the bottom
            sizex=0.1,  # Adjust the width of the image
            sizey=0.1,  # Adjust the height of the image
            layer="above"  # Place the image above the plot elements
        )
    )
    # Valuation message for the accordion
    k_high_valuation = df_sorted[-1]['K']
    r_high_valuation = df_sorted[-1]['r']
    p0_high_valuation = df_sorted[-1]['p0']

    profit_margin_needed = main.profit_margin_for_valuation(k_high_valuation, r_high_valuation, p0_high_valuation,
                                                            current_arpu, 0.05, 0.1, YEARS_DCF, non_operating_assets, latest_market_cap * 1000000)
    #max_profit_margin = np.max(profit_margin_df) old method, using the max known PM
    max_profit_margin = max_net_margin  # new method, using the max theoretical net profit margin.

    # Valuation message
    if market_cap_array[-1] < high_scenario_valuation[-1]:
        # Messages in the accordion
        valuation_accordion_title = company_symbol + " may be undervalued"
        valuation_accordion_message = company_symbol + "’s current price is below our top estimate. " \
                                                       "If you see long-term potential, it might be a good buy."
        # Messages right above the graph
        valuation_graph_title = "How well did our model perform over time?"
        valuation_graph_message = "The purple line shows " + company_symbol + "s price (market cap) over time. The yellow zone is our confidence " \
                                  "range, calculated over time (without readjustment, obviously). " \
                                  "We believe the market cap tends to fall, sooner or later, within this range. " \
                                  "The dot moves to show the valuation under your chosen scenario.\n" \
                                    " The market cap is currently lower than the most optimistic valuation (" + \
                                  f"{high_scenario_valuation[-1] / 1e9:.2f} B$) meaning that this stock may be fairly or even undervalued!"
        valuation_graph_color = "green"
        valuation_icon_color = DashIconify(icon="radix-icons:rocket", color=dmc.theme.DEFAULT_COLORS["green"][6],
                                           width=20)
    else:
        # Messages in the accordion
        valuation_accordion_title = company_symbol + " is overvalued"
        valuation_accordion_message = company_symbol + "'s current price is above our highest estimate. " \
                                                       "To justify it, they'd need a  " + \
                                      f"{profit_margin_needed *100:.1f}% " + \
                                      "profit margin, even though they could theoretically aim at best at " + f"~{max_profit_margin:.0f}%... " \
                                                                                         f"So yeah, a bit of a stretch."
        # Messages right above the graph
        valuation_graph_title = "How well did our model perform over time?"
        valuation_graph_message = "The purple line shows " + company_symbol + "s price (market cap) over time. The yellow zone is our confidence " \
                                  "range, calculated over time (without readjustment, obviously). " \
                                  "We believe the market cap tends to fall, sooner or later, within this range. " \
                                  "The dot moves to show the valuation under your chosen scenario.\n" \
                                  "The Market cap is currently higher than the most optimistic valuation (" + \
                                  f"{high_scenario_valuation[-1] / 1e9:.2f} B$), meaning that this stock seems overvalued."
        valuation_graph_color = "yellow"
        valuation_icon_color = DashIconify(icon="radix-icons:rocket", color=dmc.theme.DEFAULT_COLORS["yellow"][6],
                                           width=20)
    print("Valuation graph printed")
    t2 = time.perf_counter(), time.process_time()
    print(f" Performance of the valuation graph over time")
    print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
    return fig_valuation, valuation_graph_message, valuation_graph_color, valuation_graph_title, valuation_accordion_title, \
        valuation_accordion_message, valuation_graph_color, valuation_icon_color, hype_score, hype_score_text


# Callback resetting enabling the reset button
@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open






'''
# Callback changing the example hypemeter on the homepage
@app.callback(
    Output(component_id='hype-meter-users-home', component_property='value'),
    Output(component_id='hype-meter-hype-home', component_property='value'),
    Output(component_id='hype-indicator-home-example', component_property='children'),
    Output(component_id='hype-indicator-home-example', component_property='color'),
    Input(component_id='slider-example', component_property='value'),
    Input(component_id='hype-meter-noa-home', component_property='value'),
    prevent_initial_call=True,)

def home_page_example(slider_value, non_op_assets):
    market_cap_example = 210
    equity = 110/66 * slider_value
    hype = market_cap_example - equity - non_op_assets
    hype_ratio = hype*0.3/market_cap_example
    print("hyperatio", hype_ratio)
    hype_indicator_color, hype_indicator_text = main.hype_meter_indicator_values(hype_ratio)
    return equity, hype, hype_indicator_text, hype_indicator_color
'''

# Callback to update table based on selection
@app.callback(
    Output("top_25_companies", "children"),
    Input('all-companies-information', 'data'), # Table of companies
    Input('hyped-table-select', 'value'), # more or least hyped
    Input('hyped-table-industry', 'value'), # industry
    Input("login-state", "data"),
)
def update_table(df_all_companies, hype_choice, industries, logged_in):
    t1 = time.perf_counter(), time.process_time()

    # If dropdown hasn't been used yet, set a default
    if hype_choice is None:
        hype_choice = "least-hyped"  # default setting

    # --- 1. Filter by industry ---
    if industries:
        filtered_data = [d for d in df_all_companies if d["Industry"] in industries]
    else:
        filtered_data = df_all_companies

    # --- 2. Determine sorting order based on hype_choice ---
    reverse = True if hype_choice == "most-hyped" else False

    # --- 3. Sort by Hype Score ---
    sorted_data = sorted(filtered_data, key=lambda x: x["Hype Score"], reverse=reverse)

    # --- 4. Keep only selected columns ---
    reduced_data = [
        {
            "Industry": d["Industry"],
            "Company Name": d["Company Name"],
            "Hype Score": d["Hype Score"],
            "Growth Score": d["Growth Score"]
        }
        for d in sorted_data
    ]
    df_sorted = pd.DataFrame(sorted_data)
    # Logic of changing it depending on what is chosen
    #if hype_choice == 'most-hyped':
    #    df_sorted = dataAPI.get_hyped_companies(True)
    #else:
    #    df_sorted = dataAPI.get_hyped_companies(False)
    header = [html.Thead(html.Tr([
    html.Th('Industry', style={"width": "15%"}),
    html.Th('Company', style={"width": "30%"}),
    html.Th(dmc.Group([
        'Hype Score',
        dmc.Tooltip(
            DashIconify(icon="feather:info", width=15),
            label="The hype score indicates how hyped companies are. A hype score between 0 & 1 means that the company "
                  "is fairly priced. A negative hype score indicates an undervaluation.",
            transition="slide-down",
            transitionDuration=300,
            multiline=True,
        )
    ]), style={"width": "22.5%"}
    ),
    html.Th(dmc.Group([
        'Growth Score',
        dmc.Tooltip(
            DashIconify(icon="feather:info", width=15),
            label="The growth score represents how much growth potential a company has relative to its current state. "
                  "A score of zero implies stagnation, whereas a high score suggests strong momentum and the "
                  "possibility of staying overvalued for an extended period.",
            transition="slide-down",
            transitionDuration=300,
            multiline=True,
        )
    ]), style={"width": "32.5%"}
    )
    ])
    )]
    rows = []

    for i in range(len(df_sorted)):
        industry_type = df_sorted.iloc[i]['Industry'],
        industry_type_icon = main.get_industry_icon(df_sorted.iloc[i]['Industry'])  # function mapping the industry to an icon
        company_name = df_sorted.iloc[i]['Company Name']
        hype_score = df_sorted.iloc[i]['Hype Score']
        growth_score = df_sorted.iloc[i]['Growth Score']

        # Determine badge color and label -> To-do: apply the function in .main to this -> done, replace it by main.hype_meter_indicator_values
        # badge_color, badge_label = main.hype_meter_indicator_values(hype_score)
        if hype_score > 2.5:
            badge_color = "red"
            badge_label = "Super hyped"
        elif hype_score > 1.5:
            badge_color = "orange"
            badge_label = "Mildly hyped"
        elif hype_score > 1:
            badge_color = "yellow"
            badge_label = "Marginally hyped"
        elif hype_score > 0:
            badge_color = "green"
            badge_label = "Fairly priced"
        else:
            badge_color = "teal"
            badge_label = "Undervalued"

        # Determine growth badge color and label -> To-do: apply the function in .main to this
        if growth_score > 0.5:
            badge_color_growth = "teal"
            badge_label_growth = "Massive growth"
        elif growth_score > 0.3:
            badge_color_growth = "green"
            badge_label_growth = "Strong growth"
        elif hype_score > 0.1:
            badge_color_growth = "yellow"
            badge_label_growth = "Limited growth"
        else:
            badge_color_growth = "red"
            badge_label_growth = "Poor growth"

        row = html.Tr([
            html.Td(
                dmc.Tooltip(
                    DashIconify(icon=industry_type_icon, width=15),
                    label=industry_type,
                    #transition="slide-down",
                    #transitionDuration=300,
                    #multiline=True,
                ),
                #ta="center",
                style={"ta": "center"}
            ),
            html.Td(
                dcc.Link(
                    company_name,
                    target="_blank",  # 👈 this makes it open in a new tab
                    href=f"https://app.rast.guru/?company={company_name}"
                ),
                style={"width": "20%"}
            ),
            html.Td(
                dmc.Group([
                    f"{hype_score:.2f}",
                    dmc.Badge(badge_label, size="xs", variant="outline", color=badge_color)
                ], spacing="md"),
                style={"width": "30%"}
            ),
            html.Td(
                dmc.Group([
                    f"{growth_score:.2f}",
                    dmc.Badge(badge_label_growth, size="xs", variant="outline", color=badge_color_growth)
                ], spacing="md"),
                style={"width": "40%"}
            ),
        ])
        rows.append(row)
    body = [html.Tbody(rows)]
    #print("Hyped table is")
    #print(df_sorted)
    t2 = time.perf_counter(), time.process_time()
    print(f" Performance of the table update")
    print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
    return header + body



# Upload data functionality to be improved


'''
# Callback opening the modal when new data is uploaded and closing it when another button is clicked
@callback(
    Output("upload-modal", "opened"),
    Input("upload-button", "n_clicks"),
    Input("modal-close-button", "n_clicks"),
    Input("modal-submit-button", "n_clicks"),
    State("upload-modal", "opened"),
    prevent_initial_call=True,
)
def modal_demo(upload_clicks, close_clicks, submit_clicks, is_open):
    ctx = dash.callback_context
    if not ctx.triggered:
        return False
    else:
        prop_id = ctx.triggered[0]["prop_id"]
        if prop_id == "upload-button.n_clicks":
            return True
        elif prop_id == "modal-close-button.n_clicks" or prop_id == "modal-submit-button.n_clicks":
            return False
        else:
            return is_open

# Callback parsing the CSV/XLS and displaying it on the modal
@callback(Output('output-data-upload', 'children'),
          Output('last-imported-data', 'data'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
          prevent_initial_call=True,)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        table = main.parse_contents(list_of_contents, list_of_names, list_of_dates)
        df = main.parse_contents_df(list_of_contents, list_of_names, list_of_dates)
        children = [table]
        #table = main.parse_file_contents(list_of_contents, list_of_names)
        #children = [table]
        df_dict = df.to_dict(orient='records')
        return children, df_dict

# Callback setting the loaded data as the current selection
@callback(
    Output("dataset-selection", "value"),
    Output("upload-modal", "is_open"),
    Input("modal-submit-button", "n_clicks"),
    State('last-imported-data', 'data'),
    prevent_initial_call=True,
)
def save_imported_data(submit_clicks, df):
    if df is not None:
        return "Uploaded Data", False
    else:
        raise PreventUpdate
'''

# Download Graph functionality
'''
@app.callback(
    Output("download-chart", "data"),
    Input("download-graph-button", "n_clicks"),
    Input("main-graph1", "figure"),
    prevent_initial_call=True
)
def download_chart(n_clicks, main_graph):
    # Create an in-memory file for the chart
    fig_test = go.Figure()
    img_buffer = io.BytesIO()
    export = fig_test.write_image("fig_test", format="png", scale=2, engine='kaleido')  # High-quality PNG
    img_buffer.seek(0)

    # Return file for download
    return dcc.send_file(
        export,
        #download_name="chart.png"
    )
'''
if __name__ == '__main__':
    app.run_server(debug=True)
