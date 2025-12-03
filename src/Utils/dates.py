from datetime import datetime, timedelta

import pandas as pd

YEAR_OFFSET = 1970  # Offset taken to define the year zero


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


def date_formatting_from_string(date_string):
    """
    This function transforms a date string of format 2023-11-01T11:29:13.362885 to a number of format 2023.83
    :param date_string:
    :return:
    """
    # Parse the date string to get the year, month, and day
    date_obj = datetime.strptime(date_string[:10], "%Y-%m-%d")
    year = date_obj.year
    month = date_obj.month
    day = date_obj.day

    # Calculate the fraction of the year
    fraction_of_year = (month - 1) / 12 + (day - 1) / 365

    # Combine the year and fraction of the year
    return year + fraction_of_year


def string_formatting_to_date(decimal_year):
    """
    This function transforms a date string of format 2023-11-01T11:29:13.362885 to a number of format 2023.83
    :param decimal_year:
    :return:
    """
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


def transform_date_format(input_date):
    """
    The following function transforms a date of format 2016.99 to a date 2016-12-31
    :param input_date:
    :return:
    """
    # Extract the year and fraction part from the float
    year = int(input_date)
    fraction = input_date - year

    # Calculate the day of the year based on the fraction
    total_days = int(fraction * 365)

    # Create a datetime object with the calculated year and day of the year
    transformed_date = datetime(year, 1, 1) + timedelta(days=total_days)

    return transformed_date.strftime("%Y-%m-%d")


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


def find_closest_date(given_date, date_array):
    """
    Function finding the closest date in an array that is before the given date
    :param given_date:
    :param date_array:
    :return:
    """
    # Convert the given_date string to a datetime object
    given_date = datetime.strptime(given_date, "%Y-%m-%d")

    # Convert each date in date_array to datetime objects
    date_array = [datetime.strptime(date, "%Y-%m-%d") for date in date_array]

    # Find the index of the date in date_array that is closest to given_date
    closest_date_index = min(range(len(date_array)), key=lambda i: abs(date_array[i] - given_date))

    return closest_date_index


def previous_quarter_calculation():
    """
    Function providing the date of the end of the previous quarter (as of now)
    :return:
    """
    # Calculate the end date of the previous quarter
    # Get the current date
    current_date = datetime.now()
    if current_date.month in [1, 2, 3]:
        # If the current quarter is Q1, the previous quarter is Q4 of the previous year
        end_date_prev_quarter = datetime(current_date.year - 1, 12, 31)
        year_percentage = 1 / 4
    else:
        # Otherwise, calculate the last day of the previous quarter
        previous_quarter = (current_date.month - 1) // 3
        end_date_prev_quarter = datetime(current_date.year, previous_quarter * 3, 1)
        year_percentage = previous_quarter / 4  # Defines the percentage of the year that has passed. Because
        # the revenue in the report is from the beginning of the year
    end_date_formatted = end_date_prev_quarter.strftime('%Y-%m-%d')
    return end_date_prev_quarter