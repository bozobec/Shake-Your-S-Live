from dash_iconify import DashIconify
import dash_mantine_components as dmc


def create():
    return dmc.NavLink(
                    label="Growth rate",
                    description="",
                    leftSection=DashIconify(icon="material-symbols-light:biotech-outline-rounded",
                                            height=16),
                    href="#section-7",
                    id="link-section-7",
                    style={"padding": "8px 12px", "borderRadius": "4px"},
                )
