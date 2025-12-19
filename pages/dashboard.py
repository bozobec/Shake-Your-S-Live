# -*- coding: utf-8 -*-
import dash_mantine_components as dmc
from dash import register_page

from components.HomePage import HomeSelectCompanyCard as HomeSelectCompanyCard, ExploreRankingCard as ExploreRankingCard
from components.HomePage.DisplayedCompanies import DISPLAYED_COMPANIES

register_page(
    __name__,
    name='Valuation made simple - RAST',
    top_nav=True,
    path='/'
)


def layout(company=None, **other_unknown_query_strings):
    return dmc.Container(
        children=[
            dmc.SimpleGrid(
                cols={"base": 1, "lg": 2},
                spacing="xl",
                children=[
                    HomeSelectCompanyCard.create(companies=DISPLAYED_COMPANIES),
                    ExploreRankingCard.create()],
                style={'padding': '50px 0'}
            )
        ],
        id='card-welcome',
        size="xl",
        style={}
    )
