// assets/dashAgGridComponentFunctions.js
var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};


// Renderer for Industry Icons
//dagcomponentfuncs.IndustryIconRenderer = function (params) {
//    return React.createElement(
//        "div",
//        { style: { textAlign: 'center' } },
//        React.createElement("i", { className: "iconify", "data-icon": params.data.industry_icon })
//    );
//};


// Renderer for Company Links
dagcomponentfuncs.CompanyLinkRenderer = function (params) {
    const url = "https://app.rast.guru/?company=" + params.value;
    return React.createElement(
        "a",
        { href: url, target: "_blank", style: { color: "#953AF6", textDecoration: "none", fontWeight: "bold"} },
        params.value
    );
};

dagcomponentfuncs.ScoreBadgeRenderer = function (params) {
    const isHype = params.column.colId === "Hype Score";
    const meta = isHype ? params.data.hype_meta : params.data.growth_meta;

    if (!meta) return params.value;

    return React.createElement(
        "div",
        {
            style: {
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                width: "100%",
                height: "100%",
                gap: "8px"
            }
        },
        React.createElement("span", { style: { fontFamily: "monospace" } }, params.value.toFixed(2)),

        React.createElement(
            "div",
            {
                style: {
                    border: `1px solid ${meta.color}`,
                    color: meta.color,
                    backgroundColor: "transparent",
                    // --- MAXIMUM ROUNDNESS ---
                    borderRadius: "100px",
                    // --------------------------
                    padding: "0px 10px",        // Slightly more horizontal padding for pills
                    fontSize: "10px",
                    fontWeight: "700",
                    textTransform: "uppercase",
                    lineHeight: "16px",         // Adjusted for the pill shape
                    whiteSpace: "nowrap",
                    display: "inline-flex",
                    alignItems: "center",
                    height: "18px"              // Fixed height helps maintain the pill look
                }
            },
            meta.label
        )
    );
};