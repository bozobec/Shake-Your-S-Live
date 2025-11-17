from dash import dcc, html
import dash_bootstrap_components as dbc

stored_data = dbc.Container(
    children=
    [
        # Storing the key dataframe with all parameters
        dcc.Store(id='users-data'),
        dcc.Store(id='users-dates-raw'),  # DF containing the initial users/dates from the API
        dcc.Store(id='users-dates-formatted'),  # DF containing the users & dates in float for computation
        dcc.Store(id='valuation-over-time'),  # DF containing the valuation over time for a given dataset
        dcc.Store(id='scenarios-sorted'),  # DF containing all the possible growth scenarios
        dcc.Store(id='current-market-cap'),
        # Market cap of the company selected, 0 if N/A at the relative current time (depending on the date picked)
        dcc.Store(id='latest-market-cap'),  # Market cap of the company at the absolute current time (now)
        dcc.Store(id='graph-unit'),  # Graph unit (MAU, Population, etc.)
        dcc.Store(id='symbol-dataset'),  # Symbol of the Public company (N/A if not)
        # Counter that shows 0 if no dataset has been selected, or 1 otherwise
        dcc.Store(id='revenue-dates'),  # DF Containing the quarterly revenue and the dates
        dcc.Store(id='current-arpu-stored'),  # DF Containing the current ARPU
        dcc.Store(id='total-assets'),  # DF Containing the current total assets of the company
        dcc.Store(id='users-revenue-correlation'),  # R^2 indicating the strength of the correlation between the KPI
        # used and the revenue
        # dcc.Store(id='data-source'),  # sources of the data
        dcc.Store(id='data-selection-counter', data={'flag': False}),
        #dcc.Store(id='dataset-selected-url', data=str(company)), # stores the dataset given through the url through ?company={company}
        dcc.Store(id='dataset-selected'),  # stores the dataset selected either through the dropdown or the URL
        # Counter that shows if a new dataset has been selected
        dcc.Store(id='initial-sliders-values'),
        dcc.Store(id='current-valuation-calculated'),
        # Current valuation calculated with the current parameters and date
        # Counter that shows if a new dataset has been selected
        dcc.Store(id='last-imported-data'),
        dcc.Store(id='all-companies-information'),  # stores all the companies and the related information
        dcc.Store(id='max-net-margin'),  # stores the max theoretical net margin for the selected company
        dcc.Store(id='hype-score'),  # calculates the company's hype level that is used in the ranking
        html.Div(id='page-load-trigger'),  # Dummy trigger to launch a callback once the page loads
        dcc.Store(id="user-store"),  # storing user information
        dcc.Store(id="user-token", storage_type="session"),
        dcc.Location(id='url-input', refresh=False),
        dcc.Location(id='url-output', refresh=False),
        # Hidden stores
        dcc.Store(id="url-state"),  # intermediary to avoid circular dependency
        dcc.Store(id="login-state", storage_type="session"),
        dcc.Store(id="user-id", storage_type="session"),
        html.Div(id="login-state-bridge", children="", style={"display": "none"}),
        dcc.Download(id="download-chart"),  # Component to handle file download
        dcc.Store(id='dataset-selected-url', data=None),
        dcc.Store(id='launch-counter', data={'flag': False}),
        dcc.Location(id='url', refresh=False)
            ],
    fluid=True)

