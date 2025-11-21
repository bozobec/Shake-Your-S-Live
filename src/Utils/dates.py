import pandas as pd


def date_formatting(dates):
    """
    This function takes a panda series date of format YYYY-MM-DD and returns a decimal year, with year 0 in 1970
    :param dates:
    :return:
    """
    def date_to_decimal_year(date_obj):
        years_diff = date_obj.year - 1970
        year_fraction = (date_obj.month - 1 + (date_obj.day - 1) / 30.0) / 12.0
        decimal_year = years_diff + year_fraction
        return decimal_year

    date_objects = pd.to_datetime(dates)
    decimal_years = date_objects.apply(date_to_decimal_year)
    return decimal_years


def date_minimum_history(dates):
    """
    Calculate the minimum time you can go back in time, given a certain dataset with an array of dates (dates)
    One can go back only until 4 data are left to be analyzed
    :param dates:
    :return:
    """
    date_minimum = dates[4] + 0.5
    return date_minimum


def get_earlier_dates(dates, t_time):
    """
    Get only arrays data before a given certain t_time
    :param dates:
    :param t_time:
    :return:
    """
    earlier_dates = []
    for date in dates:
        if date < t_time:
            earlier_dates.append(date)
    return earlier_dates