# Main file for approximating an S-curve, given a certain data set

import jwt
import numpy as np

from src.Utils.dates import YEAR_OFFSET, date_formatting


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
        print("An error occured while calculating the min & max of the datepicker")
        return "", "", "", [], []


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
