from dash import register_page, html

register_page(
    __name__,
    name='Valuation made simple - RAST',
    top_nav=True,
    path='/dashboard'
)


def layout(company=None, **other_unknown_query_strings):
    return html.Div()
