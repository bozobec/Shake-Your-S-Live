import os
import time
from collections import defaultdict

import pandas as pd
import requests
from dotenv import load_dotenv

from src.Utils.RastLogger import get_default_logger

logger = get_default_logger()

load_dotenv()
logger.info(f"Airtable key loaded: {bool(os.getenv('AIRTABLE_API_KEY'))}")

# ToDo: make pretty urls

# Cache TTL constants (seconds)
_LABELS_TTL = 3600        # 1 hour — label list changes rarely
_DATA_TTL = 300           # 5 minutes — company time-series
_HYPED_TTL = 300          # 5 minutes — ranking/company metadata


class AirTableAPI:
    _instance = None
    AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
    _labels = None
    _labels_ts = 0.0                  # timestamp of last fetch
    _data = {}
    _data_ts = {}                     # per-company fetch timestamps
    _hyped_companies = {}
    _hyped_companies_ts = {}          # per-key fetch timestamps
    _hyped_companies_data = None
    _hyped_companies_data_ts = 0.0    # timestamp of last fetch

    def __new__(cls, *args, **kwargs):
        """
        This function makes sure that there is only one instance of this class, no matter where you call it in code
        :param args:
        :param kwargs:
        """
        if cls._instance is None:
            cls._instance = super(AirTableAPI, cls).__new__(cls)

        return cls._instance

    @classmethod
    def _get_airtable_labels(cls):
        """
        This function fetches all the unique categories in the airtable database
        :return:
        """
        url = "https://api.airtable.com/v0/appm3ffcu38jyqhi3/tbl7LiTDpXk9DeRUB?fields%5B%5D=Company&fields%5B%5D=Category&fields%5B%5D=Symbol"
        headers = {
            "Authorization": f"Bearer {cls.AIRTABLE_API_KEY}"
        }

        # Initialize variables
        offset = None
        all_records = []

        # Loop to fetch all records with pagination
        while True:
            # Prepare parameters, including the offset if it's present
            params = {}
            if offset:
                params['offset'] = offset

            # Make the request to Airtable
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Ensure it raises an error for bad requests

            # Parse the response JSON
            data = response.json()
            records = data.get('records', [])
            all_records.extend(records)  # Append current batch of records

            # Check for an offset to continue fetching if necessary
            offset = data.get('offset')
            if not offset:
                break  # Exit the loop if there is no more data to fetch

        # Format the data into a DataFrame including only the Company and Category
        formatted_data = [
            {
                'Company': record['fields'].get('Company', ''),
                'Category': record['fields'].get('Category', ''),
                'Symbol': record['fields'].get('Symbol', '')
            }
            for record in all_records
        ]
        df = pd.DataFrame(formatted_data)  # Create a DataFrame from all records

        # Keep only unique companies
        df.drop_duplicates(subset='Company', inplace=True)

        # Sort DataFrame by Category and Company
        df.sort_values(by=['Category', 'Company'], inplace=True)

        # Iterate through the sorted DataFrame to create label_list
        grouped = defaultdict(list)
        for _, row in df.iterrows():
            grouped[row['Category']].append({
                "value": row['Company'],
                "label": f"{row['Company']} ({row['Symbol']})",
                "disabled": False
            })

        # Return the label list
        return [{"group": g, "items": items} for g, items in grouped.items()]

    @classmethod
    def get_labels(cls):
        """
        Checks if the labels have already been downloaded and returns it. If not, it will go and fetch it.
        Re-fetches when the cached value is older than _LABELS_TTL seconds.
        :return:
        """
        if cls._labels is None or (time.time() - cls._labels_ts) > _LABELS_TTL:
            logger.info("Dataset labels not yet fetched or cache expired. Starting fetch")
            try:
                cls._labels = cls._get_airtable_labels()
                cls._labels_ts = time.time()
                logger.info("Label fetching successful.")
            except:
                logger.exception("Exception while fetching AirTable dataset labels")
        else:
            logger.info("Dataset labels already fetched. Using cached data")

        return cls._labels

    @classmethod
    def _get_airtable_data(cls, filter: str) -> pd.DataFrame:
        """
        Gets company data from Airtable using the provided company string. Return a pandas DataFrame.

        Might raise exception. Should be handled by calling method
        :param filter: string of the company
        :return:
        """

        url = "https://api.airtable.com/v0/appm3ffcu38jyqhi3/tbl7LiTDpXk9DeRUB?fields%5B%5D=Company" \
              "&fields%5B%5D=Date" \
              "&fields%5B%5D=Users" \
              "&fields%5B%5D=Unit" \
              "&fields%5B%5D=Source" \
              "&fields%5B%5D=Symbol" \
              "&fields%5B%5D=Quarterly_Revenue_Mio$" \
              "&fields%5B%5D=Net_Profit_Margin" \
              "&fields%5B%5D=Market_Cap" \
              "&fields%5B%5D=Research_And_Development" \
              "&filterByFormula=Company%3D%22{}%22" \
              "&sort%5B0%5D%5Bfield%5D=Date" \
              "&sort%5B0%5D%5Bdirection%5D=asc".format(filter)
        headers = {
            "Authorization": f"Bearer {cls.AIRTABLE_API_KEY}"
        }
        response = requests.get(url, headers=headers)  # Call the Airtable data with the specified filter
        data = response.json()  # Transforms it into a dictionary

        # Format the data into a dataframe including only the Date and the Users
        records = data['records']
        formatted_data = []
        for record in records:
            formatted_data.append({
                'Date': record['fields']['Date'],
                'Users': record['fields']['Users'],
                'Unit': record['fields']['Unit'],
                'Source': record['fields']['Source'],
                'Symbol': record['fields']['Symbol'],
                'Revenue': record['fields']['Quarterly_Revenue_Mio$'],
                'Profit Margin': record['fields']['Net_Profit_Margin'],
                'Market Cap': record['fields']['Market_Cap'],
                'Research_And_Development': record['fields']['Research_And_Development'],
            })
        df = pd.DataFrame(formatted_data)  # Create a DataFrame from the sample data
        return df

    @classmethod
    def get_data(cls, company: str) -> pd.DataFrame:
        """
        Check if company data has already been downloaded. If so returns it, if not it will go and fetch it from
        AirTable. Re-fetches when the cached value is older than _DATA_TTL seconds.
        :param company: string of the company
        :return: pandas DataFrame of the company data.
        """
        cache_expired = (time.time() - cls._data_ts.get(company, 0.0)) > _DATA_TTL
        if company not in cls._data or cache_expired:
            logger.info(f"{company} data not yet fetched or cache expired. Starting fetch")
            try:
                cls._data[company] = cls._get_airtable_data(company)
                cls._data_ts[company] = time.time()
                logger.info(f"{company} data fetching successful")
            except:
                logger.exception(f"Exception while fetching {company} data: ")
        else:
            logger.info(f"{company} data already fetched. Using cached data")

        # Todo: Netflix vs netflix in whole Code - GoPro
        return cls._data.get(company).copy()

    @classmethod
    def _get_hyped_companies(cls, hyped: bool) -> pd.DataFrame:
        """
        API Fetching the most hyped or least hyped companies
        hyped is a boolean -> True for hyped companies; False for not hyped

        Might raise exception. Should be handled by calling method
        :param hyped: boolean -> True for hyped companies; False for not hyped
        :return: returns a pandas DataFrame
        """
        logger.info("Fetching the hyped/not hyped data list")
        headers = {
            "Authorization": f"Bearer {cls.AIRTABLE_API_KEY}"
        }
        if hyped:  # If hyped is set as "true"
            url = "https://api.airtable.com/v0/appm3ffcu38jyqhi3/Companies?fields%5B%5D=Company_Name&fields%5B%5D=Hype_meter_value&view=Most+hyped+companies"
            response = requests.get(url, headers=headers)  # Call the Airtable data with the specified filter
            data = response.json()  # Transforms it into a dictionary

            # Format the data into a dataframe including only the Date and the Users
            records = data['records']
            formatted_data = []
            for record in records:
                formatted_data.append({
                    'Company Name': record['fields']['Company_Name'],
                    'Hype Score': record['fields']['Hype_meter_value'],
                })
            df = pd.DataFrame(formatted_data)  # Create a DataFrame from the sample data
            return df

        else:
            url = "https://api.airtable.com/v0/appm3ffcu38jyqhi3/Companies?fields%5B%5D=Company_Name&fields%5B%5D=Hype_meter_value&fields%5B%5D=Growth_score&view=Least+hyped+companies"
            response = requests.get(url, headers=headers)  # Call the Airtable data with the specified filter
            data = response.json()  # Transforms it into a dictionary
            # Format the data into a dataframe including only the Date and the Users
            records = data['records']
            formatted_data = []
            for record in records:
                formatted_data.append({
                    'Company Name': record['fields']['Company_Name'],
                    'Hype Score': record['fields']['Hype_meter_value'],
                    'Growth Score': record['fields']['Growth_score']
                })
            df = pd.DataFrame(formatted_data)  # Create a DataFrame from the sample data
            return df

    @classmethod
    def get_hyped_companies(cls, hyped: bool) -> pd.DataFrame:
        """
        Checks if hyped/not hyped data has been downloaded. If so returns it, if not it will go and fetch it from
        AirTable. Re-fetches when the cached value is older than _HYPED_TTL seconds.
        :param hyped: bool if hyped or not hyped
        :return: pandas DataFrame.
        """
        cache_expired = (time.time() - cls._hyped_companies_ts.get(hyped, 0.0)) > _HYPED_TTL
        if hyped not in cls._hyped_companies or cache_expired:
            logger.info(f"{'hyped' if hyped else 'not hyped'} company data not yet fetched or cache expired. Starting fetch")
            try:
                cls._hyped_companies[hyped] = cls._get_hyped_companies(hyped)
                cls._hyped_companies_ts[hyped] = time.time()
                logger.info(f"{'hyped' if hyped else 'not hyped'} company data fetching successful")
            except:
                logger.exception(f"Exception while fetching {'hyped' if hyped else 'not hyped'} company data: ")
        else:
            logger.info(f"{'hyped' if hyped else 'not hyped'} company data already fetched. Using cached data")

        return cls._hyped_companies.get(hyped).copy()

    # ToDo: This looks like we should be loading the data from airtable and then filter it depending on our needs
    @classmethod
    def _get_hyped_companies_data(cls) -> pd.DataFrame:
        """
        Function fetching the list of all the companies (companies sheet on airtable) and the related information
        (max net margin, other info, etc.)

        Might raise exception. Should be handled by calling method
        :return: pandas DataFrame
        """
        logger.info("Fetching the dataset data...")
        headers = {
            "Authorization": f"Bearer {cls.AIRTABLE_API_KEY}"
        }

        base_url = "https://api.airtable.com/v0/appm3ffcu38jyqhi3/Companies"
        params = {
            "fields[]": ["Company_Name", "Hype_meter_value", "Growth_score", "Max_Net_Margin", "Company_logo",
                         "Industry",
                         "Company description"],
            "view": "Most hyped companies"
        }

        all_records = []
        offset = None

        while True:
            # Add offset if we have one
            if offset:
                params["offset"] = offset

            # Fetch one page of records
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            # Append current batch
            records = data.get("records", [])
            for record in records:
                fields = record.get("fields", {})
                # ToDo: Can this be done more efficient?
                all_records.append({
                    "Company Name": fields.get("Company_Name"),
                    "Hype Score": fields.get("Hype_meter_value"),
                    "Max Net Margin": fields.get("Max_Net_Margin"),
                    "Growth Score": fields.get("Growth_score"),
                    "Company Logo": fields.get("Company_logo"),
                    "Industry": fields.get("Industry"),
                    "Description": fields.get("Company description")
                })

            # Check if there’s another page
            offset = data.get("offset")
            if not offset:
                break  # No more pages

        df = pd.DataFrame(all_records)
        logger.info(f"Fetched {len(df)} records successfully.")
        return df

    @classmethod
    def get_hyped_companies_data(cls) -> pd.DataFrame:
        """
        Checks if hyped company data has been downloaded. If so returns it, if not it will go and fetch it from
        AirTable. Re-fetches when the cached value is older than _HYPED_TTL seconds.
        :return:
        """
        cache_expired = (time.time() - cls._hyped_companies_data_ts) > _HYPED_TTL
        if cls._hyped_companies_data is None or cache_expired:
            logger.info("hyped_companies data not yet fetched or cache expired. Starting fetch")
            try:
                cls._hyped_companies_data = cls._get_hyped_companies_data()
                cls._hyped_companies_data_ts = time.time()
                logger.info("hyped_companies data fetching successful")
            except:
                logger.exception(f"Exception while fetching hyped_companies data: ")
        else:
            logger.info("hyped_companies data already fetched. Using cached data")

        return cls._hyped_companies_data


if __name__ == "__main__":
    # Proves that label fetching works and that the same api is returned when calling the class.
    api1 = AirTableAPI()
    api2 = AirTableAPI()
    logger.info(f"{api1 is api2 =}")
    api1.get_labels()
    api2.get_labels()

    df1 = api2.get_data('Netflix')
    df2 = api1.get_data('Netflix')

    logger.info(f"{df1 == df2}")