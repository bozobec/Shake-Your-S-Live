from dash import Dash, html, dcc, callback, dash_table
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_ag_grid as dag


# Graph message growth rate
ranking_graph_message = dmc.Alert(
    dmc.Text("About the Discrete Growth Rate"),
    id="growth-rate-graph-message",
    title="When will the growth stop?",
    color="blue",
    #hide="False",
    withCloseButton="True")

dash_ag_table = dag.AgGrid(
    id='top_25_companies_new',
    columnDefs=[
        {
            "field": "Industry",
            "headerName": "Industry", # Icon column usually looks better without a header
            "flex": 1, # Takes up 2 parts of remaining space
            "resizable": True, # Prevent moving the icon column
            "cellRenderer": "IndustryIconRenderer",
            #"cellStyle": {"display": "flex", "justifyContent": "center"}
        },
        {
            "field": "Company Name",
            "headerName": "Company",
            "flex": 1, # Takes up 2 parts of remaining space
            "cellRenderer": "CompanyLinkRenderer",
            "cellStyle": {"fontWeight": "bold"}
        },
        {
            "field": "Hype Score",
            "headerName": "Hype Score",
            "flex": 1, # Takes up 1 part
            "cellRenderer": "ScoreBadgeRenderer",
        },
        {
            "field": "Growth Score",
            "headerName": "Growth Score",
            "flex": 1, # Takes up 1 part
            "resizable": False,
            "cellRenderer": "ScoreBadgeRenderer",
            # This ensures the user can't manually shrink it to leave a gap
            "minWidth": 150,
        },
    ],
    # This is the "magic" setting that removes the blank space
    dashGridOptions={
        #"domLayout": "autoHeight", # Adjusts height to content
        "suppressHorizontalScroll": True, # Prevents the side-scroll gap
        "animateRows": True,
        "alwaysShowVerticalScroll": True, # Visual cue that it's scrollable
    },
    # Ensure the grid fills the container width
    style={"height": 600, "width": "100%"},
    #className="ag-theme-alpine", # Or "ag-theme-balham" for a denser look
)

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
                            #target="_blank",
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
                        "EydmViYXlxMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/MW36NXIPuLhgyXhbQt/giphy.gif",  # Ronaldo
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
                    # Targeting the placeholder via the input style
                    styles={
                        "input": {
                            "color": "#000000",
                            "fontWeight": "400",

                            "&::placeholder": {
                                "color": "#000000",
                                "opacity": "0.9",
                                "fontWeight": "500",
                            },
                        },
                        "dropdown": {
                            "fontWeight": "400",
                        },
                        "option": {
                            "color": "#000000",
                            "&:hover": {
                                "backgroundColor": "#373A40",
                            },
                            "&[data-selected]": {
                                "backgroundColor": "#5c7cfa",
                                "color": "white",
                            },
                            "fontWeight": "400",
                        },
                    },
                    clearable=True,
                    #limit=3,
                    mb=10,
                    leftSection=DashIconify(icon="mdi-light:factory"),
                ),
        ],
        justify="space-between",
        mt="md",
        mb="xs",
        wrap="nowrap",
        gap="xl",
    ),
    dmc.Text(
        "The exhaustive list of companies that we analyze and their ranking. The table is updated on a weekly basis: "
        "click on the company to get the current hype/growth score",
        size="xs",
        c="dimmed",
    ),
    dmc.Space(h=20),
    #dmc.ScrollArea(
    #    h=400,
    #    children=[
    #        dmc.Table(id='top_25_companies'),
    #    ]
    #),
    dash_ag_table,
    login_overlay_table,
], withBorder=True, shadow='lg', radius='md', id='section-8')