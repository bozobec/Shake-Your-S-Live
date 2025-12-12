from dash_iconify import DashIconify
import dash_mantine_components as dmc


def create():
    return dmc.NavLink(
                    label="Product Maturity",
                    description="",
                    leftSection=DashIconify(icon="healthicons:old-man-outline", height=16),
                    href="#section-6",
                    id="link-section-6",
                    style={"padding": "8px 12px", "borderRadius": "4px"},
                )
