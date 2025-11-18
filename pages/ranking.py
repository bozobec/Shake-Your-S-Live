from dash import html, register_page  #, callback # If you need callbacks, import it here.
# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import dash
import dash_mantine_components as dmc
from dash import Dash, html, dcc, callback, dash_table
from dash import callback
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dataAPI
import main
import dash_bootstrap_components as dbc
#import datetime
from datetime import datetime, timedelta, date
import math
from plotly.subplots import make_subplots
from dash_iconify import DashIconify
import time
from dash.exceptions import PreventUpdate
import random
import dash_daq as daq
#from dash_extensions import DeferScript
from functools import lru_cache
from components.analysis_card import analysis_card
import os
from components.ranking_card import table_hype_card
from components.quadrant_card import quadrant_card

register_page(
    __name__,
    name='The most undervalued companies | RAST',
    top_nav=True,
    path='/ranking'
)

def layout(company=None, **other_unknown_query_strings):
    return html.Div()  # Empty - cards are in app.py