import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from collections import defaultdict
from src.Utils.RastLogger import get_default_logger

logger = get_default_logger()

# The following code specifies firstly the filter and then fetches the data according to
# it in the specified airtable database
# This tool was used to generate the right url to be used: https://codepen.io/airtable/pen/MeXqOg

load_dotenv()
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")


def get_airtable_labels():
    """
    This function fetches all the unique categories in the airtable database
    :return:
    """
    logger.info("Fetching the dataset labels")
    url = "https://api.airtable.com/v0/appm3ffcu38jyqhi3/tbl7LiTDpXk9DeRUB?fields%5B%5D=Company&fields%5B%5D=Category&fields%5B%5D=Symbol"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}"
    }

    # Initialize variables
    offset = None
    all_records = []

    try:
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

    except Exception as e:
        logger.error(f"Error fetching dataset labels: {str(e)}")
        return None


def get_airtable_data(filter):
    logger.info("Fetching the dataset data")
    try:
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
            "Authorization": f"Bearer {AIRTABLE_API_KEY}"
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
    except Exception as e:
        logger.error(f"Error fetching dataset data: {str(e)}")
        return None


def get_marketcap(symbol_input):
    """
    API Fetching the market cap of the company in $mio.
    :param symbol_input:
    :return:
    """
    logger.info("Fetching the current market cap")
    try:
        url = "https://finnhub.io/api/v1/stock/profile2?"
        auth_token = "clmplq1r01qjj8i8s6ugclmplq1r01qjj8i8s6v0"  # Free token visible here: https://finnhub.io/dashboard
        symbol = symbol_input
        response = requests.get(url, params={'symbol': symbol, 'token': auth_token})
        data = response.json()
        currency = data.get("currency")
        market_cap = data.get("marketCapitalization")
        if currency == "JPY":
            market_cap = 0.0064 * market_cap  # exchange rate on 16 Jan 25, to be updated regularly
        return market_cap

    except Exception as e:
        logger.error(f"Error fetching market cap: {str(e)}")
        return None


def get_previous_quarter_revenue(symbol_input):
    """
    API Fetching the revenue of the last quarter
    :param symbol_input:
    :return:
    """
    logger.info("Fetching the quarterly revenue")
    try:
        url = "https://finnhub.io/api/v1/stock/financials-reported?"
        auth_token = "clmplq1r01qjj8i8s6ugclmplq1r01qjj8i8s6v0"  # Free token visible here: https://finnhub.io/dashboard
        symbol = symbol_input  # Symbol of the stock
        frequency = "quarterly"  # Frequency of the report
        # Get the current date
        current_date = datetime.now()

        # Calculate the end date of the previous quarter
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

        # Response
        response = requests.get(url, params={'symbol': symbol,
                                             'freq': frequency,
                                             'token': auth_token})
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
    except Exception as e:
        logger.error(f"Error fetching quarterly revenue: {str(e)}")
        return 0, total_assets


def get_profit_margin(symbol_input):
    """
    API Fetching the profit margin of the past year
    :param symbol_input:
    :return:
    """
    logger.info("Fetching the profit margin")
    try:
        url = "https://finnhub.io/api/v1/stock/metric?"
        auth_token = "clmplq1r01qjj8i8s6ugclmplq1r01qjj8i8s6v0"  # Free token visible here: https://finnhub.io/dashboard
        symbol = symbol_input  # Symbol of the stock
        metric = "netProfitMarginAnnual"  # Frequency of the report

        # Response
        response = requests.get(url, params={'symbol': symbol, 'metric': metric, 'token': auth_token})
        data = response.json()
        profit_margin = data['metric']['netProfitMarginAnnual']
        return profit_margin

    except Exception as e:
        logger.error(f"Error fetching yearly profit_margin: {str(e)}")
        return 0


def get_hyped_companies(hyped):
    """
    API Fetching the most hyped or least hyped companies
    hyped is a boolean -> True for hyped companies; False for not hyped
    :param hyped:
    :return:
    """
    logger.info("Fetching the hyped/not hyped data list")
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}"
    }
    if hyped:  # If hyped is set as "true"
        try:
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

        except Exception as e:
            logger.error(f"Error fetching dataset data: {str(e)}")
            return None
    else:
        try:
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
        except Exception as e:
            logger.error(f"Error fetching dataset data: {str(e)}")
            return None


def get_hyped_companies_data():
    """
    Function fetching the list of all the companies (companies sheet on airtable) and the related information
    (max net margin, other info, etc.)
    :return:
    """
    logger.info("Fetching the dataset data...")
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}"
    }

    base_url = "https://api.airtable.com/v0/appm3ffcu38jyqhi3/Companies"
    params = {
        "fields[]": ["Company_Name", "Hype_meter_value", "Growth_score", "Max_Net_Margin", "Company_logo", "Industry",
                     "Company description"],
        "view": "Most hyped companies"
    }

    all_records = []
    offset = None

    try:
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
    except Exception as e:
        logger.error(f"Error fetching dataset data: {str(e)}")
        return None
