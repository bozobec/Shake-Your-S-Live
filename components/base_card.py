import dash_mantine_components as dmc

def base_card(title: str, children=None):
    """
    A reusable Mantine Card template for RAST app sections.
    """
    return dmc.Card(
        children=[
            dmc.Group(
                [
                    dmc.Title(title, order=6),
                ],
                position="apart",
                mt="md",
            ),
            dmc.Space(h=20),
            *(children or []),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
    )