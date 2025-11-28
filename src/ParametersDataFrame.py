import numpy as np
import pandas as pd

from src.Utils.mathematics import moving_average_smoothing, logistic_function_approximation, rsquare_calculation, rmsd, \
    logisticfunction, log_approximation, logistic_parameters_given_K
from src.analysis import discrete_growth_rate, discrete_user_interval
from src.Utils.RastLogger import get_default_logger

logger = get_default_logger()


def parameters_dataframe(dates, users):
    """
    Calculation of the parameters and RSquare, mapped to the amount of data ignored
    :param dates:
    :param users:
    :return:
    """
    number_moving_average = 4  # Number of moving averages allowed
    n_data_ignored = len(dates) - 3  # Number of data until which to be ignored
    dataframe = np.zeros((n_data_ignored * number_moving_average, 9))
    # Calculation of K, r & p0 and its related RSquare for each data ignored
    for i in range(0, number_moving_average):
        moving_average = i + 1
        if moving_average == 1:
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
                    logger.info("Parameters could not be calculated for: ", j, " data ignored")
                if k == 0:
                    logger.info("Issue when ignoring", j, "data")
                    raise RuntimeError("Skipping ignoring", j, " data")
                observed_values_df = rd
                approximated_values_df = -r / k * userinterval + r
                r_squared = rsquare_calculation(observed_values_df, approximated_values_df)
                try:
                    rootmeansquare = rmsd(users_rsquare, logisticfunction(k, r, p0, dates_rsquare))
                except:
                    rootmeansquare = 0
                    logger.info("rmsd could not be calculated when ignoring:", n_data_ignored, " number of data points")
                logfit = log_approximation(dates_rsquare, users_rsquare)

                approximated_values_log = rsquare_calculation(observed_values_df,
                                                              np.polyval(logfit, np.log(userinterval)))
                diff_lin_log = approximated_values_log - r_squared

                dataframe[j + i * n_data_ignored, 0] = j  # Data ignored column
                dataframe[j + i * n_data_ignored, 1] = k  # K (carrying capacity) column
                dataframe[j + i * n_data_ignored, 2] = r  # r (growth rate) column
                dataframe[j + i * n_data_ignored, 3] = p0  # p0 (initial population) column
                dataframe[j + i * n_data_ignored, 4] = r_squared  # r squared column
                dataframe[j + i * n_data_ignored, 5] = rootmeansquare / (
                        (users[0] + users[-1]) / 2)  # Root Mean Square Deviation column
                dataframe[
                    j + i * n_data_ignored, 6] = approximated_values_log  # Root Mean Square Deviation of the log approximation column
                dataframe[j + i * n_data_ignored, 7] = diff_lin_log  # Difference between the linear R^2 and the log R^2
                dataframe[
                    j + i * n_data_ignored, 8] = moving_average  # Difference between the linear R^2 and the log R^2
            except RuntimeError as e:
                dataframe[j + i * n_data_ignored, 0] = 0  # Data ignored column
                dataframe[j + i * n_data_ignored, 1] = 1  # K (carrying capacity) column
                dataframe[j + i * n_data_ignored, 2] = 0  # r (growth rate) column
                dataframe[j + i * n_data_ignored, 3] = users[-1]  # p0 (initial population) column
                dataframe[j + i * n_data_ignored, 4] = 0  # r squared column
                dataframe[j + i * n_data_ignored, 5] = 0  # Root Mean Square Deviation column
                dataframe[j + i * n_data_ignored, 6] = 0  # Root Mean Square Deviation of the log approximation column
                dataframe[j + i * n_data_ignored, 7] = 0  # Difference between the linear R^2 and the log R^2
                dataframe[j + i * n_data_ignored, 8] = 1  # Moving average
    pd.set_option('display.max_rows', None)
    df = pd.DataFrame(dataframe,
                      columns=['Data Ignored', 'K', 'r', 'p0', 'R Squared', 'RMSD', 'R Squared LOG', 'Lin/Log Diff',
                               'Moving Average'])
    df['Method'] = 'Linear regression'
    return df


def parameters_dataframe_cleaning(df, users):
    """
    Function to clean the parameters dataframe (the dataframe containing parameters in function of the data ignored)
    Rows are deleted if: value = Nan; K<= 0.9*userMax ; r<0 ; R Squared < 0.2 ; p0 <= 0
    :param df:
    :param users:
    :return:
    """
    # Eliminate all rows where NaN values are present
    df = df.dropna()
    usersMax = np.amax(users)
    # Get names of indexes for which column K is smaller than 98% of the max user
    indexNames_K = df[df['K'] <= 1.05 * usersMax].index
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
    df_sorted = df_sorted.reset_index(drop=True)
    return df_sorted


def parameters_dataframe_cleaning_minimal(df, users):
    """
    Second Function to clean the parameters dataframe (the dataframe containing parameters in function of
    the data ignored)
    Called only in case no good scenario is found. Here only the absurd scenarios are eliminated
    Rows are deleted if: value = Nan; K<= 0.9*userMax ; K> 5*usermax r<0 ; p0 <= 0
    :param df:
    :param users:
    :return:
    """
    # Eliminate all rows where NaN values are present
    df = df.dropna()
    usersMax = np.amax(users)
    # Get names of indexes for which column K is smaller than 98% of the max user
    indexNames_K = df[df['K'] <= 0.8 * usersMax].index
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
    # df.drop(indexNames_rSquared, inplace=True)
    # Get names of indexes for which column p0 is smaller that numbers very close to zero
    indexNames_p0 = df[df['p0'] < 5.775167e-41].index
    # Delete these row indexes from dataFrame
    df.drop(indexNames_p0, inplace=True)
    df_sorted = df.sort_values(by=['K'], ascending=True)
    # Resetting the indexes
    df_sorted = df_sorted.reset_index(drop=True)
    return df_sorted


def parameters_dataframe_given_klog(dates, users):
    """
    This function serves to define how many data to delete to get the best log approximation of the dataset. We here
    simply evaluate r^2 by deleting data one by one
    :param dates:
    :param users:
    :return:
    """
    maximum_data_ignored = 0.1  # Up to 10% of the data can be ignored for the log approximation
    n_data_ignored = int(round(len(dates) * maximum_data_ignored))
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
        rootmeansquare = rmsd(users_rsquare, logisticfunction(k_log, r_log, p0_log, dates_rsquare))

        dataframe[i, 0] = i  # Data ignored column
        dataframe[i, 1] = k_log  # K (carrying capacity) column
        dataframe[i, 2] = r_log  # r (growth rate) column
        dataframe[i, 3] = p0_log  # p0 (initial population) column
        dataframe[i, 4] = r_squared_log  # r squared column
        dataframe[i, 5] = rootmeansquare  # Root Mean Square Deviation column
    df = pd.DataFrame(dataframe, columns=['Data Ignored', 'K', 'r', 'p0', 'R Squared', 'RMSD'])
    df['Method'] = 'K set'
    return df