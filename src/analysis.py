import math
from datetime import datetime

import numpy as np
import numpy_financial as npf
from sympy import Symbol, solve

from src.Utils.Logistics import logisticfunction
from src.Utils.RastLogger import get_default_logger

logger = get_default_logger()


def discrete_growth_rate(users, dates):
    """
    Calculation of the discrete growth rate array of length users-1. The dates are transformed in annual format
    :param users:
    :param dates:
    :return:
    """
    users = np.asarray(users, dtype=float)
    dates = np.asarray(dates, dtype=float)
    discretegrowthrate = np.log(users[1:] / users[:-1]) / (dates[1:] - dates[:-1])
    return discretegrowthrate


def discrete_user_interval(users):
    """
    Calculation of the discrete user interval array of length users-1 which simply calculates the average between two
    subsequent users data
    :param users:
    :return:
    """
    users = np.asarray(users, dtype=float)
    discreteuserinterval = (users[1:] + users[:-1]) / 2
    return discreteuserinterval


def growth_scenarios_summary(df):
    """
    Function creating 3 growth scenarios out of a given dataframe
    First row is the lowest K, Second row is the best R^2, Third row is the highest K
    :param df:
    :return:
    """
    column_K = df["K"]
    column_RSquared = df["R Squared"]
    max_index = column_K.idxmax()
    min_index = column_K.idxmin()
    best_index = column_RSquared.idxmax()
    mid_index = int(len(df["K"]) / 2)
    df_sorted = df.drop(index=df.index.difference([max_index, min_index, mid_index]))
    df_sorted = df_sorted.sort_values(by=['K'], ascending=True)
    return df_sorted


def time_to_population(k, r, p0, pt):
    """
    Function for calculating at what time a certain population is reached
    (logistic function solved for t if p(t) is known)
    :param k:
    :param r:
    :param p0:
    :param pt:
    :return:
    """
    try:
        t = 1 / r * math.log(pt * (k - p0) / (p0 * (k - pt)))
    except ValueError:
        logger.info("Invalid input values. Ensure (pt * (k - p0)) / (p0 * (k - pt)) is greater than 0.")
        return 50.0
    return t


def net_present_value(k, r, p0, arpu, profitmargin, discount_rate, years):
    """
    Cashflow is calculated by inputting the parameters of the S-Curve for future user growth prediction and by assuming
    that the cashflow is automatically calculated from today. ARPU in dollars and profit margin in (0.X) format,
     remain constant
    :param k:
    :param r:
    :param p0:
    :param arpu:
    :param profitmargin:
    :param discount_rate:
    :param years:
    :return:
    """
    current_year = datetime.now().year
    t = np.linspace(1.0, years, years) + current_year - 1970  # definition of the time "cashflow size" in future years
    cashflow = logisticfunction(k, r, p0, t) * arpu * profitmargin
    discounted_cashflow = npf.npv(discount_rate, cashflow)
    return discounted_cashflow


def net_present_value_arpu_growth(k, r, p0, arpu, arpu_growth, profitmargin, discount_rate, years):
    """
    Cashflow is calculated same way as above but by including a growth rate for the ARPU over time
    :param k:
    :param r:
    :param p0:
    :param arpu:
    :param arpu_growth:
    :param profitmargin:
    :param discount_rate:
    :param years:
    :return:
    """
    current_year = datetime.now().year
    t = np.linspace(1.0, years, years) + current_year - 1970  # definition of the time "cashflow size" in future years
    arpu_over_time = [arpu * (1 + arpu_growth) ** year for year in range(years)]
    cashflow = logisticfunction(k, r, p0, t) * arpu_over_time * profitmargin
    discounted_cashflow = npf.npv(discount_rate, cashflow)

    return discounted_cashflow


def arpu_for_valuation(k, r, p0, profitmargin, discount_rate, years, valuation):
    """
    Calculating the arpu needed to reach a certain valuation
    :param k:
    :param r:
    :param p0:
    :param profitmargin:
    :param discount_rate:
    :param years:
    :param valuation:
    :return:
    """
    x = Symbol('x')
    function_to_solve = solve(net_present_value(k, r, p0, x, profitmargin, discount_rate, years) - valuation, x)
    arpu = float(function_to_solve[0])
    return arpu


def profit_margin_for_valuation(k, r, p0, arpu, arpu_growth, discount_rate, years, noa_assets, valuation):
    """
    Calculating the profit margin needed to reach a certain valuation
    :param k:
    :param r:
    :param p0:
    :param arpu:
    :param arpu_growth:
    :param discount_rate:
    :param years:
    :param noa_assets:
    :param valuation:
    :return:
    """
    x = Symbol('x')
    function_to_solve = solve(
        net_present_value_arpu_growth(k, r, p0, arpu, arpu_growth, x, discount_rate, years) + noa_assets - valuation, x)
    profit_margin = float(function_to_solve[0])
    return profit_margin


def hype_meter_indicator_values(hype_ratio):
    """
    Function defining the color and the text of the hype meter indicator, depending on the size of the hype compared to
    the total market cap. The color changes the outline of the badge while the text changes its value
    :param hype_ratio:
    :return:
    """
    if hype_ratio <= 0:  # if hype ratio is smaller than 10%
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