
# Main file for approximating an S-curve, given a certain data set
import numpy as np
import math
from sklearn import linear_model
# import scikit_learn
from scipy.optimize import curve_fit
from datetime import datetime
import numpy_financial as npf
# from sklearn import linear_model
# from sklearn.metrics import mean_squared_error
from sympy.solvers import solve
from sympy import Symbol
import sqlite3
import pandas as pd
import plotly.express as px
# import matplotlib.pyplot as plt

# ---------------------------- Importing Data for testing purpose

# DO NOT DELETE Transforming string dates in yearly float format (example: Jun.11 -> 2011.4167)
SECONDS_PER_YEAR = 31557600  # Number of seconds in a year


# This function takes a panda series date of format YYYY-MM-DD and returns a decimal year, with year 0 in 1970
def date_formatting(dates):
    def date_to_decimal_year(date_obj):
        years_diff = date_obj.year - 1970
        year_fraction = (date_obj.month - 1 + (date_obj.day - 1) / 30.0) / 12.0
        decimal_year = years_diff + year_fraction
        return decimal_year
    date_objects = pd.to_datetime(dates)
    decimal_years = date_objects.apply(date_to_decimal_year)
    return decimal_years


# --------------------------------- USER GROWTH PREDICTION --------------------------------------


# Calculation of the discrete growth rate array of length users-1. The dates are transformed in annual format
def discrete_growth_rate(users, dates):
    discretegrowthrate = np.zeros(len(dates) - 1)
    for i in range(len(dates) - 1):
        discretegrowthrate[i] = math.log(users[i + 1] / users[i]) / (dates[i + 1] - dates[i])
    return discretegrowthrate


# Calculation of the discrete user interval array of length users-1 which simply calculates the average between two
# subsequent users data
def discrete_user_interval(users):
    discreteuserinterval = np.zeros(len(users) - 1)
    for i in range(len(users) - 1):
        discreteuserinterval[i] = (users[i + 1] + users[i]) / 2
    return discreteuserinterval


# Logistic function, return Y given the parameters k, r and p0
def logisticfunction(k, r, p0, dates):
    #y = (k*p0*np.exp(r*dates))/(k+p0*(np.exp(r*dates)-1))  OLD METHOD
    y = np.zeros(len(dates))
    for i in range(len(dates)):
        y[i] = (k*p0*np.exp(r*dates[i]))/(k+p0*(np.exp(r*dates[i])-1))
    return y


# Q(t) = Qinf/(1 + exp(-alpha*(t-thalf)))
# This function is an alternative to (K.*P0.*exp(r.*t))./(K+P0.*(exp(r.*t)-1))
# Where K=Qinf, r=alpha, p0=Q(0)
def logfuncgeneric(qinf, alpha, thalf, dates):
    y = qinf/(1 + math.exp(-alpha*(dates-thalf)))
    return y


# Function calculating K, r & P0 given the discrete growth rate and the dates
# A linear regression is done on the calculated discrete growth rate to obtain the carrying capacity K
# (the X value of f(x)=0) and r the slope of the linear function
# P0 is calculating by averaging the P0 calculated in the initial logistic function
def logistic_function_approximation(dates, users):
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

    # Nested function to be created to calculate different P0, initial population
    def p0_function(usersp, datesp, k, r):
        p0 = usersp * k / (-usersp * (np.exp(r * datesp) - 1) + k * np.exp(r * datesp))
        return p0

    p0_all_func = np.vectorize(p0_function)
    p0_all = p0_all_func(users, dates, k_carrying_capacity, r_growth_rate)
    p0_initialusers = np.mean(p0_all)
    return k_carrying_capacity, r_growth_rate, p0_initialusers


# Finding the different parameters k,r & p0 using a standard curve-fit method,
# using the original k,r & p0 as starting points
def logistic_function_approximation_method(dates, users):
    k, r, user0 = logistic_function_approximation(dates, users)
    thalf = (1/r)*math.log(k/user0-1)
    popt, pcov = curve_fit(logfuncgeneric, dates, users, p0=[k, r, thalf])
    return popt


# Calculation of the RSquare in function of the number of first data point ignored
def rsquare_calculation(dates, users):
    maximum_data_ignored = 0.85  # Up to 85% of the data can be ignored
    n_data_ignored = int(round(len(dates)*maximum_data_ignored))
    r_squares = np.zeros(n_data_ignored)
    k_data_ignored = np.zeros(n_data_ignored)
    data_ignored = np.zeros(n_data_ignored)
    # Calculation of K, r & p0 and its related RSquare for each data ignored
    for i in range(n_data_ignored):
        dates_rsquare = dates[i:len(dates)]
        users_rsquare = users[i:len(dates)]
        rd = discrete_growth_rate(users_rsquare, dates_rsquare)
        userinterval = discrete_user_interval(users_rsquare)
        k, r, p0 = logistic_function_approximation(dates_rsquare, users_rsquare)
        k_data_ignored[i] = k
        # Calculating the RSquare for all data
        x_values = users
        y_values = logisticfunction(k, r, p0, dates)
        correlation_matrix = np.corrcoef(x_values, y_values)
        correlation_xy = correlation_matrix[0, 1]
        r_squares[i] = correlation_xy ** 2
        mse[i] = mean_squared_error(x_values, y_values)
    return r_squares, mse

# Calculation of the parameters and RSquare, mapped to the amount of data ignored
def parameters_dataframe(dates, users):
    maximum_data_ignored = 0.85  # Up to 80% of the data can be ignored
    n_data_ignored = int(round(len(dates)*maximum_data_ignored))
    dataframe = np.zeros((n_data_ignored, 5))
    # Calculation of K, r & p0 and its related RSquare for each data ignored
    for i in range(n_data_ignored):
        dates_rsquare = dates[i:len(dates)]
        users_rsquare = users[i:len(dates)]
        rd = discrete_growth_rate(users_rsquare, dates_rsquare)
        userinterval = discrete_user_interval(users_rsquare)
        k, r, p0 = logistic_function_approximation(dates_rsquare, users_rsquare)
        x_values = users_rsquare
        y_values = logisticfunction(k, r, p0, dates_rsquare)
        correlation_matrix = np.corrcoef(x_values, y_values) # R Square calculation
        correlation_xy = correlation_matrix[0, 1]
        r_squared = correlation_xy ** 2
        dataframe[i, 0] = i  # Data ignored column
        dataframe[i, 1] = k  # K (carrying capacity) column
        dataframe[i, 2] = r  # r (growth rate) column
        dataframe[i, 3] = p0  # p0 (initial population) column
        dataframe[i, 4] = r_squared  # r squared column
    df = pd.DataFrame(dataframe, columns=['Data Ignored', 'K', 'r', 'p0', 'R Squared'])
    return df


# Function to clean the parameters dataframe (the dataframe containing parameters in function of the data ignored)
# Rows are deleted if: value = Nan; K<=userMax ; r<0 ; R Squared < 0.9 ; p0 <= 0
def parameters_dataframe_cleaning(df, users):
    # Eliminate all rows where NaN values are present
    df = df.dropna()
    usersMax = np.amax(users)
    # Get names of indexes for which column K is smaller than the max user
    indexNames_K = df[df['K'] <= usersMax].index
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
    # Get names of indexes for which column p0 is smaller or equal to zero
    indexNames_p0 = df[df['p0'] <= 0].index
    # Delete these row indexes from dataFrame
    df.drop(indexNames_p0, inplace=True)
    df_sorted = df.sort_values(by=['K'], ascending=True)
    # Resetting the indexes
    df_sorted= df_sorted.reset_index(drop=True)
    return df_sorted


# Function creating 3 growth scenarios out of a given dataframe
# First row is the lowest K, Second row is the best R^2, Third row is the highest K
def growth_scenarios_summary(df):
    column_K = df["K"]
    column_RSquared = df["R Squared"]
    max_index = column_K.idxmax()
    min_index = column_K.idxmin()
    best_index = column_RSquared.idxmax()
    mid_index = int(len(df["K"])/2)
    df_sorted = df.drop(index=df.index.difference([max_index, min_index, mid_index]))
    df_sorted = df_sorted.sort_values(by=['K'], ascending=True)
    return df_sorted



# Analysis part


# Function for calculating at what time a certain population is reached
# (logistic function solved for t if p(t) is known)
def time_to_population(k, r, p0, pt):
    t = 1/r*math.log(pt*(k-p0)/(p0*(k-pt)))
    return t


# ---------------------------------- DISCOUNTED CASH FLOW CALCULATION
# Cashflow is calculated by inputting the parameters of the S-Curve for future user growth prediction and by assuming
# that the cashflow is automatically calculated from today. ARPU in dollars and profit margin in (0.X) format, remain constant
def net_present_value(k, r, p0, arpu, profitmargin, discount_rate, years):
    current_year = datetime.now().year
    t = np.linspace(1.0, years, years) + current_year - 1970 # definition of the time "cashflow size" in future years
    cashflow = np.array(years)
    cashflow = logisticfunction(k, r, p0, t) * arpu * profitmargin
    discounted_cashflow = npf.npv(discount_rate, cashflow)
    return discounted_cashflow


# Calculating the arpu needed to reach a certain valuation
def arpu_for_valuation(k, r, p0, profitmargin, discount_rate, years, valuation):
    x = Symbol('x')
    function_to_solve = solve(net_present_value(k, r, p0, x, profitmargin, discount_rate, years) - valuation, x)
    arpu = float(function_to_solve[0])
    return arpu

