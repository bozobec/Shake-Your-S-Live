import requests
import pandas as pd
from src.Utils.rast_logger import get_default_logger

logger = get_default_logger()


class AirTableAPI:
    labels = None
    data = {}
    instance = None

    def __new__(cls, *args, **kwargs):
        """
        This function makes sure that there is only one instance of this class, no matter where you call it in code
        :param args:
        :param kwargs:
        """
        if cls.instance is None:
            cls.instance = super(AirTableAPI, cls).__new__(cls)

        return cls.instance

    @staticmethod
    def _get_airtable_labels():
        """
        This function fetches all the unique categories in the airtable database
        :return:
        """
        url = "https://api.airtable.com/v0/appm3ffcu38jyqhi3/tbl7LiTDpXk9DeRUB?fields%5B%5D=Company"
        auth_token = "patUQKc4meIVaiLIw.efa35a957210ca18edc4fc00ae1b599a6a49851b8b7c59994e4384c19c20fcd1"
        headers = {
            "Authorization": f"Bearer {auth_token}"
        }
        response = requests.get(url, headers=headers)  # Call the Airtable data with the specified filter
        data = response.json()  # Transforms it into a dictionary
        # Format the data into a dataframe including only the Date and the Usres
        records = data['records']
        unique_values = set()
        for record in records:
            company = record['fields']['Company']
            unique_values.add(company)
        unique_values_list = list(unique_values)
        return unique_values_list

    @staticmethod
    def _get_airtable_data(company: str) -> pd.DataFrame:
        """
        Gets company data from Airtable using the provided company string. Return a pandas DataFrame.
        :param company: string of the company
        :return: pandas DataFrame containing company data from AirTable
        """
        # the company needed
        url = "https://api.airtable.com/v0/appm3ffcu38jyqhi3/tbl7LiTDpXk9DeRUB?fields%5B%5D=Company" \
              "&fields%5B%5D=Date&fields%5B%5D=Users&filterByFormula=Company%3D%22{}%22&sort%5B0%5D%5Bfield" \
              "%5D=Date&sort%5B0%5D%5Bdirection%5D=asc".format(company)
        auth_token = "patUQKc4meIVaiLIw.efa35a957210ca18edc4fc00ae1b599a6a49851b8b7c59994e4384c19c20fcd1"
        headers = {
            "Authorization": f"Bearer {auth_token}"
        }
        response = requests.get(url, headers=headers)  # Call the Airtable data with the specified filter
        data = response.json()  # Transforms it into a dictionary
        # Format the data into a dataframe including only the Date and the Usres
        records = data['records']
        formatted_data = []
        for record in records:
            formatted_data.append({
                'Date': record['fields']['Date'],
                'Users': record['fields']['Users']
            })
        df = pd.DataFrame(formatted_data)  # Create a DataFrame from the sample data
        # sorted_df = df.sort_values(by='Date')  # Sort df to avoid bugs linked to wrong API call
        return df

    @classmethod
    def get_labels(cls):
        """
        Checks if the labels have already been downloaded and returns it. If not, it will go and fetch it.
        :return:
        """
        if cls.labels is None:
            logger.info("Labels not yet fetched. Starting fetch")
            try:
                cls.labels = AirTableAPI._get_airtable_labels()
                logger.info("Label fetching successful.")
            except:
                logger.exception("Exception while fetching AirTable labels")

        else:
            logger.info("Labels already fetched. Using cached data")

        return cls.labels

    @classmethod
    def get_data(cls, company: str) -> pd.DataFrame:
        """
        Check if company data has already been downloaded. If so returns it, if not it will go and fetch it from
        AirTable. Returns a pandas DataFrame
        :param company: string of the company
        :return: pandas DataFrame of the company data.
        """
        if company not in cls.data.keys():
            # we need to go and fetch it
            logger.info(f"{company} data not yet fetched. Starting fetch")
            try:
                cls.data[company] = AirTableAPI._get_airtable_data(company)
                logger.info(f"{company} data fetching successful")

            except:
                logger.exception(f"Exception while fetching {company} data: ")

        else:
            logger.info(f"{company} data already fetched. Using catched data")

        return cls.data.get(company)


if __name__ == "__main__":
    # Proves that label fetching works and that the same api is returned when calling the class.
    api1 = AirTableAPI()
    api2 = AirTableAPI()
    logger.info(f"{api1 is api2 =}")
    api1.get_labels()
    api2.get_labels()
