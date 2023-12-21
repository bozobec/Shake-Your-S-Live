import requests
import json
import numpy as np
import pandas as pd
import main
from datetime import datetime

# The following code specifies firstly the filter and then fetches the data according to
# it in the specified airtable database
# This tool was used to generate the right url to be used: https://codepen.io/airtable/pen/MeXqOg

# This function fetches all the unique categories in the airtable database
def get_airtable_labels():
    print("Fetching the dataset labels")
    try:
        url = "https://api.airtable.com/v0/appm3ffcu38jyqhi3/tbl7LiTDpXk9DeRUB?fields%5B%5D=Company"
        auth_token = "patUQKc4meIVaiLIw.efa35a957210ca18edc4fc00ae1b599a6a49851b8b7c59994e4384c19c20fcd1"
        headers = {
            "Authorization": f"Bearer {auth_token}"
        }
        response = requests.get(url, headers=headers)  # Call the Airtable data with the specified filter
        data = response.json()  # Transforms it into a dictionary
        # Format the data into a dataframe including only the Date and the Usres
        records = data['records']
        formatted_data = []
        unique_values = set()
        for record in records:
            company = record['fields']['Company']
            unique_values.add(company)
        unique_values_list = list(unique_values)
        print("Done fetching dataset label")
        return unique_values_list

    except Exception as e:
        print(f"Error fetching dataset labels: {str(e)}")
        return None

# This function fetches all the unique categories in the airtable database
def get_airtable_labels_new():
    print("Fetching the dataset labels")
    try:
        url = "https://api.airtable.com/v0/appm3ffcu38jyqhi3/tbl7LiTDpXk9DeRUB?fields%5B%5D=Company&fields%5B%5D=Category"
        auth_token = "patUQKc4meIVaiLIw.efa35a957210ca18edc4fc00ae1b599a6a49851b8b7c59994e4384c19c20fcd1"
        headers = {
            "Authorization": f"Bearer {auth_token}"
        }
        response = requests.get(url, headers=headers)  # Call the Airtable data with the specified filter
        data = response.json()  # Transforms it into a dictionary

        # Format the data into a dataframe including only the Date and the Users
        records = data['records']
        formatted_data = []
        for record in records:
            formatted_data.append({
                'Company': record['fields']['Company'],
                'Category': record['fields']['Category'],
            })
        df = pd.DataFrame(formatted_data)  # Create a DataFrame from the sample data

        # Keep only unique companies
        df.drop_duplicates(subset='Company', inplace=True)

        # Initialize label_list
        label_list = []

        # Sort DataFrame by Category and Company
        df.sort_values(by=['Category', 'Company'], inplace=True)

        # Iterate through the sorted DataFrame to create label_list
        current_category = None
        for index, row in df.iterrows():
            category = row['Category']
            company = row['Company']

            # Check if a new category is encountered
            if current_category != category:
                label_list.append({"value": category, "label": f" {category}", "disabled": True})
                current_category = category

            label_list.append({"value": company, "label": f" {company}", "disabled": False})

        #print(label_list)
        return label_list

    except Exception as e:
        print(f"Error fetching dataset labels: {str(e)}")
        return None

def get_airtable_data(filter):
    print("Fetching the dataset data")
    try:
        url2 = "https://api.airtable.com/v0/appm3ffcu38jyqhi3/tbl7LiTDpXk9DeRUB?fields%5B%5D=Company" \
               "&fields%5B%5D=Date" \
               "&fields%5B%5D=Users" \
               "&fields%5B%5D=Unit" \
               "&fields%5B%5D=Symbol" \
               "&fields%5B%5D=Quarterly_Revenue_Mio$" \
               "&filterByFormula=Company%3D%22{}%22" \
               "&sort%5B0%5D%5Bfield%5D=Date" \
               "&sort%5B0%5D%5Bdirection%5D=asc".format(filter)  # Add the filter to the URL to get only
                                                                            # the company needed
        url = "https://api.airtable.com/v0/appm3ffcu38jyqhi3/tbl7LiTDpXk9DeRUB?fields%5B%5D=Company" \
               "&fields%5B%5D=Date" \
               "&fields%5B%5D=Users" \
               "&fields%5B%5D=Unit" \
               "&fields%5B%5D=Symbol" \
               "&fields%5B%5D=Quarterly_Revenue_Mio$" \
               "&filterByFormula=Company%3D%22{}%22" \
               "&sort%5B0%5D%5Bfield%5D=Date" \
               "&sort%5B0%5D%5Bdirection%5D=asc".format(filter)
        auth_token = "patUQKc4meIVaiLIw.efa35a957210ca18edc4fc00ae1b599a6a49851b8b7c59994e4384c19c20fcd1"
        headers = {
            "Authorization": f"Bearer {auth_token}"
        }
        response = requests.get(url, headers=headers)  # Call the Airtable data with the specified filter
        data = response.json()  # Transforms it into a dictionary

        #Format the data into a dataframe including only the Date and the Users
        records = data['records']
        formatted_data = []
        for record in records:
            formatted_data.append({
                'Date': record['fields']['Date'],
                'Users': record['fields']['Users'],
                'Unit': record['fields']['Unit'],
                'Symbol': record['fields']['Symbol'],
                'Revenue': record['fields']['Quarterly_Revenue_Mio$']
            })
        df = pd.DataFrame(formatted_data)  # Create a DataFrame from the sample data
        # sorted_df = df.sort_values(by='Date')  # Sort df to avoid bugs linked to wrong API call
        return df
    except Exception as e:
        print(f"Error fetching dataset data: {str(e)}")
        return None

# API Fetching the market cap of the company in $mio.
def get_marketcap(symbol_input):
    print("Fetching the dataset data")
    try:
        url = "https://finnhub.io/api/v1/stock/profile2?"
        auth_token = "clmplq1r01qjj8i8s6ugclmplq1r01qjj8i8s6v0"  # Free token visible here: https://finnhub.io/dashboard
        symbol = symbol_input
        response = requests.get(url, params={'symbol': symbol, 'token': auth_token})
        data = response.json()
        market_cap = data.get("marketCapitalization")
        return market_cap
    except Exception as e:
        print(f"Error fetching market cap: {str(e)}")
        return None

# API Fetching the revenue of the last quarter
def get_previous_quarter_revenue(symbol_input):
    print("Fetching the quarterly revenue")
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
            year_percentage = 1/4
        else:
            # Otherwise, calculate the last day of the previous quarter
            previous_quarter = (current_date.month - 1) // 3
            end_date_prev_quarter = datetime(current_date.year, previous_quarter * 3, 1)
            year_percentage = previous_quarter/4  # Defines the percentage of the year that has passed. Because
                                                    # the revenue in the report is from the beginning of the year
        from_date = end_date_prev_quarter.strftime('%Y-%m-%d')
        to_date = current_date.strftime('%Y-%m-%d')

        # Response
        response = requests.get(url, params={'symbol': symbol, 'freq': frequency, 'from': from_date,
                                             'to': to_date, 'token': auth_token})
        data = response.json()
        try:
            total_assets = next(
                item['value'] for item in data['data'][0]['report']['bs'] if item['label'] == 'Total current assets')
        except:
            total_assets = 0.0
            print("Error fetching total assets")
        try:
            revenue = next(item['value'] for item in data['data'][0]['report']['ic'] if item['label'] == 'Revenue'
                           or item['label'] == 'Revenues' or item['label'] == 'Revenue:')
        except:
            revenue = next(item['value'] for item in data['data'][0]['report']['ic'] if item['label'] == 'Revenues')

        return revenue / year_percentage, total_assets
    except Exception as e:
        print(f"Error fetching quarterly revenue: {str(e)}")
        return 0, total_assets

# API Fetching the profit margin of the past year
def get_profit_margin(symbol_input):
    print("Fetching the profit margin")
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
        print(f"Error fetching yearly profit_margin: {str(e)}")
        return 0


print(get_profit_margin("NFLX"))