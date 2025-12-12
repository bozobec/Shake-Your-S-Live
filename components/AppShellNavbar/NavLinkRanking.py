from dash_iconify import DashIconify
import dash_mantine_components as dmc


def create():
    return dmc.NavLink(
                    label="Ranking",
                    description="Logged in only",
                    leftSection=DashIconify(icon="solar:ranking-line-duotone", height=16),
                    href="/ranking",
                    id="link-section-8",
                    style={"padding": "8px 12px", "borderRadius": "4px"},
                )
