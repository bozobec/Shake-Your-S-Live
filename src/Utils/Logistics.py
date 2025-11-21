import math

import numpy as np
from scipy.optimize import curve_fit
from sklearn import linear_model

from src.analysis import discrete_growth_rate, discrete_user_interval


def logisticfunction(k, r, p0, dates):
    """
    Logistic function, return Y given the parameters k, r and p0
    :param k:
    :param r:
    :param p0:
    :param dates:
    :return:
    """
    # y = (k*p0*np.exp(r*dates))/(k+p0*(np.exp(r*dates)-1))  OLD METHOD
    y = np.zeros(len(dates))
    for i in range(len(dates)):
        y[i] = (k * p0 * np.exp(r * dates[i])) / (k + p0 * (np.exp(r * dates[i]) - 1))
    return y


def logfuncgeneric(qinf, alpha, thalf, dates):
    """
    Q(t) = Qinf/(1 + exp(-alpha*(t-thalf)))
    This function is an alternative to (K.*P0.*exp(r.*t))./(K+P0.*(exp(r.*t)-1))
    Where K=Qinf, r=alpha, p0=Q(0)

    :param qinf:
    :param alpha:
    :param thalf:
    :param dates:
    :return:
    """
    y = qinf / (1 + math.exp(-alpha * (dates - thalf)))
    return y


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

    # Nested function to be created to calculate different P0, initial population
    def p0_function(usersp, datesp, k, r):
        p0 = usersp * k / (-usersp * (np.exp(r * datesp) - 1) + k * np.exp(r * datesp))
        return p0

    p0_all_func = np.vectorize(p0_function)
    p0_all = p0_all_func(users, dates, k_carrying_capacity, r_growth_rate)
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
