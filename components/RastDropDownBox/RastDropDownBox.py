import components.RastDropDownBox.RastDropDown as RastDropDown
import dash_mantine_components as dmc


def create(labels):
    """
    Creates a box around the RastDropBox and feeds the provided labels through to the RastDropBox. Expects
    the labels coming from AirTableAPI
    :param labels: labels coming from AirTableAPI
    :return:
    """
    return dmc.Box(
        RastDropDown.create(labels=labels),
        style={
            "minWidth": {"base": "200px", "sm": "250px", "lg": "400px"},  # Changed to minWidth
            "flex": "1 1 0%",  # Use 0% as flex-basis for consistent behavior
            "maxWidth": {"lg": "80%"},
        },
        id="dropdown-container"
    )
