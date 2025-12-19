from datetime import datetime

import requests
from urllib.parse import urljoin

from src.Utils.RastLogger import get_default_logger

logger = get_default_logger()


class FinhubAPI:
    _instance = None
    _base_url = "https://finnhub.io/api/v1/"
    _auth_token = "clmplq1r01qjj8i8s6ugclmplq1r01qjj8i8s6v0"  # Free token visible here: https://finnhub.io/dashboard
    _marketcap = {}
    _previous_quarter_revenue = {}
    _profit_margin = {}

    def __new__(cls, *args, **kwargs):
        """
        This function makes sure that there is only one instance of this class, no matter where you call it in code
        :param args:
        :param kwargs:
        """
        if cls._instance is None:
            cls._instance = super(FinhubAPI, cls).__new__(cls)

        return cls._instance

    @classmethod
    def _get_marketcap(cls, symbol_input) -> float:
        """
        API Fetching the market cap of the company in $mio.

        Can raise Exception. Should be handled by caller
        :param symbol_input:
        :return:
        """
        # ToDo: Check if question mark is needed
        url = urljoin(cls._base_url, "stock/profile2?") + '?'

        symbol = symbol_input
        response = requests.get(url, params={'symbol': symbol, 'token': cls._auth_token})
        data = response.json()
        currency = data.get("currency")
        market_cap = data.get("marketCapitalization")
        if currency == "JPY":
            market_cap = 0.0064 * market_cap  # exchange rate on 16 Jan 25, to be updated regularly
        return market_cap

    @classmethod
    def get_marketcap(cls, symbol_input) -> float:
        """
        Check if current marketcap has already been fetched, if so returns the cached value, else will go and fetch it.
        :param symbol_input:
        :return:
        """

        if symbol_input not in cls._marketcap.keys():
            logger.info(f"Current marketcap for {symbol_input} not yet fetched. Starting fetch")

            try:
                cls._marketcap[symbol_input] = cls._get_marketcap(symbol_input)
                logger.info(f"Current marketcap for {symbol_input} fetched successfully")

            except:
                logger.exception(f"Exception while fetching marketcap for {symbol_input}: ")

        else:
            logger.info(f"Current marketcap for {symbol_input} already fetched. Using cached data")

        return cls._marketcap.get(symbol_input)

    @classmethod
    def _get_previous_quarter_revenue(cls, symbol_input):
        # ToDo: Talk about this: What are the default values? What should be provided if exceptions are raised?
        """
        API Fetching the revenue of the last quarter.

        Can raise Exceptions should be handled by caller
        :param symbol_input:
        :return:
        """

        url = urljoin(cls._base_url, "stock/financials-reported?") + '?'
        symbol = symbol_input  # Symbol of the stock
        frequency = "quarterly"  # Frequency of the report
        # Get the current date
        current_date = datetime.now()

        # Calculate the end date of the previous quarter
        if current_date.month in [1, 2, 3]:
            # If the current quarter is Q1, the previous quarter is Q4 of the previous year
            year_percentage = 1 / 4
        else:
            # Otherwise, calculate the last day of the previous quarter
            previous_quarter = (current_date.month - 1) // 3
            year_percentage = previous_quarter / 4  # Defines the percentage of the year that has passed. Because
            # the revenue in the report is from the beginning of the year

        # Response
        response = requests.get(url, params={'symbol': symbol,
                                             'freq': frequency,
                                             'token': cls._auth_token})
        data = response.json()
        try:
            total_assets = next(
                item['value'] for item in data['data'][0]['report']['bs'] if item['label'] == 'Total current assets')
        except:
            total_assets = 0.0
            logger.exception("Error fetching total assets")
        try:
            revenue = next(item['value'] for item in data['data'][0]['report']['ic'] if item['label'] == 'Revenue'
                           or item['label'] == 'Revenues' or item['label'] == 'Revenue:')
        except:
            revenue = next(item['value'] for item in data['data'][0]['report']['ic'] if item['label'] == 'Revenues')

        logger.debug("Total Assets: ", str(symbol))
        logger.debug(total_assets)
        logger.debug(data)

        return revenue / year_percentage, total_assets

    @classmethod
    def get_previous_quarter_revenue(cls, symbol_input):
        """
        Checks if quarter data has been cached, if so will return it,  if not goes and fetches it.
        :param symbol_input:
        :return:
        """

        if symbol_input not in cls._previous_quarter_revenue.keys():
            logger.info(f"Previous Quarter Revenue for {symbol_input} not yet fetched. Starting fetch")

            try:
                cls._previous_quarter_revenue[symbol_input] = cls._get_previous_quarter_revenue(symbol_input)
                logger.info(f"Previous Quarter Revenue for {symbol_input} fetched successfully")

            except:
                logger.exception(f"Exception while fetching Previous Quarter Revenue for {symbol_input}: ")

        else:
            logger.info(f"Previous Quarter Revenue for {symbol_input} already fetched. Using cached data")

        return cls._previous_quarter_revenue.get(symbol_input, (0.0, 0.0))

    @classmethod
    def _get_profit_margin(cls, symbol_input):
        """
        API Fetching the profit margin of the past year

        Can raise Exceptions should be handled by caller.
        :param symbol_input:
        :return:
        """

        url = urljoin(cls._base_url, "stock/metric?") + '?'
        symbol = symbol_input  # Symbol of the stock
        metric = "netProfitMarginAnnual"  # Frequency of the report

        # Response
        response = requests.get(url, params={'symbol': symbol, 'metric': metric, 'token': cls._auth_token})
        data = response.json()
        profit_margin = data['metric']['netProfitMarginAnnual']
        return profit_margin

    @classmethod
    def get_profit_margin(cls, symbol_input):
        """
        Checks if profit margin for company is already cached and returns it if so. If not will go and fetch it.
        :param symbol_input:
        :return:
        """

        if symbol_input not in cls._profit_margin.keys():
            logger.info(f"Profit Margin for {symbol_input} not yet fetched. Starting fetch")

            try:
                cls._profit_margin[symbol_input] = cls._get_profit_margin(symbol_input)
                logger.info(f"Profit Margin for {symbol_input} fetched successfully")

            except:
                logger.exception(f"Exception while fetching Profit Margin for {symbol_input}: ")

        else:
            logger.info(f"Profit Margin for {symbol_input} already fetched. Using cached data")

        return cls._profit_margin.get(symbol_input, 0)


if __name__ == '__main__':
    finhub_api = FinhubAPI()
    finhub_api2 = FinhubAPI()

    logger.info(f"{ finhub_api is finhub_api2 = }")

    # ToDo: Handle this error more gracefully - NFLX
    netflix_isin = 'US64110L1061'

    finhub_api.get_marketcap(netflix_isin)
    logger.info(f'{finhub_api.get_marketcap(netflix_isin) = }')

    finhub_api.get_profit_margin(netflix_isin)
    logger.info(f'{finhub_api.get_profit_margin(netflix_isin) = }')

    finhub_api.get_previous_quarter_revenue(netflix_isin)
    logger.info(f'{finhub_api.get_previous_quarter_revenue(netflix_isin) = }')
