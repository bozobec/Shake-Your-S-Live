import dash_mantine_components as dmc

import components.AppShellNavbar.NavLinkCurrSit as NavLinkCurrSit
import components.AppShellNavbar.NavLinkQuadrant as NavLinkQuadrant
import components.AppShellNavbar.NavLinkValHist as NavLinkValHist
import components.AppShellNavbar.NavLinkGrowth as NavLinkGrowth
import components.AppShellNavbar.NavLinkRev as NavLinkRev
import components.AppShellNavbar.NavLinkProdMat as NavLinkProdMat
import components.AppShellNavbar.NavLinkGrowthRate as NavLinkGrowthRate
import components.AppShellNavbar.NavLinkRanking as NavLinkRanking


def create():
    """
    This function creates the Navbar on the very left of the page.
    It has several NavLinks as children.
    :return:
    """
    return dmc.AppShellNavbar(
        id="navbar",
        p="md",
        style={'display': 'none'},
        children=dmc.Stack(
            [NavLinkCurrSit.create(),
             NavLinkQuadrant.create(),
             NavLinkValHist.create(),
             NavLinkGrowth.create(),
             NavLinkRev.create(),
             NavLinkProdMat.create(),
             NavLinkGrowthRate.create(),
             NavLinkRanking.create(),
            ],
            gap="sm",
        ),
    )
