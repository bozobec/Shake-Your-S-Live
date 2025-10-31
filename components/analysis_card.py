import dash_mantine_components as dmc
from dash_iconify import DashIconify

# Scenarios in the accordion
# -------
# Growth
growth_message = dmc.Alert(
    children=dmc.Text(""),
    id="growth-message",
    title="",
    color="gray"),

# Plateau
plateau_message = dmc.Alert(
    children=dmc.Text(""),
    id="plateau-message",
    title="",
    color="gray"),

# Valuation
valuation_message = dmc.Alert(
    children=dmc.Text(""),
    id="valuation-message",
    title="",
    color="gray"),

# Correlation
correlation_message = dmc.Alert(
    children=dmc.Text(""),
    id="correlation-message",
    title="",
    color="gray"),

# Product Maturity
product_maturity_message = dmc.Alert(
    children=dmc.Text(""),
    id="product-maturity-message",
    title="",
    color="gray"),

# Accordion
accordion = dmc.Accordion(
    id="accordion-main",
    multiple=True,
    radius="xl",
    children=[
        dmc.AccordionItem(
            [
                dmc.AccordionControl(
                    "Valuation",
                    id="accordion-valuation",
                    disabled=True,
                    icon=DashIconify(icon="radix-icons:rocket", width=20)
                                     ),
                dmc.AccordionPanel(
                    valuation_message
                ),
            ],
            value="valuation",
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl(
                    "Growth",
                    id="accordion-plateau",
                    disabled=True,
                    icon=DashIconify(icon="simple-icons:futurelearn", width=20)
                                     ),
                dmc.AccordionPanel(
                    plateau_message
                ),
            ],
            value="plateau",
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl(
                    "Revenue",
                    id="accordion-correlation",
                    disabled=True,
                    icon=DashIconify(icon="lineicons:target-revenue", width=20)
                ),
                dmc.AccordionPanel(
                    correlation_message
                ),
            ],
            value="correlation",
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl(
                    "Product Maturity",
                    id="accordion-product-maturity",
                    disabled=True,
                    icon=DashIconify(icon="fluent-mdl2:product-release", width=20)
                ),
                dmc.AccordionPanel(
                    product_maturity_message
                ),
            ],
            value="product-maturity",
        ),
    ],
)

analysis_card = dmc.Card(
    children=[
        dmc.LoadingOverlay(
                    visible=False,
                    id="loading-overlay2",
                    overlayProps={"radius": "sm", "blur": 2},
                    zIndex=10,
                ),
        dmc.Group(
                            [
                                dmc.Title("Analysis", order=5),
                            ],
                            #justify="space-around",
                            mt="md",
                            mb="xs",
                ),
        accordion,
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
    # style={"width": 350},
)