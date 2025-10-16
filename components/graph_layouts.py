import plotly.graph_objects as go

# Build main graph
layout_main_graph = go.Layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    dragmode="pan",
    clickmode="event+select",
    margin=go.layout.Margin(
        l=5,  # left margin
        r=5,  # right margin
        b=5,  # bottom margin
        t=20,  # top margin
    ),
    legend=dict(
        # Adjust click behavior
        itemclick="toggleothers",
        itemdoubleclick="toggle",
        yanchor="top",
        y=1.02,
        xanchor="left",
        x=0.01,
        font=dict(
            family="Basel, Arial, sans-serif",
            size=10,
        ),
    ),
    xaxis=dict(
        linecolor="#46052A",
        #fixedrange=False,  # allow zooming on x-axis
        constrain='domain',
        fixedrange=True,
    ),
    yaxis=dict(
        title="Users",
        linecolor="#46052A",
        gridwidth=1,
        gridcolor='rgba(255, 168, 251, 0.3)',
        rangemode="nonnegative",  # prevent negative y values ###
        fixedrange=True,          # does not allow zooming on y-axis ###
        range=[0, None],
    ),
    showlegend=True,
    font=dict(
        family="Basel, Arial, sans-serif",
    ),
)

# Layout of the revenue graph
layout_revenue_graph = go.Layout(
    # title="User Evolution",
    plot_bgcolor="White",
    dragmode=False,
    margin=go.layout.Margin(
        l=0,  # left margin
        r=0,  # right margin
        b=0,  # bottom margin
        t=20,  # top margin
    ),
    legend=dict(
        # Adjust click behavior
        itemclick="toggleothers",
        itemdoubleclick="toggle",
        # orientation="h",
        # x=0.5,
        # y=-0.1,
        yanchor="top",
        y=0.96,
        xanchor="left",
        x=0.01,
        font=dict(
            family="Basel, Arial, sans-serif",
            #size=10,
            # color="black"
        ),
    ),
    xaxis=dict(
        #title="Time",
        linecolor="Grey",
        fixedrange=True,
        # hoverformat=".0f",
    ),
    yaxis=dict(
        title="Average Revenue Per User Per Month",
        linecolor="Grey",
        gridwidth=1,
        gridcolor='rgba(255, 168, 251, 0.3)',
        fixedrange=True,
        # hoverformat='{y/1e6:.0f} M'
    ),
    showlegend=True,
    font=dict(
        family="Basel, Arial, sans-serif",
        # size=10,
        # color="black"
    ),
)

# Layout of the growth rate graph
layout_growth_rate_graph = go.Layout(
    # title="User Evolution",
    plot_bgcolor="White",
    dragmode=False,
    margin=go.layout.Margin(
        l=0,  # left margin
        r=0,  # right margin
        b=0,  # bottom margin
        t=20,  # top margin
    ),
    legend=dict(
        # Adjust click behavior
        itemclick="toggleothers",
        itemdoubleclick="toggle",
        yanchor="top",
        y=0.96,
        xanchor="left",
        x=0.01,
        font=dict(
            size=10,
        ),
    ),
    xaxis=dict(
        title="Users or Units",
        linecolor="Grey",
        fixedrange=True,
    ),
    yaxis=dict(
        title="Discrete Growth Rate",
        linecolor="Grey",
        gridwidth=1,
        gridcolor='rgba(255, 168, 251, 0.3)',
        fixedrange=True,
    ),
    showlegend=True,
    font=dict(
        family="Basel, Arial, sans-serif",
    ),
)

# Layout of the product maturity graph
layout_product_maturity_graph = go.Layout(
    # title="User Evolution",
    #plot_bgcolor="White",
    margin=go.layout.Margin(
        l=0,  # left margin
        r=0,  # right margin
        b=0,  # bottom margin
        t=20,  # top margin
    ),
    dragmode=False,
    legend=dict(
        # Adjust click behavior
        itemclick="toggleothers",
        itemdoubleclick="toggle",
        # orientation="h",
        # x=0.5,
        # y=-0.1,
        yanchor="top",
        y=0.96,
        xanchor="left",
        x=0.01,
        font=dict(
            # family="Courier",
            size=10,
            # color="black"
        ),
    ),
    xaxis=dict(
        #title="Timeline",
        linecolor="Grey",
        showgrid=False,
        fixedrange=True,
        # hoverformat=".0f",
    ),
    yaxis=dict(
        title="R&D Share of Revenue [%]",
        linecolor="Grey",
        showgrid=False,
        fixedrange=True,
        #gridwidth=1,
        #gridcolor='#e3e1e1',
        # hoverformat='{y/1e6:.0f} M'
    ),
    showlegend=True,
    font=dict(
        family="Basel, Arial, sans-serif",
        # size=16,
        # color="Black"
    ),
)