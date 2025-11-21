# Main file for approximating an S-curve, given a certain data set
import numpy as np
import math
from datetime import datetime
import numpy_financial as npf
from sympy.solvers import solve
from sympy import Symbol
import pandas as pd
from src.Utils.Logistics import logisticfunction, logistic_function_approximation

# ---------------------------- Importing Data for testing purpose


# --------------------------------- USER GROWTH PREDICTION --------------------------------------


def discrete_growth_rate(users, dates):
    """
    Calculation of the discrete growth rate array of length users-1. The dates are transformed in annual format
    :param users:
    :param dates:
    :return:
    """
    discretegrowthrate = np.zeros(len(dates) - 1)
    for i in range(len(dates) - 1):
        discretegrowthrate[i] = math.log(users[i + 1] / users[i]) / (dates[i + 1] - dates[i])
    return discretegrowthrate


def discrete_user_interval(users):
    """
    Calculation of the discrete user interval array of length users-1 which simply calculates the average between two
    subsequent users data
    :param users: users data
    :return:
    """
    discreteuserinterval = np.zeros(len(users) - 1)
    for i in range(len(users) - 1):
        discreteuserinterval[i] = (users[i + 1] + users[i]) / 2
    return discreteuserinterval


def rmsd(array1, array2):
    """
    Calculation of the Root Mean Square Deviation (RMSD) based on two arrays
    :param array1:
    :param array2:
    :return:
    """

    if len(array1) != len(array2):
        raise ValueError("Arrays must have the same length")

    squared_diff = np.square(np.array(array1) - np.array(array2))
    mean_squared_diff = np.mean(squared_diff)
    rmsd_value = np.sqrt(mean_squared_diff)
    return rmsd_value


def parameters_dataframe(dates, users):
    """
    Calculation of the parameters and RSquare, mapped to the amount of data ignored
    :param dates:
    :param users:
    :return:
    """
    maximum_data_ignored = 0.85  # Up to 80% of the data can be ignored
    n_data_ignored = int(round(len(dates) * maximum_data_ignored))
    dataframe = np.zeros((n_data_ignored, 6))
    # Calculation of K, r & p0 and its related RSquare for each data ignored
    for i in range(n_data_ignored):
        dates_rsquare = dates[i:len(dates)]
        users_rsquare = users[i:len(dates)]
        rd = discrete_growth_rate(users_rsquare, dates_rsquare)
        userinterval = discrete_user_interval(users_rsquare)
        k, r, p0 = logistic_function_approximation(dates_rsquare, users_rsquare)
        x_values = userinterval
        y_values = rd
        correlation_matrix = np.corrcoef(x_values, y_values)  # R Square calculation
        correlation_xy = correlation_matrix[0, 1]
        r_squared = correlation_xy ** 2
        rootmeansquare = rmsd(users_rsquare, logisticfunction(k, r, p0, dates_rsquare))
        dataframe[i, 0] = i  # Data ignored column
        dataframe[i, 1] = k  # K (carrying capacity) column
        dataframe[i, 2] = r  # r (growth rate) column
        dataframe[i, 3] = p0  # p0 (initial population) column
        dataframe[i, 4] = r_squared  # r squared column
        dataframe[i, 5] = rootmeansquare  # Root Mean Square Deviation column
    df = pd.DataFrame(dataframe, columns=['Data Ignored', 'K', 'r', 'p0', 'R Squared', 'RMSD'])
    return df


def parameters_dataframe_cleaning(df, users):
    """
    Function to clean the parameters dataframe (the dataframe containing parameters in function of the data ignored)
    Rows are deleted if: value = Nan; K<= 0.9*userMax ; r<0 ; R Squared < 0.9 ; p0 <= 0
    :param df:
    :param users:
    :return:
    """
    # Eliminate all rows where NaN values are present
    df = df.dropna()
    usersMax = np.amax(users)
    # Get names of indexes for which column K is smaller than 90% of the max user
    indexNames_K = df[df['K'] <= 0.9 * usersMax].index
    # Delete these row indexes from dataFrame
    df.drop(indexNames_K, inplace=True)
    # Get names of indexes for which column r is smaller than zero
    indexNames_r = df[df['r'] <= 0].index
    # Delete these row indexes from dataFrame
    df.drop(indexNames_r, inplace=True)
    # Get names of indexes for which column r is smaller or equal to zero
    indexNames_rSquared = df[df['R Squared'] <= 0].index
    # Delete these row indexes from dataFrame
    df.drop(indexNames_rSquared, inplace=True)
    # Get names of indexes for which column p0 is smaller that numbers very close to zero
    indexNames_p0 = df[df['p0'] < 5.775167e-11].index
    # Delete these row indexes from dataFrame
    df.drop(indexNames_p0, inplace=True)
    df_sorted = df.sort_values(by=['K'], ascending=True)
    # Resetting the indexes
    df_sorted = df_sorted.reset_index(drop=True)
    return df_sorted


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


# Analysis part

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
    t = 1 / r * math.log(pt * (k - p0) / (p0 * (k - pt)))
    return t


# ---------------------------------- DISCOUNTED CASH FLOW CALCULATION
def net_present_value(k, r, p0, arpu, profitmargin, discount_rate, years):
    """
    Cashflow is calculated by inputting the parameters of the S-Curve for future user growth prediction and by assuming
    that the cashflow is automatically calculated from today. ARPU in dollars and profit margin in (0.X) format, remain
     constant
    :param k:
    :param r:
    :param p0:
    :param arpu: ARPU in dollars
    :param profitmargin: in (0.X) format
    :param discount_rate:
    :param years:
    :return:
    """
    current_year = datetime.now().year
    t = np.linspace(1.0, years, years) + current_year - 1970  # definition of the time "cashflow size" in future years
    cashflow = logisticfunction(k, r, p0, t) * arpu * profitmargin
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


def polynomial_approximation(dates, users, n_polynomial):
    """
    Calculates discrete growth rate from users and dates. It then tries to fit a polynomial of degree n_polynomial
    to the function userintelval, discrete growthrate and return the parameters of the polynomial
    :param dates:
    :param users:
    :param n_polynomial: degree of the polynomial
    :return: parameters of the polynomial
    """
    rd = discrete_growth_rate(users, dates)
    userinterval = discrete_user_interval(users)
    parameters = np.polyfit(userinterval, rd, n_polynomial, rcond=None, full=False)
    return parameters


# This function looks very unused. Can it be removed?
def moving_average_smoothing(dates, users, window_size):
    """
    Function to smoothen the data with a given window size
    :param dates:
    :param users:
    :param window_size:
    :return:
    """
    dates_series = pd.Series(dates)
    users_series = pd.Series(users)
    smoothed_dates = dates_series.rolling(3, min_periods=1).mean()
    smoothed_users = users_series.rolling(3, min_periods=1).mean()
    smoothed_dates_array = smoothed_dates.values
    smoothed_users_array = smoothed_users.values
    return smoothed_dates_array, smoothed_users_array
