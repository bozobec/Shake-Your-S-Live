import math

import numpy as np


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