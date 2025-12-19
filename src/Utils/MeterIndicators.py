def hype_meter_indicator_values(hype_ratio: float) -> (str, str):
    """
    Function defining the color and the text of the hype meter indicator, depending on the size of the hype compared to
    the total market cap. The color changes the outline of the badge while the text changes its value
    :param hype_ratio:
    :return:
    """
    if hype_ratio <= 0.0:  # if hype ratio is smaller than 10%
        indicator_color = "teal"
        indicator_text = "Undervalued!"
    elif hype_ratio < 0.1:  # if hype ratio is smaller than 10%
        indicator_color = "orange"
        indicator_text = "Marginally Hyped"
    elif hype_ratio < 0.15:  # if hype ratio is smaller than 15%
        indicator_color = "orange"
        indicator_text = "Moderately Hyped"
    elif hype_ratio < 0.2:  # if hype ratio is smaller than 20%
        indicator_color = "orange"
        indicator_text = "Strongly Hyped"
    else:  # if hype ratio is higher than 20%
        indicator_color = "red"
        indicator_text = "Super hyped!"
    return indicator_color, indicator_text


def hype_meter_indicator_values_new(hype_score: float) -> (str, str):
    """
    Function defining the color and the text of the hype meter indicator, depending on the size of the hype compared to
    the total market cap. The color changes the outline of the badge while the text changes its value
    :param hype_score:
    :return:
    """
    if hype_score > 2.5:
        badge_color = "red"
        badge_label = "Super hyped"
    elif hype_score > 1.5:
        badge_color = "orange"
        badge_label = "Mildly hyped"
    elif hype_score > 1:
        badge_color = "yellow"
        badge_label = "Marginally hyped"
    elif hype_score > 0:
        badge_color = "green"
        badge_label = "Fairly priced"
    else:
        badge_color = "teal"
        badge_label = "Undervalued"
    return badge_color, badge_label


def growth_meter_indicator_values(growth_score: float) -> (str, str):
    """
    Returns badge_color and badge_label depending on growth score
    :param growth_score:
    :return: badge_color and badge_label depending on growth score
    """
    if growth_score > 0.5:
        badge_color_growth = "teal"
        badge_label_growth = "Massive growth"
    elif growth_score > 0.3:
        badge_color_growth = "green"
        badge_label_growth = "Strong growth"
    elif growth_score > 0.1:
        badge_color_growth = "yellow"
        badge_label_growth = "Limited growth"
    else:
        badge_color_growth = "red"
        badge_label_growth = "Poor growth"
    return badge_color_growth, badge_label_growth