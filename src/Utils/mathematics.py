import math

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from sklearn import linear_model

from src.Utils.Logistics import logfuncgeneric
from src.analysis import discrete_growth_rate, discrete_user_interval

from src.Utils.RastLogger import get_default_logger

logger = get_default_logger()


def linear_regression(users, revenue):
    """
    Simple linear regression function returning R^2. Used to assess the correlation between users & revenue
    a high correlation signifies that the metric used is most probably the right one because it perfectly describes
    the revenue
    :param users:
    :param revenue:
    :return:
    """
    reg = linear_model.LinearRegression()
    x = users.reshape(-1, 1)
    y = revenue.reshape(-1, 1)
    regression = reg.fit(x, y)
    r_squared = regression.score(x, y)

    return r_squared


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


def rsquare_calculation(observed_values, approximated_values):
    """
    calculates rsquared of the correlation matrix of observed_values, approximated_values
    :param observed_values:
    :param approximated_values:
    :return:
    """
    x_values = observed_values
    y_values = approximated_values
    correlation_matrix = np.corrcoef(x_values, y_values)  # R Square calculation
    correlation_xy = correlation_matrix[0, 1]
    r_squared = correlation_xy ** 2
    return r_squared


def polynomial_approximation(dates, users, n_polynome):
    """
    Calculates growth rate by using dates and users. Then tries to fit a polynomial of degree n_polynome to
    userinterval and the growth rate. Return the parameters of the fitted polynomial
    :param dates:
    :param users:
    :param n_polynome: degree of polynomial
    :return:
    """
    rd = discrete_growth_rate(users, dates)
    userinterval = discrete_user_interval(users)
    parameters = np.polyfit(userinterval, rd, n_polynome, rcond=None, full=False)
    return parameters


def log_approximation(dates, users):
    """
    Calculates growth rate by using dates and users. Then tries to fit a linear function to the log of the userinterval
     and the growth rate. Return the parameters of the fitted linear function.
    :param dates:
    :param users:
    :return:
    """
    rd = discrete_growth_rate(users, dates)
    userinterval = discrete_user_interval(users)
    parameters = np.polyfit(np.log(userinterval), rd, 1, rcond=None, full=False)
    return parameters


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
    smoothed_dates = dates_series.rolling(window_size, min_periods=1).mean()
    smoothed_users = users_series.rolling(window_size, min_periods=1).mean()
    smoothed_dates_array = smoothed_dates.values
    smoothed_users_array = smoothed_users.values
    return smoothed_dates_array, smoothed_users_array


def logistic_parameters_given_K(dates, users, k):
    """
    Function calculating r, p0, given a certain k. In the function, k is added to the dataset and the dataset in then
    centered around (k, 0) to perform an intercepted regression.
    :param dates:
    :param users:
    :param k:
    :return:
    """
    discretegrowthrate_initial = discrete_growth_rate(users, dates)
    # discretegrowthrate = np.append(discretegrowthrate_initial, 0)  # adding zero to the discrete growth rate array
    user_interval_initial = discrete_user_interval(users)
    # user_interval = np.append(user_interval_initial, k)  # adding k to the user interval array

    user_interval = user_interval_initial - k  # Centering around the last point (0, K) by substracting K to the entire dataset
    discretegrowthrate = discretegrowthrate_initial
    reg = linear_model.LinearRegression(fit_intercept=True)  # Forcing the regression to go through 0,0
    x = user_interval.reshape(-1, 1)
    y = discretegrowthrate.reshape(-1, 1)
    regression = reg.fit(x, y)
    coefficient = regression.coef_  # slope "a" of the function "y(x)=a*x"
    intercept = coefficient * (user_interval[0])  # The final intercept is found by computing the function for x=K
    r_growth_rate = float(intercept)

    exp_r_dates = np.exp(r_growth_rate * dates)
    p0_all = users * k / (-users * (exp_r_dates - 1) + k * exp_r_dates)
    p0_initialusers = np.mean(p0_all)

    # Rsquare calculation
    observed_data_log = discretegrowthrate
    approximated_values_log = -r_growth_rate / k * user_interval + r_growth_rate
    # Calculate R-squared
    r_squared = rsquare_calculation(observed_data_log, approximated_values_log)
    return r_growth_rate, p0_initialusers, r_squared,


def logistic_function_approximation(dates, users):
    """
    Function calculating K, r & P0 given the discrete growth rate and the dates
    A linear regression is done on the calculated discrete growth rate to obtain the carrying capacity K
    (the X value of f(x)=0) and r the slope of the linear function
    P0 is calculating by averaging the P0 calculated in the initial logistic function
    :param dates:
    :param users:
    :return:
    """
    discretegrowthrate = discrete_growth_rate(users, dates)
    user_interval = discrete_user_interval(users)
    reg = linear_model.LinearRegression()
    x = user_interval.reshape(-1, 1)
    y = discretegrowthrate.reshape(-1, 1)
    regression = reg.fit(x, y)
    coefficient = regression.coef_
    intercept = regression.intercept_
    r_growth_rate = float(intercept)
    if coefficient == 0:
        k_carrying_capacity = 0
    else:
        k_carrying_capacity = float(-intercept / coefficient)


    # Calculate P0 (initial population) using broadcasted NumPy expression
    exp_r_dates = np.exp(r_growth_rate * dates)
    p0_all = users * k_carrying_capacity / (-users * (exp_r_dates - 1) + k_carrying_capacity * exp_r_dates)
    p0_initialusers = np.mean(p0_all)
    return k_carrying_capacity, r_growth_rate, p0_initialusers


def logistic_function_approximation_method(dates, users):
    """
    Finding the different parameters k,r & p0 using a standard curve-fit method,
    using the original k,r & p0 as starting points
    :param dates:
    :param users:
    :return:
    """
    k, r, user0 = logistic_function_approximation(dates, users)
    thalf = (1 / r) * math.log(k / user0 - 1)
    popt, pcov = curve_fit(logfuncgeneric, dates, users, p0=[k, r, thalf])
    return popt