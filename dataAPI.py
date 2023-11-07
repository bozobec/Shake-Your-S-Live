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
    return unique_values_list

def get_airtable_data(filter):
    url2 = "https://api.airtable.com/v0/appm3ffcu38jyqhi3/tbl7LiTDpXk9DeRUB?fields%5B%5D=Company" \
          "&fields%5B%5D=Date&fields%5B%""5D=Users&filterByFormula=Company%3D%22{}%22&sort%5B0%5D%5Bfield" \
          "%5D=Users&sort%5B0%5D%5B""direction%5D=asc".format(filter)  # Add the filter to the URL to get only
                                                                        # the company needed
    url = "https://api.airtable.com/v0/appm3ffcu38jyqhi3/tbl7LiTDpXk9DeRUB?fields%5B%5D=Company" \
           "&fields%5B%5D=Date&fields%5B%5D=Users&filterByFormula=Company%3D%22{}%22&sort%5B0%5D%5Bfield" \
           "%5D=Date&sort%5B0%5D%5Bdirection%5D=asc".format(filter)
    auth_token = "patUQKc4meIVaiLIw.efa35a957210ca18edc4fc00ae1b599a6a49851b8b7c59994e4384c19c20fcd1"
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = requests.get(url, headers=headers)  # Call the Airtable data with the specified filter
    data = response.json()  # Transforms it into a dictionary
    #Format the data into a dataframe including only the Date and the Usres
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


df = get_airtable_data("Netflix")
print("API operational")