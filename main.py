# Main file for approximating an S-curve, given a certain data set
import base64
# import datetime
import io
import math
from datetime import datetime, timedelta

import jwt
import numpy as np
import numpy_financial as npf
import pandas as pd
from dash import html, dash_table
from scipy.optimize import curve_fit
from sklearn import linear_model
from sympy import Symbol
# from sklearn import linear_model
# from sklearn.metrics import mean_squared_error
from sympy.solvers import solve

# ---------------------------- Importing Data for testing purpose

# DO NOT DELETE Transforming string dates in yearly float format (example: Jun.11 -> 2011.4167)
SECONDS_PER_YEAR = 31557600  # Number of seconds in a year
YEAR_OFFSET = 1970 # Offset taken to define the year zero
MIN_DATEPICKER_INDEX = 4  # For a given dataset, this is the minimum below which no date can be selected


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

# This function transforms a date string of format 2023-11-01T11:29:13.362885 to a number of format 2023.83
def date_formatting_from_string(date_string):
    # Parse the date string to get the year, month, and day
    date_obj = datetime.strptime(date_string[:10], "%Y-%m-%d")
    year = date_obj.year
    month = date_obj.month
    day = date_obj.day

    # Calculate the fraction of the year
    fraction_of_year = (month - 1) / 12 + (day - 1) / 365

    # Combine the year and fraction of the year
    return year + fraction_of_year

# This function transforms a date string of format 2023-11-01T11:29:13.362885 to a number of format 2023.83
def string_formatting_to_date(decimal_year):
    year = int(decimal_year)
    fraction_of_year = decimal_year - year

    # Calculate the month and day
    month = int((fraction_of_year * 12) + 1)
    day = int((fraction_of_year * 365) + 1)

    # Ensure the day and month values are within the valid range
    if month > 12:
        month = 12
    if day > 31:
        day = 31

    # Create a date string in the desired format
    # date_string = f"{day:02d} {datetime(2000, month, 1).strftime('%B')} {year}"
    date_string = f"{datetime(2000, month, 1).strftime('%B')} {year}"

    return date_string

# The following function transforms a date of format 2016.99 to a date 2016-12-31
def transform_date_format(input_date):
    # Extract the year and fraction part from the float
    year = int(input_date)
    fraction = input_date - year

    # Calculate the day of the year based on the fraction
    total_days = int(fraction * 365)

    # Create a datetime object with the calculated year and day of the year
    transformed_date = datetime(year, 1, 1) + timedelta(days=total_days)

    return transformed_date.strftime("%Y-%m-%d")


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
        try:
            y[i] = (k*p0*np.exp(r*dates[i]))/(k+p0*(np.exp(r*dates[i])-1))
        except:
            y[i] = 0
            print("Log function could not be computed with the following parameters")
            print("k", k, "r", r, "p0", p0)
    return y


# Q(t) = Qinf/(1 + exp(-alpha*(t-thalf)))
# This function is an alternative to (K.*P0.*exp(r.*t))./(K+P0.*(exp(r.*t)-1))
# Where K=Qinf, r=alpha, p0=Q(0)
def logfuncgeneric(qinf, alpha, thalf, dates):
    y = qinf/(1 + math.exp(-alpha*(dates-thalf)))
    return y

# Simple linear regression function returning R^2. Used to assess the correlation between users & revenue
# a high correlation signifies that the metric used is most probably the right one because it perfectly describes
# the revenue

def linear_regression(users, revenue):
    reg = linear_model.LinearRegression()
    x = users.reshape(-1, 1)
    y = revenue.reshape(-1, 1)
    regression = reg.fit(x, y)
    coefficient = regression.coef_
    intercept = regression.intercept_
    r_squared = regression.score(x, y)
    #revenue_predicted = predict(revenue)

    return r_squared

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


# Calculation of the Root Mean Square Deviation (RMSD) based on two arrays
def rmsd(array1, array2):
    if len(array1) != len(array2):
        raise ValueError("Arrays must have the same length")

    squared_diff = np.square(np.array(array1) - np.array(array2))
    mean_squared_diff = np.mean(squared_diff)
    rmsd_value = np.sqrt(mean_squared_diff)
    return rmsd_value

def rsquare_calculation (observed_values, approximated_values):
    x_values = observed_values
    y_values = approximated_values
    correlation_matrix = np.corrcoef(x_values, y_values) # R Square calculation
    correlation_xy = correlation_matrix[0, 1]
    r_squared = correlation_xy ** 2
    return r_squared

# Calculation of the parameters and RSquare, mapped to the amount of data ignored
def parameters_dataframe(dates, users):
    number_moving_average = 4  # Number of moving averages allowed
    n_data_ignored = len(dates)-3  # Number of data until which to be ignored
    dataframe = np.zeros((n_data_ignored*number_moving_average, 9))
    # Calculation of K, r & p0 and its related RSquare for each data ignored
    for i in range(0,number_moving_average):
        moving_average = i+1
        if moving_average==1:
            pass
        else:
            dates, users = moving_average_smoothing(dates, users, moving_average)
        for j in range(n_data_ignored):
            try:
                dates_rsquare = dates[j:len(dates)]
                users_rsquare = users[j:len(dates)]
                rd = discrete_growth_rate(users_rsquare, dates_rsquare)
                userinterval = discrete_user_interval(users_rsquare)
                try:
                    k, r, p0 = logistic_function_approximation(dates_rsquare, users_rsquare)
                except:
                    k, r, p0 = 0
                    print("Parameters could not be calculated for: ", j, " data ignored")
                if k == 0:
                    print("Issue when ignoring", j, "data")
                    raise RuntimeError("Skipping ignoring", j, " data")
                observed_values_df = rd
                approximated_values_df = -r/k*userinterval+r
                r_squared = rsquare_calculation(observed_values_df, approximated_values_df)
                try:
                    rootmeansquare = rmsd(users_rsquare, logisticfunction(k, r, p0, dates_rsquare))
                except:
                    rootmeansquare = 0
                    print("rmsd could not be calculated when ignoring:", n_data_ignored, " number of data points")
                logfit = log_approximation(dates_rsquare, users_rsquare)

                approximated_values_log = rsquare_calculation(observed_values_df, np.polyval(logfit, np.log(userinterval)))
                diff_lin_log = approximated_values_log-r_squared

                dataframe[j+i*n_data_ignored, 0] = j  # Data ignored column
                dataframe[j+i*n_data_ignored, 1] = k  # K (carrying capacity) column
                dataframe[j+i*n_data_ignored, 2] = r  # r (growth rate) column
                dataframe[j+i*n_data_ignored, 3] = p0  # p0 (initial population) column
                dataframe[j+i*n_data_ignored, 4] = r_squared  # r squared column
                dataframe[j+i*n_data_ignored, 5] = rootmeansquare / ((users[0]+users[-1])/2)  # Root Mean Square Deviation column
                dataframe[j+i*n_data_ignored, 6] = approximated_values_log  # Root Mean Square Deviation of the log approximation column
                dataframe[j+i*n_data_ignored, 7] = diff_lin_log  # Difference between the linear R^2 and the log R^2
                dataframe[j+i*n_data_ignored, 8] = moving_average  # Difference between the linear R^2 and the log R^2
            except RuntimeError as e:
                dataframe[j+i*n_data_ignored, 0] = 0  # Data ignored column
                dataframe[j+i*n_data_ignored, 1] = 0  # K (carrying capacity) column
                dataframe[j+i*n_data_ignored, 2] = 0  # r (growth rate) column
                dataframe[j+i*n_data_ignored, 3] = 0  # p0 (initial population) column
                dataframe[j+i*n_data_ignored, 4] = 0  # r squared column
                dataframe[j+i*n_data_ignored, 5] = 0  # Root Mean Square Deviation column
                dataframe[j+i*n_data_ignored, 6] = 0  # Root Mean Square Deviation of the log approximation column
                dataframe[j+i*n_data_ignored, 7] = 0  # Difference between the linear R^2 and the log R^2
                dataframe[j+i*n_data_ignored, 8] = 0  # Difference between the linear R^2 and the log R^2
    pd.set_option('display.max_rows', None)
    df = pd.DataFrame(dataframe, columns=['Data Ignored', 'K', 'r', 'p0', 'R Squared', 'RMSD', 'R Squared LOG', 'Lin/Log Diff', 'Moving Average'])
    df['Method'] = 'Linear regression'
    return df

# Function calculating function parameters for different moving averages (1-4)
def parameters_dataframe_moving_average(dates, users):
    for i in range(4):
        print("9")
    return 1


# Function to clean the parameters dataframe (the dataframe containing parameters in function of the data ignored)
# Rows are deleted if: value = Nan; K<= 0.9*userMax ; r<0 ; R Squared < 0.2 ; p0 <= 0
def parameters_dataframe_cleaning(df, users):
    # Eliminate all rows where NaN values are present
    df = df.dropna()
    usersMax = np.amax(users)
    # Get names of indexes for which column K is smaller than 98% of the max user
    indexNames_K = df[df['K'] <= 1.05*usersMax].index
    # Delete these row indexes from dataFrame
    df.drop(indexNames_K, inplace=True)
    # Get names of indexes for which column r is smaller than zero
    indexNames_r = df[df['r'] <= 0].index
    # Delete these row indexes from dataFrame
    df.drop(indexNames_r, inplace=True)
    # Get names of indexes for which column r is smaller or equal to zero
    indexNames_rSquared = df[df['R Squared'] <= 0.2].index
    # Delete these row indexes from dataFrame
    df.drop(indexNames_rSquared, inplace=True)
    # Get names of indexes for which column p0 is smaller that numbers very close to zero
    indexNames_p0 = df[df['p0'] < 5.775167e-41].index
    # Delete these row indexes from dataFrame
    df.drop(indexNames_p0, inplace=True)
    df_sorted = df.sort_values(by=['K'], ascending=True)
    # Resetting the indexes
    df_sorted= df_sorted.reset_index(drop=True)
    return df_sorted

# Second Function to clean the parameters dataframe (the dataframe containing parameters in function of the data ignored)
# Called only in case no good scenario is found. Here only the absurd scenarios are eliminated
# Rows are deleted if: value = Nan; K<= 0.9*userMax ; K> 5*usermax r<0 ; p0 <= 0
def parameters_dataframe_cleaning_minimal(df, users):
    # Eliminate all rows where NaN values are present
    df = df.dropna()
    usersMax = np.amax(users)
    # Get names of indexes for which column K is smaller than 98% of the max user
    indexNames_K = df[df['K'] <= 0.8*usersMax].index
    # Delete these row indexes from dataFrame
    df.drop(indexNames_K, inplace=True)
    # Get names of indexes for which column K is smaller than 98% of the max user
    indexNames_K_max = df[df['K'] > 5 * usersMax].index
    # Delete these row indexes from dataFrame
    df.drop(indexNames_K_max, inplace=True)
    # Get names of indexes for which column r is smaller than zero
    indexNames_r = df[df['r'] <= 0].index
    # Delete these row indexes from dataFrame
    df.drop(indexNames_r, inplace=True)
    # Get names of indexes for which column r is smaller or equal to zero
    indexNames_rSquared = df[df['R Squared'] <= 0.001].index
    # Delete these row indexes from dataFrame
    #df.drop(indexNames_rSquared, inplace=True)
    # Get names of indexes for which column p0 is smaller that numbers very close to zero
    indexNames_p0 = df[df['p0'] < 5.775167e-41].index
    # Delete these row indexes from dataFrame
    df.drop(indexNames_p0, inplace=True)
    df_sorted = df.sort_values(by=['K'], ascending=True)
    # Resetting the indexes
    df_sorted = df_sorted.reset_index(drop=True)
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
    try:
        t = 1/r*math.log(pt*(k-p0)/(p0*(k-pt)))
    except ValueError:
        print("Invalid input values. Ensure (pt * (k - p0)) / (p0 * (k - pt)) is greater than 0.")
        return 50.0
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

# Cashflow is calculated same way as above but by including a growth rate for the ARPU over time
def net_present_value_arpu_growth(k, r, p0, arpu, arpu_growth, profitmargin, discount_rate, years):
    current_year = datetime.now().year
    t = np.linspace(1.0, years, years) + current_year - 1970 # definition of the time "cashflow size" in future years
    cashflow = np.array(years)
    arpu_over_time = [arpu * (1 + arpu_growth) ** year for year in range(years)]
    cashflow = logisticfunction(k, r, p0, t) * arpu_over_time * profitmargin
    discounted_cashflow = npf.npv(discount_rate, cashflow)
    users_over_time = logisticfunction(k, r, p0, t)

    return discounted_cashflow


# Calculating the arpu needed to reach a certain valuation
def arpu_for_valuation(k, r, p0, profitmargin, discount_rate, years, valuation):
    x = Symbol('x')
    function_to_solve = solve(net_present_value(k, r, p0, x, profitmargin, discount_rate, years) - valuation, x)
    arpu = float(function_to_solve[0])
    return arpu

# Calculating the profit margin needed to reach a certain valuation
def profit_margin_for_valuation(k, r, p0, arpu, arpu_growth, discount_rate, years, noa_assets, valuation):
    x = Symbol('x')
    function_to_solve = solve(net_present_value_arpu_growth(k, r, p0, arpu, arpu_growth, x, discount_rate, years) + noa_assets - valuation, x)
    profit_margin = float(function_to_solve[0])
    return profit_margin

# Calculate the minimum time you can go back in time, given a certain dataset with an array of dates (dates)
# One can go back only until 4 data are left to be analyzed
def date_minimum_history(dates):
    date_minimum = dates[4] + 0.5
    return date_minimum

# Get only arrays data before a given certain t_time
def get_earlier_dates(dates, t_time):
    earlier_dates = []
    for date in dates:
        if date < t_time:
            earlier_dates.append(date)
    return earlier_dates

def polynomial_approximation(dates, users, n_polynome):
    rd = discrete_growth_rate(users, dates)
    userinterval = discrete_user_interval(users)
    parameters = np.polyfit(userinterval, rd, n_polynome, rcond=None, full=False)
    return parameters

def log_approximation(dates, users):
    rd = discrete_growth_rate(users, dates)
    userinterval = discrete_user_interval(users)
    parameters = np.polyfit(np.log(userinterval), rd, 1, rcond=None, full=False)
    return parameters

# Function to smoothen the data with a given window size
def moving_average_smoothing(dates, users, window_size):
    dates_series = pd.Series(dates)
    users_series = pd.Series(users)
    smoothed_dates = dates_series.rolling(window_size, min_periods=1).mean()
    smoothed_users = users_series.rolling(window_size, min_periods=1).mean()
    smoothed_dates_array = smoothed_dates.values
    smoothed_users_array = smoothed_users.values
    return smoothed_dates_array, smoothed_users_array

# Function calculating r, p0, given a certain k. In the function, k is added to the dataset and the dataset in then
# centered around (k, 0) to perform an intercepted regression.
def logistic_parameters_given_K(dates, users, k):
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
    intercept = coefficient*(user_interval[0])  # The final intercept is found by computing the function for x=K
    r_growth_rate = float(intercept)
    def p0_function(usersp, datesp, k, r):
        p0 = usersp * k / (-usersp * (np.exp(r * datesp) - 1) + k * np.exp(r * datesp))
        return p0

    p0_all_func = np.vectorize(p0_function)
    p0_all = p0_all_func(users, dates, k, r_growth_rate)
    p0_initialusers = np.mean(p0_all)

    #Rsquare calculation
    observed_data_log = discretegrowthrate
    approximated_values_log = -r_growth_rate/k*user_interval+r_growth_rate
    # Calculate R-squared
    r_squared = rsquare_calculation(observed_data_log, approximated_values_log)
    return r_growth_rate, p0_initialusers, r_squared,

# This function serves to define how many data to delete to get the best log approximation of the dataset. We here
# simply evaluate r^2 by deleting data one by one
def parameters_dataframe_given_klog(dates, users):
    maximum_data_ignored = 0.1  # Up to 10% of the data can be ignored for the log approximation
    n_data_ignored = int(round(len(dates)*maximum_data_ignored))
    n_data_ignored = 1  # Here we don't iterate
    dataframe = np.zeros((n_data_ignored, 6))
    # Calculation of K, r & p0 and its related RSquare for each data ignored
    for i in range(n_data_ignored):
        dates_rsquare = dates[i:len(dates)]
        users_rsquare = users[i:len(dates)]
        logfit = log_approximation(dates_rsquare, users_rsquare)
        rd = discrete_growth_rate(users_rsquare, dates_rsquare)
        userinterval = discrete_user_interval(users_rsquare)
        k_log = np.exp(-logfit[1] / logfit[0])
        r_log, p0_log, r_squared = logistic_parameters_given_K(dates_rsquare, users_rsquare, k_log)
        r_squared_log = rsquare_calculation(rd, np.log(userinterval))
        rootmeansquare = rmsd(users_rsquare, logisticfunction(k_log,r_log,p0_log,dates_rsquare))

        dataframe[i, 0] = i  # Data ignored column
        dataframe[i, 1] = k_log  # K (carrying capacity) column
        dataframe[i, 2] = r_log  # r (growth rate) column
        dataframe[i, 3] = p0_log  # p0 (initial population) column
        dataframe[i, 4] = r_squared_log  # r squared column
        dataframe[i, 5] = rootmeansquare  # Root Mean Square Deviation column
    df = pd.DataFrame(dataframe, columns=['Data Ignored', 'K', 'r', 'p0', 'R Squared', 'RMSD'])
    df['Method'] = 'K set'
    return df

# Function providing the date of the end of the previous quarter (as of now)
def previous_quarter_calculation():
    # Calculate the end date of the previous quarter
    # Get the current date
    current_date = datetime.now()
    if current_date.month in [1, 2, 3]:
        # If the current quarter is Q1, the previous quarter is Q4 of the previous year
        end_date_prev_quarter = datetime(current_date.year - 1, 12, 31)
        year_percentage = 1/4
    else:
        # Otherwise, calculate the last day of the previous quarter
        previous_quarter = (current_date.month - 1) // 3
        end_date_prev_quarter = datetime(current_date.year, previous_quarter * 3, 1)
        year_percentage = previous_quarter/4  # Defines the percentage of the year that has passed. Because
                                                # the revenue in the report is from the beginning of the year
    end_date_formatted = end_date_prev_quarter.strftime('%Y-%m-%d')
    return end_date_prev_quarter

# Function finding the closest date in an array that is before the given date
def find_closest_date(given_date, date_array):
    # Convert the given_date string to a datetime object
    given_date = datetime.strptime(given_date, "%Y-%m-%d")

    # Convert each date in date_array to datetime objects
    date_array = [datetime.strptime(date, "%Y-%m-%d") for date in date_array]

    # Find the index of the date in date_array that is closest to given_date
    closest_date_index = min(range(len(date_array)), key=lambda i: abs(date_array[i] - given_date))

    return closest_date_index


# Function to provide the minimum and maximum date of the datepicker for a given dataset as a pandas dataframe and
# formats the dataframe as an output
def datepicker_limit(dataset_df):
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

# Function defining the color and the text of the hype meter indicator, depending on the size of the hype compared to
# the total market cap. The color changes the outline of the badge while the text changes its value
def hype_meter_indicator_values(hype_ratio):
    if hype_ratio <= 0: # if hype ratio is smaller than 10%
        indicator_color = "teal"
        indicator_text = "Undervalued!"
    elif hype_ratio < 0.1: # if hype ratio is smaller than 10%
        indicator_color = "orange"
        indicator_text = "Marginally Hyped"
    elif hype_ratio < 0.15: # if hype ratio is smaller than 15%
        indicator_color = "orange"
        indicator_text = "Moderately Hyped"
    elif hype_ratio < 0.2: # if hype ratio is smaller than 20%
        indicator_color = "orange"
        indicator_text = "Strongly Hyped"
    else: # if hype ratio is higher than 20%
        indicator_color = "red"
        indicator_text = "Super hyped!"
    return indicator_color, indicator_text

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            print("CSV uploaded")
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            print("CSV successfully read")
        elif 'xls' in filename:
            print("XLS uploaded")
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            print("XLS successfully read")
        # Remove empty rows
        df.dropna(axis=0, how='all', inplace=True)
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.fromtimestamp(date)),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

    ])

def parse_contents_df(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            print("CSV uploaded")
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            print("CSV successfully read")
        elif 'xls' in filename:
            print("XLS uploaded")
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            print("XLS successfully read")
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
        # Remove empty rows
        df.dropna(axis=0, how='all', inplace=True)

    return df


# Improved function for parsing file contents
def parse_file_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        if 'csv' in filename:
            print("CSV uploaded")
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            print("CSV successfully read")
        elif 'xls' in filename:
            print("XLS uploaded")
            df = pd.read_excel(io.BytesIO(decoded))
            print("XLS successfully read")
        else:
            raise ValueError("Unsupported file format")

        # Remove empty rows
        df.dropna(axis=0, how='all', inplace=True)

    except Exception as e:
        print(e)
        return None

    return df

# Improved function to generate DataFrame from contents
def parse_file_contents_df(contents, filename, date):
    df = parse_file_contents(contents, filename)
    return df

# Generate an icon per industry
def get_industry_icon(industry: str) -> str:
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

# Verify JWT (simplified, replace with proper signature verification in production)
def verify_token(token):
    try:
        claims = jwt.decode(token, options={"verify_signature": False})
        return claims
    except Exception:
        return None

# Replace the infinite values
def replace_inf_with_previous_2(df, column):
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

    # Find indices where values are infinite
    inf_mask = np.isinf(df_copy[column])

    # Get indices of infinite values
    inf_indices = df_copy[inf_mask].index

    # Replace each infinite value with value from 2 rows back
    for idx in inf_indices:
        idx_position = df_copy.index.get_loc(idx)
        if idx_position >= 2:  # Check if there are at least 2 rows before
            previous_idx = df_copy.index[idx_position - 2]
            df_copy.loc[idx, column] = df_copy.loc[previous_idx, column]
        # If less than 2 rows back, leave as inf or handle differently

    return df_copy


