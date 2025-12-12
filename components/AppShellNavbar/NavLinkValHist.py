from dash_iconify import DashIconify
import dash_mantine_components as dmc


def create():
    return dmc.NavLink(
                    label="Valuation history",
                    description="",
                    leftSection=DashIconify(icon="tabler:pig-money", height=16),
                    href="#section-3",
                    id="link-section-3",
                    style={"padding": "8px 12px", "borderRadius": "4px"},
                )
