# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser
import copy
import json
import math
import os
import time
import urllib.parse
import urllib.parse
from datetime import datetime, timedelta, date

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import jwt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import stripe
from dash import callback
from dash import html, dcc, callback_context, no_update, clientside_callback
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from flask import request, jsonify, send_from_directory
from plotly.subplots import make_subplots
from posthog import Posthog

import main
import src.ParametersDataFrame
import src.Utils.Logistics
import src.Utils.dates
import src.Utils.mathematics
import src.analysis
from components.analysis_card import analysis_card
from components.functionalities_card import functionalities_card
from components.graph_layouts import layout_main_graph, layout_revenue_graph, layout_growth_rate_graph, \
    layout_product_maturity_graph
from components.growth_card import growth_card
from components.growth_rate_card import growth_rate_card
from components.hype_meter_card import hype_meter_card, card_welcome
from components.offcanvas import offcanvas
from components.modal_video_tutorial import modal_tutorial
from components.product_maturity_card import product_maturity_card
from components.quadrant_card import quadrant_card
from components.ranking_card import table_hype_card
from components.revenue_card import revenue_card
from components.stored_data import stored_data
from components.valuation_card import valuation_card
import components.AppShellNavbar.RastAppShellNavbar as RastAppShellNavbar
import components.RastDropDownBox.RastDropDownBox as RastDropDownBox

from src.API.AirTableAPI import AirTableAPI
from src.API.FinhubAPI import FinhubAPI
from src.Utils.RastLogger import get_default_logger
from src.Utils.dates import YEAR_OFFSET
from components.company_quadrant_card import company_quadrant_card

logger = get_default_logger()

t1 = time.perf_counter(), time.process_time()

# Load environment variables from .env file
load_dotenv()

# Retrieve secrets
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
logger.info(f"Stripe key loaded: {bool(stripe.api_key)}")

pd.set_option('display.max_rows', 200)
# APP_TITLE = "RAST"

IS_PRODUCTION = os.getenv("IS_PRODUCTION") == "true"  # Setup in heroku 'heroku config:set IS_PRODUCTION=true'
clerk_script_ignored = r"clerk\.dev\.js" if IS_PRODUCTION else r"clerk\.prod\.js"  # if production, ignores clerk.dev.js

dash._dash_renderer._set_react_version('18.2.0')

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.LUX],
                # external_stylesheets=[dbc.themes.MORPH], Nice stylesheet

                use_pages=True,
                url_base_pathname="/",
                assets_ignore=clerk_script_ignored,
                )

# Posthog settings
posthog = Posthog(
    project_api_key='phc_b1l76bi8dgph2LI23vhWTdSNkiL34y2dkholjYEC7gw',
    host='https://eu.i.posthog.com',
    enable_exception_autocapture=True,
)

# Load index template from external file
with open("index.html") as f:
    app.index_string = f.read()

# ---------------------------------------------------------------------------

# Constants for the calculation
MIN_DATE_INDEX = 5  # Defines the minimum year below which no date can be picked in the datepicker!
YEARS_DCF = 15  # Amount of years taken into account for DCF calculation

# ---------------------------------------------------------------------------------
# App Layout

server = app.server

sections = [
    {"id": "section-1", "title": "Current Situation", "subtitle": "", "color": "blue", "icon": "mdi:bullseye"},
    {"id": "section-2", "title": "Quadrant", "subtitle": "", "color": "yellow", "icon": "carbon:quadrant-plot"},
    {"id": "section-3", "title": "Valuation history", "subtitle": "", "color": "orange", "icon": "tabler:pig-money"},
    {"id": "section-4", "title": "Growth", "subtitle": "", "color": "purple", "icon": "streamline-sharp:decent-work-and-economic-growth"},
    {"id": "section-5", "title": "Revenue", "subtitle": "", "color": "purple", "icon": "fa6-solid:money-check-dollar"},
    {"id": "section-6", "title": "Product Maturity", "subtitle": "", "color": "red", "icon": "healthicons:old-man-outline"},
    {"id": "section-7", "title": "Growth rate", "subtitle": "", "color": "yellow", "icon": "material-symbols-light:biotech-outline-rounded"},
    {"id": "section-8", "title": "Ranking", "subtitle": "Logged in only", "color": "yellow", "icon": "solar:ranking-line-duotone"},
]

layout_one_column = dmc.AppShell(
    children=[
        dmc.AppShellHeader(
            dmc.Group(
                [
                    dmc.Group(
                        [
                            dmc.Burger(
                                id="burger",
                                size="xs",
                                hiddenFrom="sm",
                                opened=False,
                                color="white",
                            ),
                            html.A(
                                id='logo-link',
                                children=dmc.Image(
                                    src="/assets/RAST_Vector_Logo.svg",
                                    h={"base": 25, "sm": 35, "lg": 40},  # Responsive height
                                    w={"base": 65, "sm": 91, "lg": 104},  # Responsive width
                                    alt="RAST app guru, valuation made simple"
                                ),
                                href="https://www.rast.guru",
                            ),
                        ],
                        gap="xs",
                        wrap="nowrap",
                    ),
                    RastDropDownBox.create(labels=AirTableAPI.get_labels() or [] if IS_PRODUCTION else ["Airbnb", "Affirm", "Spotify"]),
                    dmc.Group(
                        [
                            # Text version - visible on medium+ screens
                            dcc.Link(
                                dmc.Button(
                                    [
                                        DashIconify(icon="solar:ranking-linear", width=18),
                                        dmc.Text("Ranking", visibleFrom="sm", ml="xs", fw=600)
                                    ],
                                    variant="subtle",
                                    color="gray",
                                    size="xs",
                                    style={"color": "var(--mantine-color-gray-3)"},
                                ),
                                href="/ranking",
                            ),
                            #dmc.Box(offcanvas, visibleFrom="sm"),
                            dmc.Box(modal_tutorial, visibleFrom="sm"),
                            html.Div(
                                id="clerk-header",
                                style={"flexShrink": "0"}  # Prevent shrinking
                            ),  # Clerk user button
                        ],
                        gap="sm",
                        wrap="nowrap",
                    ),
                ],
                h="100%",
                px="sm",  # Increased padding (or use a number like px=40)
                justify="space-between",  # This pushes items to left and right
                align="center",
                wrap="nowrap",
                gap="sm",
            ),
            bg="black",
        ),
        RastAppShellNavbar.create(),
        dmc.AppShellMain(
            children=[
                dmc.Grid(
                    [
                        # Left column: scrollable content
                        dmc.GridCol(
                            span={"base": 12, "lg": 8},
                            children=
                            [
                                card_welcome,
                                dmc.Stack(
                                    id="homepage-cards",
                                    children=[
                                        dmc.Breadcrumbs(
                                            id="breadcrumbs-container",
                                            px="lg",
                                            separator="→",
                                            children=[
                                                dmc.Anchor("Home", href="/", underline=False),
                                                ]
                                        ),
                                        hype_meter_card,
                                        company_quadrant_card,
                                        analysis_card,
                                        valuation_card,
                                        growth_card,
                                        revenue_card,
                                        product_maturity_card,
                                        growth_rate_card,
                                        html.Div(id='js-title-trigger', style={'display': 'none'}), # trigger changing the page's title
                                    ],
                                    gap="md",
                                    p="md",
                                    style={'display': 'none'}
                                ),
                                dmc.NotificationContainer(id="notification-container"),
                            ],
                        ),

                        # Right column:static functionalities card
                        dmc.GridCol(
                            span={"base": 12, "lg": 4},
                            children=dmc.Stack(
                                [functionalities_card],
                                gap="md",
                                p="md",
                                style={
                                    "position": "sticky",
                                    "top": "17px",  # stays fixed below header
                                    "alignSelf": "start",
                                },
                            ),
                        ),
                    ],
                ),
                html.Div(
                    id="ranking-grid",
                    style={"display": "none"},  # Hidden by default
                    children=dmc.Grid([
                        dmc.GridCol([table_hype_card], span={'base': 12, 'sm': 10}),
                        dmc.GridCol([quadrant_card], span={'base': 12, 'sm': 10}),
                    ],
                        gutter="xs"
                    )
                ),
                dash.page_container,
                stored_data,
            ],
            id="main-content",
            style={
                "height": "100vh",
                "overflow": "auto",
                "overflowX": "hidden"
            },
        ),
    ],
    header={"height": 60},
    navbar={
        "width": 250,
        "breakpoint": "sm",
        "collapsed": {"mobile": True},
        "style": {
            "backgroundColor": "rgba(255, 255, 255, 0.7)",  # White with 70% opacity
        }},
    padding="0",
    id="app-shell",
),

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
        "fontFamily": "Basel, Arial, sans-serif",
        "headings": {
            "fontFamily": "ABCGravityUprightVariable, sans-serif",
        },
    },
    children=layout_one_column)

# Clerk domain (e.g., "your-app.clerk.accounts.dev")

# Pick the right url depending on the environment (first one is prod, stored on heroku, second is dev)
CLERK_JWKS_URL = os.getenv("https://clerk.rast.guru/.well-known/jwks.json",
                           "https://happy-skylark-73.clerk.accounts.dev/.well-known/jwks.json")
logger.info("clerk jwks")
logger.info(CLERK_JWKS_URL)
jwks = requests.get(CLERK_JWKS_URL).json()
logger.info(f"Flask routes: {[r.rule for r in app.server.url_map.iter_rules()]}")


# ----------------------------------------------------------------------------------

# Adding sitemap and robots
@server.route("/sitemap.xml")
def send_sitemap():
    logger.info("Sitemap route accessed!")  # Debug line
    return send_from_directory("static", "sitemap.xml")


@server.route("/robots.txt")
def send_robots():
    return send_from_directory("static", "robots.txt")


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


PUBLIC_PATHS = ["/", "/robots.txt", "/sitemap.xml", "/ranking", "/pricing"]


@server.before_request
def check_auth():
    # Allow Dash internals and static files
    if request.path.startswith(("/_dash", "/assets", "/static")):
        return None

    # Allow public routes
    if request.path in PUBLIC_PATHS:
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


@app.callback(
    Output("app-shell", "navbar"),
    Input("burger", "opened"),
    State("app-shell", "navbar"),
)
def toggle_navbar(opened, navbar):
    navbar["collapsed"] = {"mobile": not opened}
    return navbar


# Callback to close navbar when a navigation link is clicked (mobile only)
@app.callback(
    Output("burger", "opened", allow_duplicate=True),
    [Input(f"link-{section['id']}", "n_clicks") for section in sections],
    State("burger", "opened"),
    prevent_initial_call=True,
)
def close_navbar_on_click(*args):
    """Close the navbar when any navigation link is clicked on mobile"""
    # args[-1] is the State (current opened status)
    # If navbar is currently open, close it
    if args[-1]:  # If opened is True
        return False
    return no_update


# Clientside callback for smooth scrolling and scroll spy
clientside_callback(
    """
    function(n_clicks_list) {
        // Use a persistent key to ensure listeners are only added once per page load.
        // This is often more reliable than checking n_clicks, especially for listeners.
        if (window.__scrollListenersAttached) {
            return window.dash_clientside.no_update;
        }

        const mainContent = document.getElementById('main-content');
        // Ensure this selector targets your links correctly
        const links = document.querySelectorAll('[id^="link-section-"]'); 
        const sections = document.querySelectorAll('[id^="section-"]'); 

        // --- 1. Attach Scroll Spy Listener ---
        function updateActiveLink() {
            // ... (Your original scroll spy logic, and the PostHog logic)
            // ... (This part seems okay as it relates to the scroll event)

            // Re-inserting the PostHog tracking logic here for completeness:
            let currentSectionId = '';
            const scrollPosition = mainContent.scrollTop + 200; 

            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.offsetHeight;

                if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                    currentSectionId = section.id;
                }
            });

            // PostHog Tracking Logic (Ensure window.posthog exists on your page)
            if (currentSectionId && currentSectionId !== window.lastTrackedSection) {
                const urlParams = new URLSearchParams(window.location.search);
                const companyName = urlParams.get('company') || 'None Selected';

                if (window.posthog) {
                    console.log(`[POSTHOG DEBUG] Attempting to capture: Section Viewed for section ${currentSectionId}`)
                    
                    window.posthog.capture('Section Viewed', {
                        section_name: currentSectionId.replace('section-', ''), 
                        company_name: companyName,
                        scroll_transition: 'enter',
                    });
                }
                window.lastTrackedSection = currentSectionId;
            }

            // Scroll Spy logic (Style update)
            links.forEach(link => {
                const linkTarget = link.getAttribute('href').substring(1);
                if (linkTarget === currentSectionId) {
                    link.style.backgroundColor = '#953AF6';
                    link.style.fontWeight = '600';
                    link.style.color = '#FFFFFF';
                } else {
                    link.style.backgroundColor = 'transparent';
                    link.style.fontWeight = 'normal';
                    link.style.color = '#495057';
                }
            });
        }

        // Attach scroll listener once
        if (mainContent) {
            mainContent.addEventListener('scroll', updateActiveLink);
            updateActiveLink(); // Initial run
        }

        // --- 2. Attach Click Listeners (The fix is ensuring this runs) ---
        links.forEach(link => {
            // Ensure link is a valid DOM element
            if (link && !link.hasAttribute('data-click-listener')) {
                link.addEventListener('click', function(e) {
                    e.preventDefault();

                    // Verify targetId is correct
                    const targetId = this.getAttribute('href').substring(1); 
                    const targetElement = document.getElementById(targetId);

                    if (targetElement && mainContent) {
                        const targetPosition = targetElement.offsetTop - 70;
                        mainContent.scrollTo({ 
                            top: targetPosition,
                            behavior: 'smooth'
                        });
                    }
                });
                link.setAttribute('data-click-listener', 'true');
            }
        });

        // Mark listeners as attached to prevent duplication on subsequent updates
        window.__scrollListenersAttached = true; 

        return window.dash_clientside.no_update;
    }
    """,
    Output("link-section-1", "n_clicks"),  # Use a dummy output ID that exists
    # Use any input that reliably triggers on load or user interaction.
    # The list of n_clicks is fine if 'sections' is defined in Python.
    [Input(f"link-{section['id']}", "n_clicks") for section in sections],
    prevent_initial_call=False,
)

clientside_callback(
    """
    function() {
        const aside = document.querySelector('[class*="AppShellAside"]');

        if (aside && !aside.hasAttribute('data-scroll-fixed')) {
            aside.addEventListener('wheel', function(e) {
                // Check if aside content is scrollable
                const isScrollable = this.scrollHeight > this.clientHeight;

                if (!isScrollable) {
                    // If not scrollable, don't capture the scroll
                    e.preventDefault();
                    // Pass scroll to main content
                    const mainContent = document.getElementById('main-content');
                    if (mainContent) {
                        mainContent.scrollTop += e.deltaY;
                    }
                }
            });
            aside.setAttribute('data-scroll-fixed', 'true');
        }

        return window.dash_clientside.no_update;
    }
    """,
    Output("app-shell", "id"),
    Input("app-shell", "id"),
    prevent_initial_call=False,
)

# Callback displaying the pricing table on the pricing page

app.clientside_callback(
    """
    function(id_table, pathname) {
        // Only mount if we're on the pricing page
        if (pathname === '/pricing') {
            const container = document.getElementById('pricing-table-container');

            // --- New/Modified Logic Starts Here ---
            if (container) {
                // Function to attempt mounting
                function tryMountClerk() {
                    if (window.Clerk) {
                        // Clear previous content to avoid duplicates
                        container.innerHTML = '';
                        // Mount the pricing table
                        window.Clerk.mountPricingTable(container);
                        return true; // Successfully mounted
                    }
                    return false; // Clerk not ready yet
                }

                // Try mounting immediately
                if (!tryMountClerk()) {
                    // If not ready, poll every 50ms until Clerk is available
                    const maxAttempts = 100; // Max 5 seconds
                    let attempts = 0;
                    const intervalId = setInterval(() => {
                        if (tryMountClerk() || attempts >= maxAttempts) {
                            clearInterval(intervalId); // Stop the interval
                        }
                        attempts++;
                    }, 50);
                }
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('pricing-table-container', 'data-mounted'),
    Input('pricing-table-container', 'id'),
    Input('_pages_location', 'pathname')
)


# Stores login state & user data and avoids update if login state has not changed
@app.callback(
    Output('login-state', 'data'),  # stores logged in state (boolean)
    Output('pro-user-state', 'data'),  # stores pro account state (boolean)
    Output('user-id', 'data'),
    Input("login-state-bridge", "children"),
    prevent_initial_call=True,  # avoid firing on page load if empty
)
def update_login_state(bridge_content):
    if not bridge_content:
        return no_update  # nothing to do

    try:
        state = json.loads(bridge_content)
    except json.JSONDecodeError:
        logger.info(f"Failed to parse login-state-bridge content: {bridge_content}")
        return no_update

    # Extract logged_in and user_id
    logged_in = state.get("logged_in", False)
    user_id = state.get("user_id", None)
    free_user = state.get("has_free_plan", False)
    pro_user = state.get("has_pro_plan", False)

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

    # Message for free vs pro user
    if free_user:
        user_type_message = " who is a free user"
    elif pro_user:
        user_type_message = " who is a pro user"
    else:
        user_type_message = " error: neither free nor pro user"

    logger.info(f"Updating login-state to: {logged_in} for user: {user_id, user_type_message}")
    return logged_in, pro_user, user_id


@app.callback(
    Output("login-overlay-table", "style"),
    Output("login-overlay-chart", "style"),
    Output("scenarios-picker", "disabled"),
    Output("picker-tooltip", "disabled"),
    Input("login-state", "data"),
    State("pro-user-state", "data")
)
def toggle_overlay(logged_in, pro_user_state):
    # Scenario picker logic: If logged_in is True, disabled is False.
    picker_disabled = not logged_in
    # Tooltip logic: Disable the tooltip if the user IS logged in
    tooltip_disabled = logged_in

    if not logged_in or not pro_user_state:  # False or None:
        style = {"display": "block",
                 "position": "absolute",
                 "top": 0,
                 "left": 0,
                 "width": "100%",
                 "height": "100%",
                 "backgroundColor": "rgba(0,0,0,0.6)",
                 "zIndex": 5,
                 "backdropFilter": "blur(2px)"}
        return style, style, picker_disabled, tooltip_disabled
        # skipping it if no dropdown value is selected to avoid firing it when starting
    if IS_PRODUCTION:
        posthog.capture(
            # distinct_id='loggd',  # replace with real user/session ID
            event='logged_in',
            properties={
                'logged_in': 'True',
            }
        )
    return {"display": "none"}, {"display": "none"}, picker_disabled, tooltip_disabled


# ----------------------------------------------------------------------------------
# Callback behaviours and interaction

# Callback to open/close the modal
@app.callback(
    Output("video-modal", "opened"),
    Input("open-modal-btn", "n_clicks"),
    State("video-modal", "opened"),
    prevent_initial_call=True,
)
def toggle_modal(n_clicks, opened):
    return not opened

# Callback to update the URL based on the dropdown selection
@app.callback(
    Output('url-input', 'search'),  # Output 1: URL search string
    Output('dataset-selection', 'value'),  # Output 2: Dropdown value
    Output('breadcrumbs-container', 'children'),  # Output 2: Dropdown value
    Input('url-input', 'search'),  # Input 1: URL search string
    Input("dataset-selection", "value")  # Input 2: Dropdown selection
)
def sync_url_and_dropdown(url_search, dropdown_value):
    # This helps break the cycle by identifying the source of the trigger
    ctx = dash.callback_context

    # 1. Handle Initial Load
    if not ctx.triggered:
        # On initial load, prioritize the URL. If 'company' is in the URL,
        # set the dropdown to match. Otherwise, no update.
        company_from_url = None
        if url_search:
            query_params = urllib.parse.parse_qs(url_search.lstrip('?'))
            company_from_url = query_params.get('company', [None])[0]

        if company_from_url and company_from_url != dropdown_value:
            # Update dropdown from URL on initial load
            return no_update, company_from_url, main.render_breadcrumbs(company_from_url)

        return no_update, no_update, main.render_breadcrumbs()

    # 2. Determine Trigger Source
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # --- A. Dropdown Triggered the Change ---
    if trigger_id == 'dataset-selection':
        # User selected a company from the dropdown.
        # Goal: Update the URL to reflect the selection.
        if dropdown_value:
            new_search = f"?company={urllib.parse.quote(dropdown_value)}"
            return new_search, no_update, main.render_breadcrumbs(dropdown_value)
        # If selection is cleared/empty, you might want to clear the URL or no_update
        return no_update, no_update, main.render_breadcrumbs()


    # --- B. URL Triggered the Change ---
    elif trigger_id == 'url-input':
        # User typed directly into the URL or navigated using a URL.
        # Goal: Update the dropdown to match the URL.
        company_from_url = None
        if url_search:
            query_params = urllib.parse.parse_qs(url_search.lstrip('?'))
            company_from_url = query_params.get('company', [None])[0]

        if company_from_url and company_from_url != dropdown_value:
            # Update dropdown if the URL contains a valid, different company
            return no_update, company_from_url, main.render_breadcrumbs(company_from_url)

        # If the URL is empty or the company is already selected, do nothing
        return no_update, no_update, main.render_breadcrumbs(company_from_url)

    # Fallback
    return no_update, no_update, no_update

# This callback runs in the browser (JavaScript) and updates the page title
# It triggers whenever the dropdown value changes
app.clientside_callback(
    """
    function(company) {
        if (company) {
            // Update the browser tab title
            document.title = company + " Valuation & Financial Analysis | RAST.guru";
        } else {
            // Default title if no company is selected
            document.title = "Stock Valuation & DCF | RAST.guru";
        }
        return ""; // Clientside callbacks must return something
    }
    """,
    Output('js-title-trigger', 'children'), # You'll need a hidden Div for this
    Input('dataset-selection', 'value')
)


# Callback to show/hide sections based on page
@callback(
    [
        Output("homepage-cards", "style"),  # To hide the homepage cards
        Output("functionalities-card", "style", allow_duplicate=True),  # To hide the functionalities
        Output("navbar", "style", allow_duplicate=True),  # To hide the navbar
        Output("dropdown-container", "style"),  # To hide the dropdown
        Output("ranking-grid", "style"),  # To display the ranking
        Output('card-welcome', "style", allow_duplicate=True),  # To display the welcome card on homepage
    ],
    Input("url", "pathname"),
    Input("url", "search"),
    prevent_initial_call=True
)
def toggle_page_layout(pathname, search):
    # --- CASE 1: RANKING PAGE ---------------------------------
    if pathname == "/ranking":
        # Hide homepage cards and right column, full width left
        return (
            {"display": "none"},  # Hide homepage cards
            {"display": "none"},  # Hide functionalities card
            {"display": "none"},  # Hide navbar
            {"display": "none"},  # Hide dropdown
            {"display": "block"},  # ranking-grid
            {"display": "none"},  # Hide card welcome
        )

    # --- CASE 2: COMPANY PAGE ---------------------------------
    # If search begins with ?company=
    if search and "company=" in search:
        return (
            {"display": "block"},  # homepage-cards
            {"display": "block"},  # functionalities-card
            {"display": "block"},  # navbar
            {  # dropdown-container visible
                "width": {"base": "200px", "sm": "250px", "lg": "400px"},
                "flex": "1",
                "maxWidth": {"lg": "80%"},
                "display": "block"
            },
            {"display": "none"},  # ranking-grid
            {"display": "none"},  # Hide card welcome
        )
    # --- CASE 3: PRICING PAGE ---------------------------------
    if pathname == "/pricing":
        # Hide homepage cards and right column, full width left
        return (
            {"display": "none"},  # Hide homepage cards
            {"display": "none"},  # Hide functionalities card
            {"display": "none"},  # Hide navbar
            {"display": "none"},  # Hide dropdown
            {"display": "none"},  # ranking-grid
            {"display": "none"},  # Hide card welcome
        )

    # --- CASE 4: HOMEPAGE -------------------------------------
    return (
        {"display": "none"},  # homepage-cards
        {"display": "none"},  # functionalities-card
        {"display": "none"},  # navbar
        {  # dropdown-container visible
            "width": {"base": "200px", "sm": "250px", "lg": "400px"},
            "flex": "1",
            "maxWidth": {"lg": "80%"},
            "display": "block"
        },
        {"display": "none"},  # ranking-grid
        {"display": "block"},  # Show card welcome
    )


# Callback loading and storing the company information
@app.callback(
    Output('all-companies-information', 'data'),
    Output(component_id='hyped-ranking-graph', component_property='figure'),  # Update graph 1
    Output(component_id='hyped-ranking-graph-company', component_property='figure'),  # Update graph 1
    Output(component_id='hyped-table-industry', component_property='data'),  # Update graph 1
    Output(component_id='valuation-category', component_property='data'),  # Update graph 1
    Input(component_id='dataset-selection', component_property='value'),
    Input('url', 'pathname'),  # Triggered once when the page is loaded
    State("pro-user-state", "data")
)
def initialize_data(dropdown_selection, path, pro_user_state):
    # ---- Performance assessment
    t2 = time.perf_counter(), time.process_time()
    logger.info(f" Time to launch the app (before the first callback")
    logger.info(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    logger.info(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
    logger.info("Loading company information")

    # Stopping callback if no company has been selected or if not in the ranking page
    if dropdown_selection is None and path != '/ranking':
        raise PreventUpdate

    # Load or compute data
    airtable_api = AirTableAPI()
    df_all_companies_information = airtable_api.get_hyped_companies_data()
    all_companies_information_store = df_all_companies_information.to_dict('records')

    # Create the list of industries for the ranking dropdown
    # Initialize label_list
    df_list = df_all_companies_information.copy()
    df_list.drop_duplicates(subset='Industry', inplace=True)
    industry_list = []
    for index, row in df_list.iterrows():
        industry = row['Industry']
        if pd.notna(industry) and industry is not None:  # Skip null/NaN values
            industry_list.append({
                "value": industry,
                "label": f"{industry}",
            })
    logger.info("List of industries")
    logger.info(industry_list)
    # Creates the graph mapping companies
    # Example company data
    # companies = ["Company A", "Company B", "Company C", "Company D"]
    companies = df_all_companies_information["Company Name"].tolist()
    growth_score = df_all_companies_information["Growth Score"].tolist()
    hype_score = df_all_companies_information["Hype Score"] + 3

    # Shift to make all positive, then log
    hype_score_log = np.log1p(hype_score + 2)  # +2 shifts so -1 becomes 1

    # Create figure
    fig = go.Figure()

    # Midpoints for quadrants (here using 0.5, adjust if needed, 1.386 for y because log1p(1+2)
    # x_mid, y_mid = 0.5, 1.386
    # x_mid, y_mid = 0.5, max(hype_score)/2
    y_min = min(hype_score)
    y1 = max(hype_score)
    y_mid = np.sqrt(y_min * y1)
    x_mid = 0.3

    # Convert to log10 exponents for positioning
    log_y_min = np.log10(y_min)
    log_y_max = np.log10(y1)
    log_y_mid = np.log10(y_mid)

    # Calculate annotation positions as EXPONENTS (not actual values)
    # Top annotations: 85% up from mid to max in log space
    log_y_top = log_y_mid + 0.95 * (log_y_max - log_y_mid)

    # Bottom annotations: 85% down from mid to min in log space
    log_y_bottom = log_y_mid - 0.85 * (log_y_mid - log_y_min)

    fig_company = copy.deepcopy(fig)

    # Annotations
    # Ranking graph

    # Add quadrant lines
    fig.add_shape(type="line", x0=x_mid, x1=x_mid, y0=y_min, y1=y1, line=dict(dash="dash", width=2, color="black"))
    fig.add_shape(type="line", x0=0, x1=1, y0=y_mid, y1=y_mid, line=dict(dash="dash", width=2, color="black"))

    # Optional: Add shaded quadrants
    fig.add_shape(type="rect", x0=x_mid, x1=1, y0=y_mid, y1=y1, fillcolor="lightgray", opacity=0.2, line_width=0)
    fig.add_shape(type="rect", x0=0, x1=x_mid, y0=y_mid, y1=y1, fillcolor="white", opacity=0.2, line_width=0)
    fig.add_shape(type="rect", x0=0, x1=x_mid, y0=y_min, y1=y_mid, fillcolor="lightgray", opacity=0.2, line_width=0)
    fig.add_shape(type="rect", x0=x_mid, x1=1, y0=y_min, y1=y_mid, fillcolor="#FFD000", opacity=0.2, line_width=0)

    # Add quadrant labels - position them in log space
    fig.add_annotation(x=0.65, y=log_y_top, text=" Hot & hyped ", showarrow=False, font=dict(size=12),
                       bgcolor="#F862F0")
    fig.add_annotation(x=0.15, y=log_y_top, text="<b> Bubble zone </b>", showarrow=False, font=dict(size=12),
                       bgcolor="#F862F0")
    fig.add_annotation(x=0.15, y=log_y_bottom, text=" Steady, Forgotten ", showarrow=False, font=dict(size=12),
                       bgcolor="#F862F0")
    fig.add_annotation(x=0.65, y=log_y_bottom, text="<b> Undervalued gems </b>", showarrow=False, font=dict(size=12),
                       bgcolor="#FED100")

    # Marking points as gold and bolded if in the "undervalued gems", otherwise as purple
    marker_colors = [
        "#C58400" if (x > x_mid and y < y_mid) else "#953AF6"
        for x, y in zip(growth_score, hype_score_log)
    ]

    # Alternate text positions to try to limit overlapping
    text_positions = ['top center' if i % 2 == 0 else 'bottom center' for i in range(len(growth_score))]

    # Layout tweaks
    fig.update_layout(
        xaxis=dict(
            title="Growth potential",
            range=[0, 1],
        ),
        yaxis=dict(
            title="Hype level (log scale)",
            type="log",
        ),
        plot_bgcolor="white",
        margin=go.layout.Margin(
            l=0,  # left margin
            r=0,  # right margin
            b=0,  # bottom margin
            t=20,  # top margin
        ),
    )

    # Add scatter points with labels
    fig.add_trace(go.Scatter(
        x=growth_score,
        y=hype_score,
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

    # Company-Specific quadrant

    df_all_companies_information.set_index("Company Name")
    selected_row = df_all_companies_information[df_all_companies_information['Company Name'] == dropdown_selection]

    OFFSET_LOG_SCALE = 3

    if dropdown_selection is not None:
        try:
            growth_score_company = df_all_companies_information[df_all_companies_information['Company Name'] == dropdown_selection]['Growth Score'].iloc[0]
            hype_score_company = df_all_companies_information[df_all_companies_information['Company Name'] == dropdown_selection]['Hype Score'].iloc[0] + OFFSET_LOG_SCALE
            selected_industry = selected_row['Industry'].iloc[0]
            ## Fetching the data of the competitors
            competitors_df = df_all_companies_information[
                (df_all_companies_information['Industry'] == selected_industry) &
                (df_all_companies_information['Company Name'] != dropdown_selection)
                ]
            competitors_names = competitors_df['Company Name'].tolist()
            competitors_growth = competitors_df['Growth Score'].tolist()
            competitors_hype = (competitors_df['Hype Score'] + OFFSET_LOG_SCALE).tolist()
        except KeyError:
            raise ValueError(f"Company '{dropdown_selection}' not found in the quadrant dataframe")

        # Add quadrant lines
        fig_company.add_shape(type="line", x0=x_mid, x1=x_mid, y0=y_min, y1=y1,
                              line=dict(dash="dash", width=2, color="#868786"))
        fig_company.add_shape(type="line", x0=0, x1=1, y0=y_mid, y1=y_mid,
                              line=dict(dash="dash", width=2, color="#868786"))

        # Add quadrant labels - position them in log space
        fig_company.add_annotation(x=0.65, y=log_y_top, text=" Hot & hyped ", showarrow=False, font=dict(size=12),
                                   bgcolor="#E2E2E2")
        fig_company.add_annotation(x=0.15, y=log_y_top, text=" Bubble zone ", showarrow=False, font=dict(size=12),
                                   bgcolor="#E2E2E2")
        fig_company.add_annotation(x=0.15, y=log_y_bottom, text=" Steady, Forgotten ", showarrow=False,
                                   font=dict(size=12),
                                   bgcolor="#E2E2E2")
        fig_company.add_annotation(x=0.65, y=log_y_bottom, text=" Undervalued gems ", showarrow=False,
                                   font=dict(size=12), bgcolor="#E2E2E2")

        if growth_score_company < x_mid and hype_score_company < y_mid:
            valuation_category = "lowGrowth_lowHype"
            fig_company.add_shape(type="rect", x0=0, x1=x_mid, y0=y_min, y1=y_mid, fillcolor="#9493FC", opacity=0.2,
                                  line_width=0)
            fig_company.add_annotation(x=0.15, y=log_y_bottom, text=" <b> Steady, Forgotten </b> ", showarrow=False,
                                       font=dict(size=12),
                                       bgcolor="#F862F0")
        elif growth_score_company > x_mid and hype_score_company < y_mid:
            valuation_category = "highGrowth_lowHype"
            fig_company.add_shape(type="rect", x0=x_mid, x1=1, y0=y_min, y1=y_mid, fillcolor="#FFD000", opacity=0.2,
                                  line_width=0)
            fig_company.add_annotation(x=0.65, y=log_y_bottom, text=" <b> Undervalued gems </b> ", showarrow=False,
                                       font=dict(size=12),
                                       bgcolor="#FED100")
        elif growth_score_company < x_mid and hype_score_company > y_mid:
            valuation_category = "lowGrowth_highHype"
            fig_company.add_shape(type="rect", x0=0, x1=x_mid, y0=y_mid, y1=y1, fillcolor="#FB4040", opacity=0.2,
                                  line_width=0)
            fig_company.add_annotation(x=0.15, y=log_y_top, text=" <b> Bubble Zone </b> ", showarrow=False,
                                       font=dict(size=12),
                                       bgcolor="#F862F0")
        else:
            valuation_category = "highGrowth_highHype"
            fig_company.add_shape(type="rect", x0=x_mid, x1=1, y0=y_mid, y1=y1, fillcolor="#9493FC", opacity=0.2,
                                  line_width=0)
            fig_company.add_annotation(x=0.65, y=log_y_top, text=" <b> Hot & hyped </b> ", showarrow=False,
                                       font=dict(size=12),
                                       bgcolor="#F862F0")
        # Add scatter points of all companies
        '''
        fig_company.add_trace(go.Scatter(
            x=growth_score,
            y=hype_score,
            hoverinfo="none",
            name=dropdown_selection,
            mode="markers+text",
            textfont=dict(size=8),
            marker=dict(
                size=10,
                color="#F2E5FF",
                line=dict(width=2, color="white")
            )
        ))
        '''

        # Add scatter points with labels
        if pro_user_state is False:
            competitor_labels = ["Competitors are visible to pro users only"] * len(competitors_names)
            fig_company.add_trace(go.Scatter(
                x=competitors_growth,
                y=competitors_hype,
                text="-",
                hovertext=competitor_labels,
                hoverinfo="text",
                name=selected_industry+" companies",
                mode="markers+text",
                textfont=dict(size=8),
                marker=dict(
                    size=10,
                    color="#953BF6",
                    line=dict(width=2, color="white")
                )
            )
            )
        # Add scatter points with labels
        else:
            competitor_labels = competitors_names
            fig_company.add_trace(go.Scatter(
                x=competitors_growth,
                y=competitors_hype,
                text=competitors_names,
                hovertext=competitor_labels,
                hoverinfo="text",
                hovertemplate=(
                        "<br><b>%{text}</b><br>" +  # Bold Company Name
                        "Growth score: %{x}<br>" +  # Value from x-axis
                        "Hype score: %{y}" +  # Value from y-axis
                        "<extra></extra>"  # Removes the secondary trace box
                ),
                textposition="bottom center",
                name="Competitors",
                mode="markers+text",
                textfont=dict(size=8),
                marker=dict(
                    size=10,
                    color="#953BF6",
                    line=dict(width=2, color="white")
                )
            ))

        # Position of the company label depending on where it is positioned in the quadrant
        if hype_score_company > 12:
            label_position = 'bottom center'
        elif hype_score_company > 12 and growth_score_company < 0.1:
            label_position = 'bottom right'
        elif growth_score_company < 0.1:
            label_position = 'middle right'
        elif growth_score_company < 0.1 and hype_score_company < 1.2:
            label_position = 'top right'
        elif hype_score_company < 1.2:
            label_position = 'top center'
        else:
            label_position = 'top center'

        # Add scatter point of the company with label
        fig_company.add_trace(go.Scatter(
            x=[growth_score_company],
            y=[hype_score_company],
            mode="markers+text",
            name=dropdown_selection,
            text=dropdown_selection,
            textposition=label_position,
            textfont=dict(size=12, family="Arial Black"),
            hovertemplate=(
                    f"<b>{dropdown_selection}</b><br>" +  # Bold Company Name
                    "Growth score: %{x}<br>" +  # Value from x-axis
                    "Hype score: %{y}" +  # Value from y-axis
                    "<extra></extra>"  # Removes the secondary trace box
            ),
            marker=dict(
                size=15,
                color="#F862F0",
                line=dict(width=4, color="white")
            ),
        ))

        # Update the figure layout
        fig_company.update_layout(
            # Remove margins
            margin=dict(l=0, r=0, t=0, b=0),
            # Hide legend
            showlegend=True,
            legend=dict(
                orientation="v",  # "h" for horizontal, "v" for vertical
                yanchor="top",
                y=1.15,  # Places legend above the chart
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                title="Growth potential",
                range=[0, 1],
                fixedrange=True,
                title_standoff=15
                # type="log"
            ),
            yaxis=dict(
                title="Hype level (log scale)",
                type="log",
                fixedrange=True,
            ),
            plot_bgcolor="white",
            # Deactivate zoom and interaction with the graph
            dragmode=False,
        )
    else:
        fig_company = fig
        valuation_category = ""

    return all_companies_information_store, fig, fig_company, industry_list, valuation_category


# Callback to enable the slider if "Custom" is selected
@app.callback(
    Output("range-slider-k", "disabled"),
    Output("range-arpu-growth", "disabled"),
    Output("range-discount-rate", "disabled"),
    Output("range-profit-margin", "disabled"),
    Output("all-sliders", "style"),

    [Input("dataset-selection", "value"),
     Input("scenarios-picker", "value")], prevent_initial_call=True)
def enable_slider(selection, scenario_value):
    visible_style = {"display": "block"}
    invisible_style = {"display": "hidden"}
    if IS_PRODUCTION:
        posthog.capture(
            event='scenario_selected',
            properties={
                'source_location': 'scenarios_picker',
                'scenario_name': scenario_value  # <-- The dynamic value from the input
            }
        )
    if scenario_value == "Nerd mode":
        return False, False, False, False, visible_style
    else:
        return True, True, True, True, invisible_style


# Callback displaying the functionalities & graph cards, and hiding the text
@app.callback(
    Output(component_id='functionalities-card', component_property='style'),
    Output(component_id='launch-counter', component_property='data'),
    Output("accordion-plateau", "disabled"),
    Output("accordion-valuation", "disabled"),
    Output("accordion-correlation", "disabled"),
    Output("accordion-product-maturity", "disabled"),
    Output("loader-general", "style", allow_duplicate=True),
    Output("homepage-cards", "style", allow_duplicate=True),
    Output("section-1", "style", allow_duplicate=True),
    Output("card-welcome", 'style'),
    Output("section-3", "style", allow_duplicate=True),
    Output("section-4", "style", allow_duplicate=True),
    Output("section-5", "style", allow_duplicate=True),
    Output("section-6", "style", allow_duplicate=True),
    Output("section-7", "style", allow_duplicate=True),
    Output("section-8", "style", allow_duplicate=True),
    Output("navbar", "style", allow_duplicate=True),  # showing navbar
    Input(component_id='dataset-selection', component_property='value'),
    [State('launch-counter', 'data')]
    , prevent_initial_call=True
)
def show_cards(data, launch_counter):
    if launch_counter['flag'] is not True:
        launch_counter['flag'] = True
        show_card = {'visibility': 'visible'}
        hide_graph_card = {'display': 'none'}
        display_card = {'display': 'block'}
        logger.info("Displaying the graph hihi")
        navbar_state = {"width": 250, "breakpoint": "sm", "style": {}}
        navbar_state["style"] = {"display": "block"}
        return {'display': 'block'}, launch_counter, False, False, False, False, show_card, display_card, display_card, hide_graph_card, \
            display_card, display_card, display_card, display_card, display_card, show_card, \
            {"visibility": "visible"}

    else:
        logger.info(f"Card already displayed {launch_counter}")
        raise PreventUpdate


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
    Output("summary-card-title", "children"),
    Output("company-info-text", "children"),
    Output("graph-title", "children"),
    Output("growth-card-title", "children"),
    Output("revenue-card-title", "children"),
    # Output("company-quadrant-card", "children"),
    # Output("graph-subtitle", "children"),
    Output(component_id='profit-margin', component_property='style'),  # Show/hide depending on company or not
    Output(component_id='discount-rate', component_property='style'),  # Show/hide depending on company or not
    Output(component_id='section-1', component_property='style'),  # Show/hide hypemetercard depending on company or not
    Output(component_id='arpu-growth', component_property='style'),  # Show/hide depending on company or not
    Output(component_id='profit-margin-container', component_property='children'),
    Output(component_id='best-profit-margin-container', component_property='children'),
    # Change the text below the profit margin slider
    Output(component_id='range-profit-margin', component_property='marks'),
    # Adds a mark to the slider if the profit margin > 0
    # Output(component_id='range-profit-margin', component_property='value'),
    # Sets the value to the current profit margin
    Output(component_id='total-assets', component_property='data'),  # Stores the current assets
    Output(component_id='users-revenue-correlation', component_property='data'),  # Stores the correlation between
    # Output(component_id='range-discount-rate', component_property='value'),
    Output(component_id='initial-sliders-values', component_property='data'),  # Stores the default slider values
    Output(component_id='data-source', component_property='children'),  # Stores the source of the data shown
    Output(component_id='data-selection-counter', component_property='data'),  # Flags that the data has changed
    Output("loader-general", "style", allow_duplicate=True),
    # Output(component_id='market-cap-tab', component_property='style'),  # Hides Market cap tab if other data is selected
    Output(component_id='symbol-dataset', component_property='data'),  # Hides Market cap tab if other data is selected
    Output(component_id='max-net-margin', component_property='data'),
    # Stores the max net margin opf the selected company
    Output('company-logo', 'src'),

    # the chosen KPI and the revenue

    Input(component_id='dataset-selection', component_property='value'),  # Take dropdown value
    Input(component_id='last-imported-data', component_property='data')],  # Take dropdown value
    Input(component_id='all-companies-information', component_property='data'),  # Take information about all companies
    # [State('main-plot-container', 'figure')],
    prevent_initial_call=True,
)
def set_history_size(dropdown_value, imported_df, df_all_companies):
    t1 = time.perf_counter(), time.process_time()
    logger.info(f"{IS_PRODUCTION = }")
    """
    Posthog event
    """
    # skipping it if no dropdown value is selected to avoid firing it when starting
    if dropdown_value is not None and IS_PRODUCTION:
        posthog.capture(
            event='dash_select_changed',
            properties={
                'location': 'dash_app',
                'selected_value': dropdown_value
            }
        )
    try:
        # Fetch dataset from API
        airtable_api = AirTableAPI()
        df = airtable_api.get_data(dropdown_value)
        if df.empty:
            dropdown_value = "Imported Data"
            df = pd.DataFrame(imported_df)
            key_unit = df.columns[1]
            data_source = "Import"
            df.columns = ['Date', 'Users']  # Renaming the columns the same way as Airtable
            symbol_company = "N/A"  # By default, imported data are not "Financial" data
            df['Revenue'] = 0
        else:
            key_unit = df.loc[0, 'Unit']
            data_source = df.loc[0, 'Source']
            symbol_company = df.loc[0, 'Symbol']

        # Fetches Max net Margin and stores it
        # max_net_margin = df_all_companies.loc[df_all_companies["Company Name"] == dropdown_value, "Max Net Margin"]
        max_net_margin = None
        company_logo_link_src = None

        # Ugly "if" statement making sure that the information are loaded, because it can happen that the initial callback is not triggered
        if not df_all_companies:
            df_all_companies_information = airtable_api.get_hyped_companies_data()
            df_all_companies = df_all_companies_information.to_dict('records')
        for company in df_all_companies:
            if company['Company Name'].lower() == dropdown_value.lower():
                max_net_margin = company['Max Net Margin']
                company_logo_link_src = company['Company Logo']
                description_company = company['Description']
                break

        # Creating the title & subtitle for the graph
        if symbol_company != "N/A":
            title_summary_card = dropdown_value + "'s current valuation in short" + " ($" + symbol_company + ")"
            company_description = dropdown_value + " is a " + description_company.lower()
            title_valuation_card = dropdown_value + "'s valuation over time"
            title_growth_card = dropdown_value + "'s " + key_unit + " over time"
            title_revenue_card = "Revenue per " + key_unit
        else:
            title_summary_card = dropdown_value + "'s current valuation in short"
            company_description = ""
            title_valuation_card = dropdown_value
            title_growth_card = dropdown_value + "'s " + key_unit + " over time"
            title_revenue_card = "Revenue per " + key_unit

        # Creating the source string for the graph
        if data_source == "Financial Report":
            source_string = "Data Source: " + dropdown_value + " Quarterly " + str(
                data_source) + " | Forecast: rast.guru"
        else:
            source_string = "Data Source: " + str(data_source)

        # Transforming it to a dictionary to be stored
        users_dates_dict = df.to_dict(orient='records')

        # Process & format df. The dates in a panda serie of format YYYY-MM-DD are transformed to a decimal yearly array
        dates = np.array(src.Utils.dates.date_formatting(df["Date"]))
        dates_formatted = dates + YEAR_OFFSET
        dates_unformatted = np.array(df["Date"])
        users_formatted = np.array(df["Users"]).astype(float) * 1000000

        logger.info("Basisnetmargin")
        logger.info(type(max_net_margin))
        logger.info(max_net_margin)

        # Logic to be used when implementing changing the ARPU depending on the date picked
        # date_last_quarter = main.previous_quarter_calculation().strftime("%Y-%m-%d")
        # closest_index = main.find_closest_date(date_last_quarter,dates_unformatted)

        # Check whether it is a public company: Market cap fetching & displaying profit margin,
        # discount rate and arpu for Companies
        if symbol_company != "N/A":
            hide_loader = {'display': ''}  # keep on showing the loader
            display_loading_overlay = False  # keep on showing the loading overlay
            show_company_functionalities = {'display': ''}  # Style component showing the fin. function.
            tab_selected = "1"  # show the first tab i.e. the valuation one
            try:
                # Ugly if to create exceptions for companies that have weird assets
                if dropdown_value == "Centene Corporation":
                    total_assets = 0
                else:
                    # Getting with API
                    yearly_revenue, total_assets = FinhubAPI().get_previous_quarter_revenue(symbol_company)
                logger.info("Latest yearly revenue & total assets fetched")
            except:
                logger.exception("Error fetching revenue & total assets, standard value assigned")
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
            users_revenue_regression = src.Utils.mathematics.linear_regression(users_correlation_sorted,
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
            display_loading_overlay = False  # keep on showing the loading overlay
            total_assets = 0
            show_company_functionalities = {'display': 'none'}
            tab_selected = "2"  # show the second tab i.e. the Growth one
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
        current_date = datetime.now()
        max_history_datepicker = current_date.date().isoformat()
        date_value_datepicker = max_history_datepicker  # Sets the value of the datepicker as the max date
        # current_date = dates_formatted[-1]
        logger.info(f"Other data : { min_history_datepicker = }; { max_dataset_date = };" +
                    f" { max_history_datepicker_date = }; { max_history_datepicker = }; { date_value_datepicker= }; ")

        # Discount Rate
        value_discount_rate_slider = 5

        # Graph creation
        hovertemplate_maingraph = "%{text}"
        y_legend_title = key_unit

        # Initial_sliders_values
        initial_sliders_values = {'slider_profit_margin': value_profit_margin_slider,
                                  'slider_discount_rate': value_discount_rate_slider}

        t2 = time.perf_counter(), time.process_time()
        logger.info(f" Calculation of the different sliders")
        logger.info(f" Real time: {t2[0] - t1[0]:.2f} seconds")
        logger.info(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
        return min_history_datepicker, max_history_datepicker, date_value_datepicker, users_dates_dict, \
               users_dates_formatted_dict, y_legend_title, title_summary_card, company_description, title_valuation_card, title_growth_card, title_revenue_card, \
               show_company_functionalities, show_company_functionalities, show_company_functionalities, \
               show_company_functionalities, text_profit_margin, text_best_profit_margin, marks_profit_margin_slider, \
               total_assets, users_revenue_regression, \
               initial_sliders_values, source_string, True, True, symbol_company, max_net_margin, company_logo_link_src
    except:
        logger.exception(f"Error fetching or processing dataset")
        raise PreventUpdate


@app.callback(
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
    Output(component_id="growth-score-text", component_property="children"),  # hype score text
    Output(component_id="growth-score", component_property="data"),  # hype score text

    Input(component_id='dataset-selection', component_property='value'),  # Take dropdown value
    Input(component_id='date-picker', component_property='value'),  # Take date-picker date
    Input("scenarios-picker", "value"),  # Input the scenario to reset the position of the slider to the best scenario
    Input(component_id='users-dates-formatted', component_property='data'),
    Input(component_id='users-revenue-correlation', component_property='data'),
    Input(component_id='graph-unit', component_property='data'),  # Getting the Unit used
    Input(component_id='users-dates-raw', component_property='data'),
    Input(component_id='initial-sliders-values', component_property='data'),
    State(component_id='symbol-dataset', component_property='data'),
    State(component_id='max-net-margin', component_property='data'),  # Max net margin opf the selected company
    prevent_initial_call=True)
# Analysis to load the different scenarios (low & high) when a dropdown value is selected
def load_data(dropdown_value, date_picked, scenario_value, df_dataset_dict,
              users_revenue_correlation, key_unit, df_raw, initial_slider_values, symbol_dataset, max_net_margin):
    logger.info("Starting scenarios calculation")
    t1 = time.perf_counter(), time.process_time()
    date_picked_formatted = src.Utils.dates.date_formatting_from_string(date_picked)
    logger.info("datedate")
    df_dataset = pd.DataFrame(df_dataset_dict)
    logger.info(f"DF_dataset_first {df_dataset}")
    if dropdown_value is None or df_dataset is None or df_raw is None:
        raise PreventUpdate
    # Dates array definition from dictionary
    dates_raw = np.array([entry['Date'] for entry in df_raw])
    dates_new = np.array([entry['Date'] for entry in df_dataset_dict])
    dates = dates_new - 1970
    data_len = len(src.Utils.dates.get_earlier_dates(dates, date_picked_formatted - 1970))
    # Users are taken from the database and multiply by a million
    users_new = np.array([entry['Users'] for entry in df_dataset_dict])
    users_original = users_new.astype(float) * 1000000
    closest_index = data_len - 1  # Index of the last data matching the date selected
    current_annual_profit_margin = df_dataset.loc[closest_index, 'Profit Margin']
    current_revenue_array = np.array(df_dataset['Revenue'])
    current_revenue_array = current_revenue_array[:closest_index + 1]
    research_and_development = np.array(df_dataset['Research_And_Development'])
    current_research_and_development = research_and_development[:closest_index + 1]
    share_research_and_development = current_research_and_development / current_revenue_array * 100

    users = users_original
    # Resizing of the dataset taking into account the date picked
    history_value_formatted = date_picked_formatted - 1970  # New slider: Puts back the historical value to the format for computations
    dates_actual = src.Utils.dates.get_earlier_dates(dates, history_value_formatted)
    current_users_array = users_new * 1e6
    current_users = current_users_array[closest_index]

    # All parameters are calculated by ignoring data 1 by 1, taking the history reference as the end point
    df_full = src.ParametersDataFrame.parameters_dataframe(dates[0:data_len],
                                        users[0:data_len])  # Dataframe containing all parameters with all data ignored
    logger.info(f"{df_full = }")
    df_sorted = src.ParametersDataFrame.parameters_dataframe_cleaning(df_full, users[
                                                            0:data_len])  # Dataframe where inadequate scenarios are eliminated
    logger.info(f"{df_sorted = }")

    if df_sorted.empty:
        logger.info("No good scenario could be calculated")
        df_sorted = src.ParametersDataFrame.parameters_dataframe_cleaning_minimal(df_full, users[0:data_len])
        if df_sorted.empty:
            logger.info("No good scenario AT ALL could be calculated, all kind of scenarios are considered")
            df_sorted = df_full
    else:
        logger.info("Successful scenarios exist")
    logger.info(f"{df_sorted = }")
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
    u = users[-1] / k_scenarios[-1]

    # Core, stage-aware momentum (dimensionless)
    g = r_scenarios[-1] * (1 - u)

    # Headroom (dimensionless) - captures how far they are from saturation regardless of speed
    h = 1 - u

    # Calculation of a reference r, by winsorizing at 5 - 95 pct -> it should be done across ALL companies
    # r_wins = mstats.winsorize(r_scenarios, limits=[0.05, 0.05])  # returns numpy masked array
    r_ref_global = 0.4

    # Growth score calculation (early rocket: low u, high r): BIG GS | tired incumbent (high u, low r): low GS
    # Here we take a simple 0.5 weight, different weight could be given to the headroom or core
    growth_score = 0.5 * g / r_ref_global + 0.5 * h

    badge_color_growth, badge_label_growth = main.growth_meter_indicator_values(growth_score)
    growth_score_text = dmc.Group([
        dmc.Text(f"Growth score: {growth_score:.2f}", size="sm"),
        dmc.Badge(badge_label_growth, size="xs", variant="outline", color=badge_color_growth)
    ], gap="md")

    logger.info("GS growth score")
    logger.info(growth_score)

    # Growth Rate
    rd = src.analysis.discrete_growth_rate(users[0:data_len], dates[0:data_len] + 1970)
    average_rd = sum(rd[-3:]) / 3

    # Growth Rate Graph message
    if average_rd < 0.1:
        growth_rate_graph_message1 = dmc.Text(
            children=[
                "The discrete growth rate indicates where ",
                dropdown_value,
                " is along its S-curve. When it reaches 0, growth of its ",
                key_unit,
                " ends. The flatter the regression line (purple) the longer the growth phase. For ",
                dropdown_value,
                ", the average annual discrete growth rate is approaching 0 (",
                f"{average_rd:.1f}), indicating an approaching end of the growth."
            ],
            size="sm")
        growth_rate_graph_color = "yellow"
        if any(r < 0 for r in r_full[-5:]):
            growth_rate_graph_message1 = dmc.Text(
                children=[
                    growth_rate_graph_message1,
                    " However, the latest growth rates vary substantially, which could lead to a prolonged growth."
                ]
                , size="sm")
    else:
        growth_rate_graph_message1 = dmc.Text(
            children=[
                "The discrete growth rate indicates where ",
                dropdown_value + " is along its S-curve. When it reaches 0, growth of its ",
                key_unit,
                " has ended. The flatter the regression line (purple) the longer the growth phase. For ",
                dropdown_value,
                ", the line is still far away from zero, indicating a substantial growth ahead."
            ],
            size="sm")

        growth_rate_graph_color = "green"

    # Revenue Graph Message
    revenue_graph_message = dmc.Text("The graph shows revenue per " + key_unit + " (purple bars) and profit margin (pink line).\n" \
                            " The dotted line represents projected revenue growth, adjustable with the Revenue slider.\n" \
                            " The max net margin indicates the theoretical maximum margin for " + dropdown_value + ".", size="sm")
    revenue_graph_message_color = "primaryPurple"

    # Product Maturity Graph Message
    if np.all(share_research_and_development == 0):
        product_maturity_graph_message = dmc.Text("No R&D data available at the moment for " + str(dropdown_value) + " 🫣", size="sm")
        product_maturity_graph_message_color = "gray"
        product_maturity_accordion_title = "No Data Available 🫣"
        product_maturity_accordion_body = "At the moment no data is available for " + str(dropdown_value) + " 🫣"
        product_maturity_accordion_color = "gray"
        product_maturity_accordion_icon_color = DashIconify(icon="fluent-mdl2:product-release",
                                                            color=dmc.DEFAULT_THEME["colors"]["gray"][6],
                                                            width=20)
    elif share_research_and_development[-1] > 30:
        product_maturity_graph_message = dmc.Text("Tech companies often invest a large share of their revenue in R&D, " \
                                                  "and decrease it as their products mature. Currently, " \
                                                  + dropdown_value + " is investing heavily in development: a sign that " \
                                                                     "its revenue & profit margin could grow significantly in the future.",
                                                  size="sm")
        product_maturity_graph_message_color = "green"
        product_maturity_accordion_title = "The Product is Growing!"
        product_maturity_accordion_body = dmc.Text(
            children=[
                "At the moment, ",
                str(dropdown_value),
                " is heavily investing in its product, indicating that the revenue & profit margin may strongly grow in the future."], size="sm")
        product_maturity_accordion_color = "green"
        product_maturity_accordion_icon_color = DashIconify(icon="fluent-mdl2:product-release",
                                                            color=dmc.DEFAULT_THEME["colors"]["green"][6],
                                                            width=20)

    elif share_research_and_development[-1] > 10:
        product_maturity_graph_message = dmc.Text("Tech companies often invest a large share of their revenue in R&D. " \
                                            "Currently, " + str(dropdown_value) + " is limiting its investment in " \
                                          "its product, indicating that the product is on its way to being mature and " \
                                                                                  "limited profit margin improvements should be expected.", size="sm")
        product_maturity_graph_message_color = "yellow"
        product_maturity_accordion_title = "The Product is Maturing"
        product_maturity_accordion_body = dmc.Text(
            children=[
                "At the moment, " + str(dropdown_value) + \
                                         " is limiting its investment in its product, indicating that the revenue and " \
                                         "profit margin should stabilize."
            ],
            size="sm")
        product_maturity_accordion_color = "yellow"
        product_maturity_accordion_icon_color = DashIconify(icon="fluent-mdl2:product-release",
                                                            color=dmc.DEFAULT_THEME["colors"]["yellow"][6],
                                                            width=20)
    else:
        product_maturity_graph_message = dmc.Text(
            children=[
                "At the moment, ",
                str(dropdown_value),
                " is heavily limiting its product investment, indicating that limited improvement on profit "
                "margin is to be expected"],
            size="sm")
        product_maturity_graph_message_color = "red"
        product_maturity_accordion_title = "The Product is Mature"
        product_maturity_accordion_body = dmc.Text(
            children=[
                "At the moment, ",
                str(dropdown_value),
                " is heavily limiting its investment in its product, indicating that limited improvement on the "
                "profit margin is to be expected"
            ])
        product_maturity_accordion_color = "red"
        product_maturity_accordion_icon_color = DashIconify(icon="fluent-mdl2:product-release",
                                                            color=dmc.DEFAULT_THEME["colors"]["red"][6],
                                                            width=20)

    # Growth Accordion
    # Promising Growth
    if diff_r2lin_log > 0.1 or any(k < 0 for k in k_full[-7:-4]) or any(r < 0 for r in r_full[-7:-4] if r > 0.1):
        growth_message_title = "Promising Exponential Growth Ahead!"
        growth_message_body = "Rast's model predicts a strong likelihood of exponential growth in the foreseeable " \
                              "future, surpassing the best-case scenario displayed."
        growth_message_color = "green"
        growth_icon_color = DashIconify(icon="uit:chart-growth", color=dmc.DEFAULT_THEME["colors"]["green"][6],
                                        width=20)

    # Stable Growth
    else:
        growth_message_title = "Consistent and Predictable Growth!"
        growth_message_body = "Rast's model suggests a high probability that the dataset has transitioned into a " \
                              "stable growth pattern, aligning closely with our best-case scenario."
        growth_message_color = "yellow"
        growth_icon_color = DashIconify(icon="uit:chart-growth", color=dmc.DEFAULT_THEME["colors"]["yellow"][6],
                                        width=20)

    # High Growth
    if k_scenarios[-1] < 1e9:
        plateau_high_growth = f"{k_scenarios[-1] / 1e6:.1f} M"
    else:
        plateau_high_growth = f"{k_scenarios[-1] / 1e9:.1f} B"
    time_high_growth = src.analysis.time_to_population(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1],
                                                       k_scenarios[-1] * 0.9) + 1970
    # Low Growth
    if k_scenarios[0] < 1e9:
        plateau_low_growth = f"{k_scenarios[0] / 1e6:.1f} M"
    else:
        plateau_low_growth = f"{k_scenarios[0] / 1e9:.1f} B"
    time_high_growth = src.analysis.time_to_population(k_scenarios[0], r_scenarios[0], p0_scenarios[0],
                                                       k_scenarios[0] * 0.9) + 1970
    # Best Growth
    if k_scenarios[highest_r2_index] < 1e9:
        plateau_best_growth = f"{k_scenarios[highest_r2_index] / 1e6:.1f} M"
    else:
        plateau_best_growth = f"{k_scenarios[highest_r2_index] / 1e9:.1f} B"

    time_best_growth = src.analysis.time_to_population(k_scenarios[highest_r2_index],
                                                       r_scenarios[highest_r2_index],
                                                       p0_scenarios[highest_r2_index],
                                                       k_scenarios[highest_r2_index] * 0.95) + 1970

    # Plateau Accordion
    if diff_r2lin_log > 0.1:
        plateau_message_title = "The revenue is unlikely to stop growing before " + \
                                src.Utils.dates.string_formatting_to_date(time_high_growth)
        plateau_message_body = "Given the likelihood of exponential growth in the foreseeable " \
                               "future, the high growth scenario is likely with 95% of its plateau at " + \
                               str(plateau_high_growth) + " users which should happen in " + src.Utils.dates.string_formatting_to_date(
            time_high_growth) + ". If overvalued, the company's hype can remain a while until the revenue stop growing."
    else:
        plateau_message_title = "Plateau could be reached in " + src.Utils.dates.string_formatting_to_date(time_best_growth) \
                                + " with " + str(plateau_best_growth) + " users"
        plateau_message_body = "Given the likelihood of a stable growth in the foreseeable " \
                               "future, the best growth scenario is likely to reach 95% of its plateau in " \
                               + src.Utils.dates.string_formatting_to_date(time_best_growth) + " with " + str(
            plateau_best_growth) + " users"
    # Plateau message color
    if time_best_growth < date_picked_formatted:
        plateau_message_color = "red"
        plateau_icon_color = DashIconify(icon="simple-icons:futurelearn", color=dmc.DEFAULT_THEME["colors"]["red"][6],
                                         width=20)
    else:
        plateau_message_color = "green"
        plateau_icon_color = DashIconify(icon="simple-icons:futurelearn", color=dmc.DEFAULT_THEME["colors"]["green"][6],
                                         width=20)

    # Formatting of the displayed correlation message

    formatted_correlation = f"{users_revenue_correlation * 100:.2f}"  # Formatting the displayed r^2:
    if users_revenue_correlation >= 0.6:
        correlation_message_title = str(key_unit) + " is a great revenue indicator"
        correlation_message_body = "We use " + str(key_unit) + " as a key revenue driver" \
                                                            " to estimate the valuation, because " + str(key_unit) + \
                                   " account for " + str(formatted_correlation) + "% of the revenue variability."
        correlation_message_color = "primaryGreen"
        correlation_icon_color = DashIconify(icon="lineicons:target-revenue",
                                             color=dmc.DEFAULT_THEME["colors"]["green"][6],
                                             width=20)
    elif users_revenue_correlation > 0:
        correlation_message_title = "Take it with a grain of salt"
        correlation_message_body = str(key_unit) + " do not have a strong correlation with the revenue over time. " \
                                                   "We are looking into alternative metrics to estimate this " \
                                                   "company's valuation, since only " + str(formatted_correlation) + \
                                   "% of the revenue variability is explained by this metric."
        correlation_message_color = "yellow"
        correlation_icon_color = DashIconify(icon="lineicons:target-revenue",
                                             color=dmc.DEFAULT_THEME["colors"]["yellow"][6],
                                             width=20)

    else:
        correlation_message_title = "Correlation not applicable"
        correlation_message_body = "The correlation information is only relevant for companies"
        correlation_message_color = "gray"
        correlation_icon_color = DashIconify(icon="lineicons:target-revenue",
                                             color=dmc.DEFAULT_THEME["colors"]["gray"][6],
                                             width=20)

    # Slider definition
    df_scenarios = df_sorted
    data_ignored_array = df_scenarios.index.to_numpy()
    slider_max_value = data_ignored_array[-1]

    # Defining the upper/lower limit after which the star is displayed right next to the label
    percentage_limit_label = 0.1
    max_limit_slider_label = data_ignored_array[int(len(data_ignored_array) * (1 - percentage_limit_label))]
    min_limit_slider_label = data_ignored_array[int(len(data_ignored_array) * percentage_limit_label)]
    logger.info(max_limit_slider_label)
    logger.info(min_limit_slider_label)
    logger.info(highest_r2_index)
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
            latest_market_cap = FinhubAPI.get_marketcap(symbol_company)
            if latest_market_cap is None:
                raise ValueError("Market cap returned None")
            logger.info(f"{latest_market_cap = }")
        except Exception as e:
            logger.info("Couldn't fetch latest market cap, assigning DB value")
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
        # current_arpu = yearly_revenue_quarters / average_users_past_year
        current_arpu = sum(quarterly_revenue[-4:] / current_users_array[closest_index - 4:closest_index])
        printed_current_arpu = f"{current_arpu:.0f} $ (current arpu)"  # formatting
        first_arpu = quarterly_revenue[0] / current_users_array[0]
        logger.info(f"FirstARPU = {first_arpu}")
        # arpu_growth_calculated = current_arpu/(first_arpu * (dates[data_len] - dates[3]))
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
    try:
        arpu_needed = src.analysis.arpu_for_valuation(k_scenarios[highest_r2_index], r_scenarios[highest_r2_index],
                                                      p0_scenarios[highest_r2_index], 0.2, 0.05, 10,
                                                      current_market_cap * 1000000)
    except Exception as e:
        arpu_needed = 0

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
        valuation_icon_color = DashIconify(icon="radix-icons:rocket", color=dmc.DEFAULT_THEME["colors"]["green"][6],
                                           width=20)
    else:
        valuation_message_title = "Valuation not applicable"
        valuation_message_body = "The valuation information is only relevant for companies"
        valuation_message_color = "gray"
        valuation_icon_color = DashIconify(icon="radix-icons:rocket", color=dmc.DEFAULT_THEME["colors"]["gray"][6],
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
        growth_slider_value = base_growth  # bringing it back to the base case, to avoid clash when changing date-picker

    t2 = time.perf_counter(), time.process_time()
    logger.info(f" Definition of the messages in analysis and above the graphs")
    logger.info(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    logger.info(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
    return initial_slider_values, \
           ["valuation"], plateau_message_title, plateau_message_body, plateau_message_color, plateau_icon_color, \
           correlation_message_title, correlation_message_body, \
           correlation_message_color, correlation_icon_color, product_maturity_accordion_title, product_maturity_accordion_body, \
           product_maturity_accordion_color, product_maturity_accordion_icon_color, df_sorted_dict, slider_max_value, marks_slider, current_arpu, hype_market_cap, \
           current_market_cap, latest_market_cap, growth_rate_graph_message1, growth_rate_graph_color, \
           product_maturity_graph_message, product_maturity_graph_message_color, revenue_graph_message, \
           revenue_graph_message_color, growth_slider_value, arpu_growth_slider_value, discount_rate_slider_value, profit_margin_slider_value, growth_score_text, growth_score


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
        State(component_id='date-picker', component_property='value'),  # Take date-picker date
        Input(component_id='users-dates-formatted', component_property='data'),
        Input(component_id='scenarios-sorted', component_property='data'),
        State(component_id='graph-unit', component_property='data'),  # Stores the graph unit (y axis legend)
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
    logger.info(f"ProfitMargin {profit_margin_array}")

    # Gets the date selected from the new date picker
    date_picked_formatted = src.Utils.dates.date_formatting_from_string(date_picked_formatted_original)
    history_value = date_picked_formatted
    history_value_graph = datetime.strptime(date_picked_formatted_original, "%Y-%m-%d")
    # Extract the x-coordinate for the vertical line
    x_coordinate = history_value_graph

    # Calculating the length of historical values to be considered in the plots
    # history_value_formatted = history_value[0] - 1970  # Puts back the historical value to the format for computations
    history_value_formatted = date_picked_formatted - 1970  # New slider: Puts back the historical value to the format for computations
    dates_actual = src.Utils.dates.get_earlier_dates(dates, history_value_formatted)
    data_len = len(dates_actual)  # length of the dataset to consider for retrofitting
    users_actual = users[0:data_len]

    logger.info(f"Selected date {date_picked_formatted}")
    logger.info(graph_unit)

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
    logger.info(f"{moving_average = }")
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

    logger.info(f"Value Ring: {value_section = }, {r_squared_showed = }")

    highest_r2_index = np.argmax(rsquared_scenarios)
    logger.info(f"HIGHEST {highest_r2_index}")

    # Graph message

    # Selected Growth
    if k_scenarios[data_slider] < 1e6:
        plateau_selected_growth = f"{k_scenarios[data_slider]:.0f}"
    elif k_scenarios[data_slider] < 1e9:
        plateau_selected_growth = f"{k_scenarios[data_slider] / 1e6:.1f} M"
    else:
        plateau_selected_growth = f"{k_scenarios[data_slider] / 1e9:.1f} B"
    time_selected_growth = src.analysis.time_to_population(k_scenarios[data_slider],
                                                           r_scenarios[data_slider],
                                                           p0_scenarios[data_slider],
                                                           k_scenarios[data_slider] * 0.9) + 1970

    today_time = src.Utils.dates.date_formatting_from_string(datetime.today().strftime('%Y-%m-%d'))
    if time_selected_growth < today_time:
        past_tense = " started approaching 90% of its peak in "
    else:
        past_tense = " will be approaching 90% of its peak as of "
    graph_message = dmc.Text(children=[
        dmc.Text("The pink bars ", span=True, c="#F862F0", fw=600),
        "show how " + dropdown_value + "’s " + graph_unit + " (the key revenue driver) have grown over time. ",
        dmc.Text("The yellow zone ", span=True, c="#C48501", fw=600), "is our forecast range, " \
                                                                      "showing how this driver should evolve in the future. These drivers follow an S-curve: " \
                                                                      "fast growth at first, then a gradual slowdown.\n" \
                                                                      " With the selected growth, the",
        dmc.Text(" plateau ", span=True, c="#953BF6", fw=600), past_tense,
        dmc.Text(src.Utils.dates.string_formatting_to_date(time_selected_growth) + ", projected at " \
                 + str(plateau_selected_growth) + " " + str(graph_unit), span=True, c="#953BF6", fw=600),
    ],
        size="sm",
        # fw=300,
    )

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
                                  marker_color='#FFA8FB', text=formatted_y_values,
                                  hovertemplate=hovertemplate_maingraph))
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
        range_y = [0, src.Utils.Logistics.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1], [60])[
            0] * 1.3]
    else:
        range_y = [0, users_raw[-1] * 1.2]

    fig_main.update_layout(
        hovermode="x unified",
        annotations=[
            dict(
                x=(x_coordinate + relativedelta(months=9)).strftime("%Y-%m-%d"),
                y=0.6 * src.Utils.Logistics.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1], [60]),
                text="F O R E C A S T",
                showarrow=False,
                font=dict(size=8, color="black"),
                opacity=0.5,
            )
        ],
        yaxis=dict(
            title=graph_unit,
            range=range_y
        ),
        margin=dict(t=40, b=10, l=5, r=5),
    )

    # Prediction, S-Curves

    date_a = datetime.strptime(dates_raw[0], "%Y-%m-%d")
    # date_b = datetime.strptime(dates_raw[-1], "%Y-%m-%d")
    date_b = datetime.strptime(dates_raw[-1], "%Y-%m-%d")

    # date_b_actual = history_value_graph  # Date including the datepicker
    date_b_actual = datetime.strptime(dates_raw[data_len - 1], "%Y-%m-%d")

    # Calculate date_end using the formula date_b + 2 * (date_b - date_a)
    date_end = date_b + (date_b - date_a)

    date_end_formatted = src.Utils.dates.date_formatting_from_string(date_end.strftime("%Y-%m-%d"))

    # Add S-curve - S-Curve the user can play with
    x = np.linspace(dates[0], float(date_end_formatted) - 1970, num=50)

    x_scenarios = np.linspace(dates_actual[-1], float(date_end_formatted) - 1970, num=50)  # changed
    y_predicted = src.Utils.Logistics.logisticfunction(k, r, p0, x_scenarios)
    # Generate x_dates array
    x_dates = np.linspace(date_a.timestamp(), date_end.timestamp(), num=50)
    x_dates_scenarios = np.linspace(date_b_actual.timestamp(), date_end.timestamp(), num=50)  # changed
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
    y_trace = src.Utils.Logistics.logisticfunction(k_scenarios[0], r_scenarios[0], p0_scenarios[0], x_scenarios)
    formatted_y_values = [
        f"{y:.3f}" if y < 1e6 else f"{y / 1e6:.3f} M" if y < 1e9 else f"{y / 1e9:.3f} B"
        for y in y_trace
    ]
    fig_main.add_trace(go.Scatter(name="Low Growth", x=x_dates_scenarios,
                                  y=src.Utils.Logistics.logisticfunction(k_scenarios[0], r_scenarios[0],
                                                                         p0_scenarios[0], x_scenarios),
                                  mode='lines',
                                  line=dict(color='#C58400', width=0.5), showlegend=False, text=formatted_y_values,
                                  hovertemplate=hovertemplate_maingraph)),
    # fig.add_trace(go.Line(name="Predicted S Curve", x=x + 1970,
    # y=main.logisticfunction(k_scenarios[1], r_scenarios[1], p0_scenarios[1], x), mode="lines"))
    y_trace = src.Utils.Logistics.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1], x_scenarios)
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
    y_area_low = src.Utils.Logistics.logisticfunction(k_scenarios[0], r_scenarios[0], p0_scenarios[0],
                                                      x_scenarios)  # Low growth array
    y_area_high = src.Utils.Logistics.logisticfunction(k_scenarios[-1], r_scenarios[-1], p0_scenarios[-1],
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
    logger.info("Userbase Graph printed")
    logger.info("Image created")

    x1 = np.linspace(dates[-1] + 0.25, dates[-1] + 10, num=10)
    # Add predicted bars
    # marker_color='White', marker_line_color='Black'))

    # Build second chart containing the discrete growth rates & Regressions
    # -------------------------------------------------------

    fig_second = go.Figure(layout=layout_growth_rate_graph)
    fig_second.update_xaxes(range=[0, users[-1] * 1.1],
                            title=graph_unit)  # Fixing the size of the X axis with users max + 10%
    dates_moved, users_moved = src.Utils.mathematics.moving_average_smoothing(dates, users, moving_average)

    # Defining the min as zero or less if the minimum is negative
    if min(src.analysis.discrete_growth_rate(users_moved, dates_moved + 1970) - 0.05) > 0:
        fig_second.update_yaxes(range=[0,
                                       max(src.analysis.discrete_growth_rate(users_moved, dates_moved + 1970) + 0.05)])
    else:
        fig_second.update_yaxes(range=[min(src.analysis.discrete_growth_rate(users_moved, dates_moved + 1970) - 0.05),
                                       max(src.analysis.discrete_growth_rate(users_moved, dates_moved + 1970) + 0.05)])
    fig_second.add_trace(
        go.Scatter(name="Discrete Growth Rate Smoothened by moving average: " + str(moving_average),
                   x=src.analysis.discrete_user_interval(users_moved),
                   y=src.analysis.discrete_growth_rate(users_moved, dates_moved + 1970), mode="markers",
                   line=dict(color='#F963F1')
                   ))
    logger.info(f"{users = } - {dates + 1970}")
    logger.info(src.analysis.discrete_growth_rate(users, dates + 1970))
    # Add trace of the regression
    fig_second.add_trace(
        go.Scatter(name="Regression", x=src.analysis.discrete_user_interval(users),
                   y=-r / k * src.analysis.discrete_user_interval(users) + r, mode="lines", line=dict(color='#953AF6')))

    if number_ignored_data > 0:
        fig_second.add_trace(
            go.Scatter(name="Ignored Data Points",
                       x=src.analysis.discrete_user_interval(users_moved[0:number_ignored_data]),
                       y=src.analysis.discrete_growth_rate(users_moved[0:number_ignored_data],
                                                           dates_moved[0:number_ignored_data] + 1970),
                       mode="markers", line=dict(color='#808080')))

    # Changes the color of the scatters after the date considered
    if data_len < len(dates):
        fig_second.add_trace(
            go.Scatter(name="Discrete Growth Rate", x=src.analysis.discrete_user_interval(users[data_len:]),
                       y=src.analysis.discrete_growth_rate(users[data_len:], dates[data_len:] + 1970),
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
        x1=users[-1] * 1.1,
        y0=0,
        y1=0,
        line=dict(color="black", width=1, dash="dot")
    )
    fig_second.update_layout(
        annotations=[
            dict(
                x=users[0],
                y=0.01,
                text="Growth end",
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
    logger.info(p0)
    if p0 > 2.192572e-11:
        t_plateau = src.analysis.time_to_population(k, r, p0, 0.95 * k) + 1970
        month_plateau = math.ceil((t_plateau - int(t_plateau)) * 12)
        if month_plateau == 0:  # sometimes month_plateau is 0, quick fix to be improved
            month_plateau = 1
        year_plateau = int(np.round(t_plateau, 0))
        date_plateau = datetime(year_plateau, month_plateau, 1).date()
        date_plateau_displayed = date_plateau.strftime("%b, %Y")
        t_plateau_displayed = 'Year {:.1f}'.format(t_plateau)
        logger.info("Plateau calculated correctly")
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
        dates_revenue_actual = src.Utils.dates.get_earlier_dates(dates[valid_indices], history_value_formatted)
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
                name="Annual Revenue per Unit (arpu)",
                x=x_revenue,
                y=y_revenue,
                # mode='lines',
                marker_color='#953AF6',
                opacity=0.8,
                # showlegend=False,
                # text=formatted_y_values,
                # hovertemplate=hovertemplate_maingraph
            ),
                # secondary_y=True,
            )
            fig_revenue.add_trace(go.Scatter(
                name="Future Annual Revenue per Unit (arpu)",
                x=future_arpu_dates,
                y=future_arpu,
                mode='lines',
                line_dash="dot",
                marker=dict(color='#FFD000', size=4),
                showlegend=True,
                text=formatted_y_values,
                hovertemplate=hovertemplate_maingraph),
                # secondary_y=True,
            )
            # Revenue past the selected date that are known [data_len:]
            fig_revenue.add_trace(go.Scatter(
                name="Annual Revenue per Unit (ARPU)",
                x=x_revenue[len(dates_revenue_actual):],
                y=y_revenue[len(dates_revenue_actual):],
                mode='lines',
                line=dict(color='Gray', width=1),
                showlegend=False,
                # text=formatted_y_values, #
                hovertemplate=hovertemplate_maingraph),
                # secondary_y=True,
            )
            fig_revenue.update_yaxes(range=[min(annual_revenue_per_user) * 0.9, max(annual_revenue_per_user) * 1.5],
                                     title="ARPU (" + graph_unit + ") [$]",
                                     color="#953AF6")
            fig_revenue.add_trace(go.Scatter(
                name="Profit Margin",
                x=x_revenue,
                y=profit_margin_array[valid_indices],
                mode='lines',
                # line_dash="dot",
                marker=dict(color='#F963F1', size=4),
                showlegend=True,
                # text=formatted_y_values,
                # hovertemplate=hovertemplate_maingraph
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

            fig_revenue.update_yaxes(range=[min(profit_margin_array) - abs(min(profit_margin_array)) * 0.1,
                                            max_net_margin * 1.2],
                                     title_text="Profit Margin [%]",
                                     color="#F963F1",
                                     secondary_y=True,
                                     fixedrange=True,
                                     )
            logger.info("Fig Revenue Printed")

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
            logger.info("No revenue to be added to the graph")
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
                x0=(dates_research_and_development[0] - pd.DateOffset(months=6)).strftime('%Y-%m-%d'),
                x1=(dates_research_and_development[-1] + pd.DateOffset(months=6)).strftime('%Y-%m-%d'),
                y0=0,
                y1=10,
                # xref="paper", yref="y",
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
            x=(dates_research_and_development[0] - pd.DateOffset(months=6)).strftime('%Y-%m-%d'),
            # Align left within the rectangle
            y=(30 + 100) / 2,  # Center vertically within the rectangle
            xref="x",
            yref="y",
            text="  Heavy Product Investments",
            showarrow=False,
            font=dict(color="#4946F2", size=12),
            align="left",
            xanchor="left",
            # bgcolor="rgba(231, 245, 255, 0.8)"  # Matching background color for better visibility
        )
        # Add graph line
        formatted_y_values = [
            f"{y:.2f}%" for y in share_research_and_development
        ]
        fig_product_maturity.add_trace(
            go.Scatter(name="R&D Share of Revenue [%]",
                       x=dates_research_and_development,
                       y=share_research_and_development,
                       text=formatted_y_values,
                       hovertemplate=hovertemplate_maingraph,
                       mode="markers",
                       marker=dict(
                           color="#FFD000",  # Fill color with some transparency (tomato color here)
                           size=10,  # Size of the markers
                           line=dict(
                               color="#C58400",  # Outline color (black in this example)
                               width=1  # Width of the outline
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

    logger.info("2. CALLBACK END")
    t2 = time.perf_counter(), time.process_time()
    logger.info(f" Creating graph")
    logger.info(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    logger.info(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
    return fig_main, fig_revenue, fig_second, fig_product_maturity, sections, graph_message


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
    logger.info(f" Performance of the valuation over time")
    logger.info(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    logger.info(f" CPU time: {t2[1] - t1[1]:.2f} seconds")

    return printed_arpu


# Callback Adapting the Hype-meter
@app.callback(
    Output(component_id="hype-meter-noa", component_property="value"),
    Output(component_id="hype-tooltip-noa", component_property="children"),
    Output(component_id="hype-meter-users", component_property="value"),
    Output(component_id="hype-tooltip-users", component_property="children"),
    Output(component_id="hype-meter-hype", component_property="value"),
    Output(component_id="hype-tooltip-hype", component_property="children"),
    Output(component_id="hype-tooltip-price", component_property="children"),
    Output(component_id="current-valuation-calculated", component_property="data"),
    Output(component_id="hype-meter-undervaluation-hype", component_property="value"),
    # Progress 1 colored value (hype)
    Output(component_id="hype-meter-undervaluation-hype", component_property="color"),  # Progress 1 color
    Output(component_id="hype-meter-undervaluation-rest", component_property="value"),  # Progress 1 white part
    Output(component_id="hype-meter-price", component_property="value"),
    Output(component_id="hype-meter-price-rest", component_property="value"),
    Output(component_id="hype-overvaluation-label", component_property="children"),
    Output(component_id="hype-meter-undervaluation-hype", component_property="label"),
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
        State(component_id='graph-unit', component_property='data'),
        State(component_id='hype-score', component_property='data')
    ], prevent_initial_call=True
)
def calculate_arpu(df_sorted, profit_margin, discount_rate, row_index, arpu_growth, current_market_cap,
                   latest_market_cap, current_arpu,
                   total_assets, df_dataset_dict, graph_unit, hype_score):
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
    future_customer_equity = src.analysis.net_present_value_arpu_growth(k_selected, r_selected, p0_selected,
                                                                        current_arpu,
                                                                        arpu_growth, profit_margin, discount_rate,
                                                                        YEARS_DCF)
    # Quick fix, in case the future_customer_equity throws inf. It should be refactored by only relying on the
    # historical valuation function, instead of recalculating it here
    if future_customer_equity == float('inf'):
        future_customer_equity = current_customer_equity * 3
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
        hype_color_indicator = "#fa5252"  # red
        # Progress 2
        intrinsic_value_ratio_rest = 100 - (
                non_operating_assets_ratio + customer_equity_ratio)  # white part of the intrinsic value bar
        # Progress 3
        price_rest_ratio = 0.0
        current_market_cap_ratio = 100  # the price bar is full if hype is positive
        text_overvaluation = "Overvaluation"
    # if hype is negative
    else:
        # Progress 1
        hype_ratio_progress = hype_ratio_absolute
        hype_ratio_rest = 100 - hype_ratio_absolute
        hype_color_indicator = "#40c057"  # green
        # Progress 2
        intrinsic_value_ratio_rest = 0.0
        # Progress 3
        current_market_cap_ratio = hype_ratio_rest
        price_rest_ratio = 100 - current_market_cap_ratio
        text_overvaluation = "Undervaluation"

    hype_tooltip = f"Hype: ${hype_total / 1e9:.2f} B.  It reflects the current overvaluation of the company in terms " \
                   f"of market capitalization versus actual value."
    if current_market_cap > 1e9:
        price_tooltip = f"Price: ${current_market_cap / 1e9:.2f} B, the current valuation (or price) on the stock market."
    else:
        price_tooltip = f"Price: ${current_market_cap / 1e6:.2f} M, the current valuation (or price) on the stock market."
    hype_indicator_color, hype_indicator_text = src.analysis.hype_meter_indicator_values(hype_ratio / 100)

    t2 = time.perf_counter(), time.process_time()
    logger.info(f" Performance of the valuation over time")
    logger.info(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    logger.info(f" CPU time: {t2[1] - t1[1]:.2f} seconds")

    return non_operating_assets_ratio, noa_tooltip, customer_equity_ratio, customer_equity_tooltip, intrinsic_value_ratio_rest, \
           hype_tooltip, price_tooltip, current_valuation, hype_ratio_progress, hype_indicator_color, hype_ratio_rest, \
           current_market_cap_ratio, price_rest_ratio, text_overvaluation, text_overvaluation


# Callback calculating the valuation over time and displaying the functionalities & graph cards, and hiding the text
@app.callback(
    Output(component_id='data-selection-counter', component_property='data', allow_duplicate=True),
    Output(component_id='valuation-over-time', component_property='data'),
    Output("loader-general", "style", allow_duplicate=True),
    Input(component_id='users-dates-formatted', component_property='data'),
    Input(component_id='total-assets', component_property='data'),
    Input(component_id='users-dates-raw', component_property='data'),
    Input(component_id='latest-market-cap', component_property='data'),  # Stores the current (now) company market cap
    State(component_id='max-net-margin', component_property='data'),
    [State('data-selection-counter', 'data')]
    , prevent_initial_call=True
)
def historical_valuation_calculation(df_formatted, total_assets, df_raw, latest_market_cap, max_net_margin,
                                     df_rawdataset_counter):
    logger.info("Dataset Flag")
    logger.info(max_net_margin)
    logger.info(type(max_net_margin))
    logger.info(df_rawdataset_counter)
    # The entire callback is skipped if the current market cap = 0, i.e. if it is not a public company OR
    # if it was already calculated
    if latest_market_cap == 0 or df_rawdataset_counter == False:
        raise PreventUpdate
    t1 = time.perf_counter(), time.process_time()
    dates_raw = np.array([entry['Date'] for entry in df_raw])
    dates_new = np.array([entry['Date'] for entry in df_formatted])
    revenue_df = np.array([entry['Revenue'] for entry in df_formatted])
    max_net_margin = max_net_margin / 100
    profit_margin_df = np.array([entry['Profit Margin'] for entry in df_formatted])
    profit_margin_original = profit_margin_df / 100
    market_cap_df = np.array([entry['Market Cap'] for entry in df_formatted])
    market_cap_original = market_cap_df * 1e9
    dates_original = dates_new - 1970
    # Users are taken from the database and multiplied by a million
    users_new = np.array([entry['Users'] for entry in df_formatted])
    users_original = users_new.astype(float) * 1_000_000
    MIN_REVENUE_INDEX = MIN_DATE_INDEX

    # Iteration range for valuation calculation
    iteration_range = [MIN_DATE_INDEX,
                       len(dates_original)]  # Range for calculating all the valuations starting from the 4th date

    # Valuation calculation
    non_operating_assets = total_assets
    # df_valuation_over_time = pd.DataFrame(columns=columns)
    valuation_data = []
    logger.info(f"{iteration_range = }")
    if df_rawdataset_counter:  # calculates the historic of valuation only if the dataset has been updated
        for i in range(iteration_range[0], iteration_range[1]):
            dates_valuation = dates_original[:i+1]
            users_valuation = users_original[:i+1]
            quarterly_revenue = revenue_df * 1_000_000  # Getting in database
            revenue_valuation = quarterly_revenue[:i+1]
            market_cap_valuation = market_cap_original[i]

            profit_margin_valuation = profit_margin_original[:i+1]

            # Smoothing the data
            # dates, users = main.moving_average_smoothing(dates_valuation, users_valuation, 1)
            dates = dates_valuation
            users = users_valuation

            # All parameters are calculated by ignoring data 1 by 1, taking the history reference as the end point
            df_full = src.ParametersDataFrame.parameters_dataframe(dates,
                                                                   users)  # Dataframe containing all parameters with all data ignored
            if df_full.empty:
                logger.info("nonono scenario calculated at all")
            df_sorted = src.ParametersDataFrame.parameters_dataframe_cleaning(df_full,
                                                                              users)  # Dataframe where inadequate scenarios are eliminated

            if df_sorted.empty:  # Smoothening data for cases where it doesn't work
                # Smoothing the data
                # dates1, users1 = main.moving_average_smoothing(dates_valuation, users_valuation, 4)
                dates = dates_valuation
                users = users_valuation

                # All parameters are calculated by ignoring data 1 by 1, taking the history reference as the end point
                df_full1 = src.ParametersDataFrame.parameters_dataframe(dates,
                                                                        users)  # Dataframe containing all parameters with all data ignored
                df_sorted = src.ParametersDataFrame.parameters_dataframe_cleaning(df_full1,
                                                                                  users)  # Dataframe where inadequate scenarios are eliminated
                if df_sorted.empty:
                    logger.info("Cleaning it minimally")
                    df_sorted = src.ParametersDataFrame.parameters_dataframe_cleaning_minimal(df_full, users)
                    logger.info(f"df_sorted_minimally {df_sorted}")
                    if df_sorted.empty:
                        df_sorted = df_full
                        logger.info(f"No scenario could be calculated, df used: {df_sorted}")
                    # continue
            else:
                logger.info("Successful scenarios exist")
            # Number of scenarios to store
            i -= MIN_DATE_INDEX

            # Profit margin assessment
            profit_margin = np.empty(2)
            profit_margin_previous_year = profit_margin_valuation[-4:]
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
            logger.info("averageprofit")
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
                    future_customer_equity = src.analysis.net_present_value_arpu_growth(k_selected, r_selected,
                                                                                        p0_selected,
                                                                                        current_arpu, arpu_growth[j],
                                                                                        profit_margin[j],
                                                                                        discount_rate[j],
                                                                                        YEARS_DCF)
                    current_customer_equity = users_valuation[-1] * current_arpu * profit_margin[j]
                    total_valuation = future_customer_equity + current_customer_equity + non_operating_assets
                    # Check if this is the second iteration (j=1) and ensure it's higher than first
                    if j == 1 and len(valuation_data) > 0:
                        # Get the valuation from the first iteration (index 7 in the list)
                        first_valuation = valuation_data[-1][7]
                        # Ensure second valuation is at least 1.2x the first
                        if total_valuation <= first_valuation:
                            total_valuation = first_valuation * 2
                    valuation_data.append([
                        dates_new[i + MIN_DATE_INDEX],
                        dates_raw[i + MIN_DATE_INDEX],
                        k_selected,
                        r_selected,
                        p0_selected,
                        profit_margin[j],
                        current_arpu,
                        total_valuation,
                        market_cap_valuation
                    ])
    # Convert the list to a DataFrame
    columns = ['Date', 'Date Raw', 'K', 'r', 'p0', 'Profit Margin', 'ARPU', 'Valuation', 'Market Cap']
    df_valuation_over_time = pd.DataFrame(valuation_data, columns=columns)

    # Clean up dataframe to avoid having infinite values (function to be deleted once K calculation is improved)
    # Create a copy to avoid modifying the original
    df_valuation_cleaned = main.replace_inf_with_previous_2(df_valuation_over_time, "Valuation")
    # df_valuation_cleaned_second_time = main.cleans_high_valuations(df_valuation_cleaned, "Valuation")
    df_valuation_over_time_dict = df_valuation_cleaned.to_dict(orient='records')  # Removing "inf" values

    logger.info("DF Valuation over time")
    logger.info(df_valuation_over_time)
    hide_loader = {'display': 'none'}
    display_loading_overlay = False

    logger.info("DF Valuation over time")
    logger.info(df_valuation_over_time)
    # logger.info(df_valuation_over_time2)
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
    Output(component_id='quadrant-company-message', component_property='children'),
    Output(component_id='quadrant-company-message', component_property='color'),
    Output(component_id='quadrant-company-message', component_property='title'),
    Output(component_id="valuation-message", component_property="title"),
    Output(component_id="valuation-content", component_property="children"),
    Output(component_id="valuation-message", component_property="color"),
    Output(component_id="accordion-valuation", component_property="icon"),
    Output(component_id="hype-score", component_property="data"),  # hype score storage
    Output(component_id="hype-score-text", component_property="children"),  # hype score text
    Output(component_id="growth-content", component_property="children"),  # hype score text
    Output(component_id="hype-meter-indicator", component_property="color"),
    Output(component_id="hype-meter-indicator", component_property="children"),

    Input(component_id='valuation-over-time', component_property='data'),
    Input(component_id='graph-unit', component_property='data'),  # Getting the Unit used
    State(component_id='date-picker', component_property='value'),  # Take date-picker date
    State(component_id='users-dates-formatted', component_property='data'),
    State(component_id='total-assets', component_property='data'),
    State(component_id='users-dates-raw', component_property='data'),
    State(component_id='latest-market-cap', component_property='data'),  # Stores the current (now) company market cap
    State(component_id='scenarios-sorted', component_property='data'),  # Stores the calculated growth scenarios
    State(component_id='current-arpu-stored', component_property='data'),  # Stores the current arpu
    State(component_id='dataset-selection', component_property='value'),  # Stores the name of the dataset selected
    Input(component_id="current-valuation-calculated", component_property="data"),
    State(component_id='max-net-margin', component_property='data'),  # Max net margin!
    State(component_id='valuation-category', component_property='data'),  # Take date-picker date
    prevent_initial_call=True,
)
def graph_valuation_over_time(valuation_over_time_dict, unit_metric, date_picked, df_formatted, total_assets, df_raw,
                              latest_market_cap, df_sorted, current_arpu, company_sign, current_valuation,
                              max_net_margin, valuation_category):
    if not latest_market_cap:  # if latest market cap doesn't exist, none of this callback is triggered
        raise PreventUpdate
    logger.info("Graph Valuation Start")
    t1 = time.perf_counter(), time.process_time()
    dates_raw = np.array([entry['Date'] for entry in df_raw])
    dates_new = np.array([entry['Date'] for entry in df_formatted])
    revenue_df = np.array([entry['Revenue'] for entry in df_formatted])
    profit_margin_df = np.array([entry['Profit Margin'] for entry in df_formatted])
    company_symbol = str(company_sign)

    # Valuation calculation
    non_operating_assets = total_assets
    df_valuation_over_time = pd.DataFrame(valuation_over_time_dict)
    logger.info("Df valuation")
    logger.info(latest_market_cap)
    logger.info(df_valuation_over_time)
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

    hype_score = (latest_market_cap * 1e6 - low_scenario_valuation[-1]) / \
                 (high_scenario_valuation[-1] - low_scenario_valuation[-1])
    logger.info("hype score calculation")
    logger.info(hype_score)
    logger.info(latest_market_cap)
    logger.info(low_scenario_valuation[-1])
    logger.info(high_scenario_valuation[-1])
    badge_color, badge_label = main.hype_meter_indicator_values_new(hype_score)
    # badge_color_growth, badge_label_growth = main.growth_meter_indicator_values(growth_score)
    hype_score_text = dmc.Group([
        dmc.Text(f"Hype score: {hype_score:.2f}", size="sm"),
        dmc.Badge(badge_label, size="xs", variant="outline", color=badge_color)
    ], gap="md")

    # Append today's date and latest market cap
    today_date = date.today()
    market_cap_array = np.append(market_cap_array, latest_market_cap * 1e6)
    dates_raw_market_cap = np.append(dates_raw, today_date)
    low_scenario_valuation = np.append(low_scenario_valuation, low_scenario_valuation[-1])
    high_scenario_valuation = np.append(high_scenario_valuation, high_scenario_valuation[-1])

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
                                       # fillcolor='#C92A2A',
                                       fillpattern={  # 'shape': '/',
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
    y_area_low = low_scenario_valuation  # Low growth array
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
                                       text=formatted_y_values, hovertemplate=hovertemplate_maingraph,
                                       showlegend=False))
    # Market Cap
    formatted_y_values = [f"${y / 1e6:.1f} M" if y < 1e9 else f"${y / 1e9:.2f} B" for y in market_cap_array]
    fig_valuation.add_trace(go.Scatter(name="Market Cap", x=dates_raw_market_cap[MIN_DATE_INDEX:], y=market_cap_array,
                                       mode="lines", line=dict(color="#953AF6", width=2), text=formatted_y_values,
                                       hovertemplate=hovertemplate_maingraph))

    # Current valuation
    # logger.info(f"Datata {date_picked = }; {type(date_picked) = }")
    # date_obj = datetime.strptime(date_picked, '%Y-%m-%d')
    if current_valuation > high_scenario_valuation[-1]:
        color_dot = "#300541"
    else:
        color_dot = "#FBC53C"

    formatted_y_values = [f"${current_valuation / 1e6:.1f} M" if current_valuation < 1e9
                          else f"${current_valuation / 1e9:.2f} B"]

    fig_valuation.add_scatter(name="Chosen scenario", x=[date_picked], y=[current_valuation],
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
            # minallowed=0,
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
                x=dates_until_today[mid_id_valuation - 1],
                y=low_scenario_valuation[mid_id_valuation - 1],
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
                x=dates_until_today[mid_id_valuation + 1],
                y=high_scenario_valuation[mid_id_valuation + 1],
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
    try:
        profit_margin_needed = src.analysis.profit_margin_for_valuation(k_high_valuation, r_high_valuation,
                                                                        p0_high_valuation,
                                                                        current_arpu, 0.05, 0.1, YEARS_DCF,
                                                                        non_operating_assets,
                                                                        latest_market_cap * 1000000)
    # Except to avoid errors
    except Exception as e:
        profit_margin_needed = max_net_margin * 0.2
    # max_profit_margin = np.max(profit_margin_df) old method, using the max known PM
    max_profit_margin = max_net_margin  # new method, using the max theoretical net profit margin.

    # Valuation message
    if market_cap_array[-1] < high_scenario_valuation[-1]:
        # Messages in the accordion
        valuation_accordion_title = company_symbol + " may be undervalued"
        valuation_accordion_message = company_symbol + "’s current price is below our top estimate. " \
                                                       "If you see long-term potential, it might be a good buy."
        # Messages right above the graph
        valuation_graph_title = "How well did our model perform over time?"
        valuation_graph_message = dmc.Text(
            children=[
                dmc.Text("The purple line", span=True, c="#953BF6", fw=600),
                " shows ",
                company_symbol,
                "'s ",
                dmc.Text("price", span=True, c="black", fw=600),
                " (market cap) over time. ",
                dmc.Text("The yellow zone", span=True, c="#C48501", fw=600),
                " is our ",
                dmc.Text("confidence range. ", span=True, c="black", fw=600),
                "We believe the market cap tends to fall, sooner or later, within this range. " \
                " The market cap is currently ",
                dmc.Text("lower than the most optimistic valuation ", span=True, c="black", fw=600),
                f"({high_scenario_valuation[-1] / 1e9:.2f} B$) ",
                "meaning that this stock may be ",
                dmc.Text("fairly or even undervalued!", span=True, c="#034205", fw=600),
                dmc.Text("Note: Move the dot by changing scenarios or parameters in the nerd mode", c="black",
                         fs="italic"),
            ],
            size="sm",
        )
        valuation_graph_color = "green"
        valuation_icon_color = DashIconify(icon="radix-icons:rocket", color=dmc.DEFAULT_THEME["colors"]["green"][6],
                                           width=20)
    else:
        # Messages in the accordion!
        valuation_accordion_title = company_symbol + " is overvalued"
        valuation_accordion_message = dmc.Text(
            children=[
                company_symbol,
                "'s current price is ",
                dmc.Text(" above our highest estimate. ", span=True, c="black", fw=600),
                "To justify it, they'd need a ",
                f"{profit_margin_needed * 100:.1f}% ",
                "profit margin, even though they could theoretically aim at best at ",
                f"~{max_profit_margin:.0f}%... ",
                f"So yeah, a bit of a stretch."
            ]
        )

        # Messages right above the graph
        valuation_graph_title = "How well did our model perform over time?"
        valuation_graph_message = dmc.Text(
            children=[
                dmc.Text("The purple line", span=True, c="#953BF6", fw=600),
                " shows ",
                company_symbol,
                "'s ",
                dmc.Text("price", span=True, c="black", fw=600),
                " (market cap) over time. ",
                dmc.Text("The yellow zone", span=True, c="#C48501", fw=600),
                " is our ",
                dmc.Text("confidence range. ", span=True, c="black", fw=600),
                "We believe the market cap tends to fall, sooner or later, within this range. " \
                " The market cap is currently ",
                dmc.Text("higher than the most optimistic valuation", span=True, c="black", fw=600),
                f"({high_scenario_valuation[-1] / 1e9:.2f} B$) ",
                "meaning that this stock seems ",
                dmc.Text("overvalued!", span=True, c="#FA4140", fw=600),
                dmc.Text("Note: Move the dot by changing scenarios or parameters in the nerd mode", c="black",
                         fs="italic"),
            ],
            size="sm",
        )
        valuation_graph_color = "yellow"
        valuation_icon_color = DashIconify(icon="radix-icons:rocket", color=dmc.DEFAULT_THEME["colors"]["yellow"][6],
                                           width=20)

    if valuation_category == "lowGrowth_lowHype":
        quadrant_title = "Low Growth, Low Hype"
        quadrant_message = dmc.Text(
            children=[company_symbol,
                      " belongs to the",
                      dmc.Text(" 'Steady, Forgotten' ", span=True, c="black", fw=600),
                      " category, which means that it is not overvalued, nor is it showing crazy growth. "
                      " It can be considered a safe (boring?) investment: no major upside nor downside in the mid-term should be expected."
                      ],
            size="sm",
        )
        quadrant_color = "yellow"
        growth_description = dmc.Text(
            children=[
                "But there is probably ",
                dmc.Text(" no big upside ", span=True, c="black", fw=600),
                " to expect in the future given the low growth of ",
                unit_metric,
                "."
            ]
        )
    elif valuation_category == "highGrowth_lowHype":
        quadrant_title = "Strong Growth, Low Hype"
        quadrant_message = dmc.Text(
            children=[company_symbol,
                      " belongs to the VIP ",
                      dmc.Text(" 'Undervalued gems' ", span=True, c="#C58400", fw=600),
                      " club, which means that it is not overvalued, AND it is showing very solid growth. "
                      " If no other red flags exist (such as high debt, or recent public scandal related to ",
                      company_symbol,
                      "), then the",
                      dmc.Text(" price could very likely rise in the mid-term.", span=True, c="#black", fw=600),
                      ],
            size="sm",
        )
        quadrant_color = "green"
        growth_description = dmc.Text(
            children=[
                "Combined with the strong growth of ",
                dmc.Text(unit_metric, fs="italic", span=True),
                dmc.Text(" a big upside ", span=True, c="black", fw=600),
                " could be expected in the future.",
            ]
        )
    elif valuation_category == "lowGrowth_highHype":
        quadrant_title = "Low Growth, Strong Hype"
        quadrant_message = dmc.Text(
            children=[company_symbol,
                      " belongs to the unwanted ",
                      dmc.Text(" 'Bubble zone'", span=True, c="#480404", fw=600),
                      ". Why? Well because it's showing high hype with limited growth in terms of ",
                      dmc.Text(unit_metric, fs="italic", span=True),
                      ". The longer ",
                      company_symbol,
                      " takes to generate more money per ", unit_metric,
                      ", the greater the risk of a sharp drop in its stock price."
                      ],
            size="sm",
            # fw=300,
        )
        quadrant_color = "#FB4040"
        growth_description = dmc.Text(
            children=[
                "Given the limited growth of ",
                dmc.Text(unit_metric, fs="italic", span=True),
                ",",
                dmc.Text(" a maaaassive change ", span=True, c="black", fw=600),
                " should happen in the near future to justify the current value.",
            ]
        )
    else:
        quadrant_title = "High Growth, High Hype"
        quadrant_message = dmc.Text(
            children=[company_symbol,
                      " belongs to the ",
                      dmc.Text(" 'Hot & hyped' ", span=True, c="#480404", fw=600),
                      " zone. Its hype is strong, but so is its growth in terms of ",
                      dmc.Text(unit_metric, fs="italic", span=True),
                      ". Which such a growth, the hype can live a while longer. But the price is likely to drop at the first sign of weakness."
                      ],
            size="sm",
            # fw=300,
        )
        quadrant_color = "yellow"
        growth_description = dmc.Text(
            children=[
                "BUT, the growth of ",
                dmc.Text(unit_metric, fs="italic", span=True),
                dmc.Text(" is so ridiculously strong", span=True, c="black", fw=600),
                " that the hype may last for a while!",
            ]
        )

    print("Valuation graph printed")
    t2 = time.perf_counter(), time.process_time()
    print(f" Performance of the valuation graph over time")
    print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
    return fig_valuation, valuation_graph_message, valuation_graph_color, valuation_graph_title, quadrant_message, quadrant_color, quadrant_title, valuation_accordion_title, \
           valuation_accordion_message, valuation_graph_color, valuation_icon_color, hype_score, hype_score_text, growth_description, badge_color, badge_label



# Callback to update table based on selection
@app.callback(
    Output("top_25_companies", "children"),
    Input('all-companies-information', 'data'),  # Table of companies
    Input('hyped-table-select', 'value'),  # more or least hyped
    Input('hyped-table-industry', 'value'),  # industry
    Input("login-state", "data"),
    State('pro-user-state', 'data'),  # stores pro account state (boolean))
)
def update_table(df_all_companies, hype_choice, industries, logged_in, pro_user):
    t1 = time.perf_counter(), time.process_time()
    if df_all_companies is None:
        raise PreventUpdate

    # Blocks the process for dev
    IS_PRODUCTION = os.getenv("IS_PRODUCTION") == "true"  # Setup in heroku 'heroku config:set IS_PRODUCTION=true'
    if IS_PRODUCTION is False:
        return no_update  # nothing to do

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
    if pro_user:
        sorted_data = sorted(filtered_data, key=lambda x: x["Hype Score"] if x["Hype Score"] is not None else 0,
                             reverse=reverse)
    else:
        sorted_data = filtered_data

    df_sorted = pd.DataFrame(sorted_data)
    # Logic of changing it depending on what is chosen
    # if hype_choice == 'most-hyped':
    #    df_sorted = dataAPI.get_hyped_companies(True)
    # else:
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
                # transition="slide-down",
                # transitionDuration=300,
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
                # transition="slide-down",
                # transitionDuration=300,
                multiline=True,
            )
        ]), style={"width": "32.5%"}
        )
    ])
    )]
    rows = []

    for i in range(len(df_sorted)):
        industry_type = df_sorted.iloc[i]['Industry'],
        industry_type_icon = main.get_industry_icon(
            df_sorted.iloc[i]['Industry'])  # function mapping the industry to an icon
        if pro_user:
            company_name = df_sorted.iloc[i]['Company Name']
        else:
            company_name = "Nope, still not pro amigo"
        hype_score = df_sorted.iloc[i]['Hype Score']
        growth_score = df_sorted.iloc[i]['Growth Score']

        # Determine badge color and label -> To-do: apply the function in .main to this -> done, replace it by main.hype_meter_indicator_values
        # badge_color, badge_label = main.hype_meter_indicator_values(hype_score)

        badge_color, badge_label = main.hype_meter_indicator_values_new(hype_score)

        # Determine growth badge color and label -> To-do: apply the function in .main to this
        badge_color_growth, badge_label_growth = main.growth_meter_indicator_values(growth_score)

        row = html.Tr([
            html.Td(
                dmc.Tooltip(
                    DashIconify(icon=industry_type_icon, width=15),
                    label=industry_type,
                ),
                # ta="center",
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
                ], gap="md"),
                style={"width": "30%"}
            ),
            html.Td(
                dmc.Group([
                    f"{growth_score:.2f}",
                    dmc.Badge(badge_label_growth, size="xs", variant="outline", color=badge_color_growth)
                ], gap="md"),
                style={"width": "40%"}
            ),
        ])
        rows.append(row)
    body = [html.Tbody(rows)]
    # logger.info("Hyped table is")
    # logger.info(df_sorted)
    t2 = time.perf_counter(), time.process_time()
    logger.info(f" Performance of the table update")
    logger.info(f" Real time: {t2[0] - t1[0]:.2f} seconds")
    logger.info(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
    return header + body


if __name__ == '__main__':
    app.run(debug=True)
