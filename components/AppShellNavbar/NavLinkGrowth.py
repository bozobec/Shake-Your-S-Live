from dash_iconify import DashIconify
import dash_mantine_components as dmc


def create():
    return dmc.NavLink(
                    label="Growth",
                    description="",
                    leftSection=DashIconify(icon="streamline-sharp:decent-work-and-economic-growth",
                                            height=16),
                    href="#section-4",
                    id="link-section-4",
                    style={"padding": "8px 12px", "borderRadius": "4px"},
                )
