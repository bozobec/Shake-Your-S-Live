# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
from dash import html
from dash import register_page


register_page(
    __name__,
    name='The most undervalued companies | RAST',
    top_nav=True,
    path='/ranking'
)


def layout(company=None, **other_unknown_query_strings):
    return html.Div()  # Empty - cards are in app.py
