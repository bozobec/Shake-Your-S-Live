from dash_iconify import DashIconify
import dash_mantine_components as dmc


def create():
    return dmc.NavLink(
                    label="Quadrant",
                    description="",
                    leftSection=DashIconify(icon="carbon:quadrant-plot", height=16),
                    href="#section-2",
                    id="link-section-2",
                    style={"padding": "8px 12px", "borderRadius": "4px"},
                )
