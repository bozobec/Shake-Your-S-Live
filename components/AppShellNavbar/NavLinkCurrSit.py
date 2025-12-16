from dash_iconify import DashIconify
import dash_mantine_components as dmc


def create():
    return dmc.NavLink(
        label=" Current situation",
        description="",
        leftSection=DashIconify(icon="mdi:bullseye", height=16),
        href="#section-1",
        id="link-section-1",
        style={"padding": "8px 12px", "borderRadius": "4px"},
    )
