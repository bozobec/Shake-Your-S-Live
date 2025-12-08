# Main file for approximating an S-curve, given a certain data set

import jwt
import numpy as np

from src.Utils.dates import YEAR_OFFSET, date_formatting
from src.Utils.RastLogger import get_default_logger

logger = get_default_logger()

MIN_DATEPICKER_INDEX = 4  # For a given dataset, this is the minimum below which no date can be selected


def datepicker_limit(dataset_df):
    """
    Function to provide the minimum and maximum date of the datepicker for a given dataset as a pandas dataframe and
    formats the dataframe as an output
    :param dataset_df:
    :return:
    """
    if dataset_df is not None:
        dates = np.array(date_formatting(dataset_df["Date"]))

        dates_formatted = dates + YEAR_OFFSET
        dates_unformatted = np.array(dataset_df["Date"])

        dataset_df_formatted = dataset_df.copy()
        dataset_df_formatted["Date"] = dates_formatted

        date_value_datepicker = str(dates_unformatted[-1])
        min_history_datepicker = str(dates_unformatted[MIN_DATEPICKER_INDEX])
        max_history_datepicker = str(dates_unformatted[-1])

        return min_history_datepicker, max_history_datepicker, date_value_datepicker, dataset_df_formatted
    else:
        # Return default values or handle as needed in case of an error
        logger.info("An error occured while calculating the min & max of the datepicker")
        return "", "", "", [], []


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


def get_industry_icon(industry: str) -> str:
    """
    Generate an icon per industry
    :param industry:
    :return:
    """
    """
    Return an Iconify icon name corresponding to a given industry.
    """

    mapping = {
        "E-Commerce & DTC Retail": "mdi:cart-outline",
        "SaaS & Enterprise Software": "mdi:cloud-outline",
        "Cybersecurity & Infrastructure": "mdi:shield-lock-outline",
        "Fintech & Payments": "mdi:credit-card-outline",
        "Consumer Platforms & Marketplaces": "mdi:account-group-outline",
        "Media, Streaming & Entertainment": "mdi:television-play",
        "Automotive & Advanced Manufacturing": "mdi:factory",
        "Mobility, Delivery & Transportation": "mdi:truck-delivery-outline",
        "Restaurants & Food Chains": "mdi:food-fork-drink",
        "Energy": "mdi:leaf",
        "IT Services & Consulting": "mdi:laptop-account",
        "Healthcare & Insurance": "mdi:medical-bag",
    }

    # Return the matching icon or a default
    return mapping.get(industry, "mdi:briefcase-outline")


def verify_token(token):
    """
    Verify JWT (simplified, replace with proper signature verification in production)
    :param token:
    :return:
    """
    try:
        claims = jwt.decode(token, options={"verify_signature": False})
        return claims
    except Exception:
        return None


def replace_inf_with_previous_2(df, column):
    """
    Replace the infinite values and Nan values
    This is a fix that should be fixed by improving the valuation in the first place
    :param df:
    :param column:
    :return:
    """
    """
    Replace infinite values in a column with the value from 2 rows back.

    Parameters:
    -----------
    df : pandas.DataFrame
        The dataframe to modify
    column : str
        The name of the column to check and replace infinite values

    Returns:
    --------
    pandas.DataFrame
        DataFrame with infinite values replaced
    """
    # Create a copy to avoid modifying the original
    df_copy = df.copy()

    # Find indices where values are infinite OR NaN
    inf_mask = np.isinf(df_copy[column]) | df_copy[column].isna()

    # Get indices of infinite values
    inf_indices = df_copy[inf_mask].index

    # Replace each infinite value with value from 2 rows back or next value (if no 2 rows back exist)
    for idx in inf_indices:
        idx_position = df_copy.index.get_loc(idx)
        if idx_position >= 2:  # Check if there are at least 2 rows before
            previous_scenario_idx = df_copy.index[idx_position - 2]
            prev_scenario_value = df_copy.loc[previous_scenario_idx, column]
        else:
            next_valuation_idx = df_copy.index[idx_position - 2]
            prev_scenario_value = df_copy.loc[next_valuation_idx, column]

        # Takes the highest value between the previous high valuation OR the current low one +20%
        df_copy.loc[idx, column] = prev_scenario_value
        # If less than 2 rows back, leave as inf or handle differently

    return df_copy


def cleans_high_valuations(df, column):
    """
    Check if every second value (high valuation) is smaller than the previous one (low valuation).
    If it is, replace it with the previous value * 1.2.

    Parameters:
    -----------
    df : pandas.DataFrame
        The dataframe to modify
    column : str
        The name of the column to check and adjust values

    Returns:
    --------
    pandas.DataFrame
        DataFrame with adjusted values
    """
    # Create a copy to avoid modifying the original
    df_copy = df.copy()

    # Iterate through every second row starting from index 1 (second row)
    for i in range(1, len(df_copy), 2):
        current_idx = df_copy.index[i]
        previous_idx = df_copy.index[i - 1]
        previous_high_valuation_idx = df_copy.index[i - 2]

        current_value = df_copy.loc[current_idx, column]
        previous_value = df_copy.loc[previous_idx, column]

        previous_high_valuation = df_copy.loc[previous_high_valuation_idx, column]

        # Check if current value is smaller than previous value
        if current_value < previous_value:
            # Replace with previous value * 1.2
            df_copy.loc[current_idx, column] = previous_high_valuation

    return df_copy
