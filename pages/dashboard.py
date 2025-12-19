# -*- coding: utf-8 -*-

from dash import html
from dash import register_page

register_page(
    __name__,
    name='Valuation made simple - RAST',
    top_nav=True,
    path='/'
)


def layout(company=None, **other_unknown_query_strings):
    return html.Div()  # Empty - cards are in app.py
