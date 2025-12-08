from dash import Dash, html, dcc, callback, dash_table
import dash_mantine_components as dmc
from dash_iconify import DashIconify


# Graph message growth rate
ranking_graph_message = dmc.Alert(
    dmc.Text("About the Discrete Growth Rate"),
    id="growth-rate-graph-message",
    title="When will the growth stop?",
    color="blue",
    #hide="False",
    withCloseButton="True")

login_overlay_table = dmc.Group(
    id="login-overlay-table",
    children=[
        dmc.Stack(
            [
                dmc.Text(
                    children=[
                        "Sorry amigo, you'll need to become a ",
                        dmc.Anchor(
                            dmc.Text(
                                "pro",
                                fw=900,
                                span=True,
                            ),
                            target="_blank",
                            underline = "not-hover",
                            href="/pricing",
                            c="#FFA8FA",
                        ),
                        " member to view our most undervalued companies.",
                    ],
                    fw=700,
                    size="xl",
                    c="white",
                    ta="center",
                    span=False,
                ),
                html.Img(
                    src="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExeHc3YWJsNWx3ZXNxNDdwdDZiYnQyMWR1bjJpbTIxY3"
                        "EydmViYXlxMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/MW36NXIPuLhgyXhbQt/giphy.gif",
                    style={
                        "width": "200px",
                        "height": "200px",
                        "margin": "0 auto",
                        "display": "block"
                    }
                ),
            ],
            gap="xl",
            align="center",
            justify="center",
            style={"height": "100%"}
        )
    ],
    style={
        "display": "none",
        "position": "absolute",
        "top": 0,
        "left": 0,
        "width": "100%",
        "height": "100%",
        "backgroundColor": "rgba(0, 0, 0, 0.7)",
        "zIndex": 5,
        "backdropFilter": "blur(100px)",
    },
    align="center",
    justify="center"
)

table_hype_card = dmc.Card(children=[
    dmc.Group([
            dmc.Title("RAST Ranking", order=5),
            dmc.MultiSelect(
                    #label="Select the companies that you want to see",
                    placeholder="Filter by industry",
                    id="hyped-table-industry",
                    #description="You can select up to 3 industries.",
                    #value="All",
                    data=[
                        {"value": "most-hyped", "label": "Most hyped"},
                        {"value": "least-hyped", "label": "Least hyped"},
                    ],
                    clearable=True,
                    limit=3,
                    mb=10,
                    leftSection=DashIconify(icon="mdi-light:factory"),
                ),
        dmc.Select(
                    #label="Select the companies that you want to see",
                    placeholder="Most or least hyped companies",
                    id="hyped-table-select",
                    value="least-hyped",
                    data=[
                        {"value": "most-hyped", "label": "Most hyped"},
                        {"value": "least-hyped", "label": "Least hyped"},
                    ],
                    w=200,
                    mb=10,
                    allowDeselect=False,
                ),
        ],
        justify="space-around",
        mt="md",
        mb="xs",
        wrap="nowrap",
        gap="xl",
    ),
    dmc.Text(
        "The exhaustive list of companies that we analyze and their ranking. Click on the company to get the most "
        "updated hype/growth score",
        size="xs",
        c="dimmed",
    ),
    dmc.ScrollArea(
        h=400,
        children=[
            dmc.Table(id='top_25_companies')
        ]
    ),
    login_overlay_table,
], withBorder=True, shadow='lg', radius='md', id='section-8')