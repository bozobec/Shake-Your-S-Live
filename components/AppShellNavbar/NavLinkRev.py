from dash_iconify import DashIconify
import dash_mantine_components as dmc


def create():
    return dmc.NavLink(
                    label="Revenue",
                    description="",
                    leftSection=DashIconify(icon="fa6-solid:money-check-dollar", height=16),
                    href="#section-5",
                    id="link-section-5",
                    style={"padding": "8px 12px", "borderRadius": "4px"},
                )
