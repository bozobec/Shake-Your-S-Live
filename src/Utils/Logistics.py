import math

import numpy as np

from src.Utils.RastLogger import get_default_logger

logger = get_default_logger()


def logisticfunction(k, r, p0, dates):
    """
    Logistic function, return Y given the parameters k, r and p0
    :param k:
    :param r:
    :param p0:
    :param dates:
    :return:
    """
    dates = np.asarray(dates, dtype=float)
    exp_r_dates = np.exp(r * dates)
    denominator = k + p0 * (exp_r_dates - 1)
    with np.errstate(divide='ignore', invalid='ignore'):
        y = np.where(denominator != 0, (k * p0 * exp_r_dates) / denominator, 0.0)
    if np.any(np.isnan(y) | np.isinf(y)):
        y = np.nan_to_num(y, nan=0.0, posinf=0.0, neginf=0.0)
        logger.info("Log function could not be computed with the following parameters")
        logger.info(f"k = {k}; r = {r}; p0 = {p0}")
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


