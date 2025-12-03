import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

# ToDo: What is this?
'''
# List of URLs to crawl
urls = [
    "https://rast.guru/app?company=Affirm",
    "https://rast.guru/app?company=Airbnb",
    "https://rast.guru/app?company=Arista%20Networks"
]

# Configure Chrome options (running headless)
chrome_options = Options()
chrome_options.add_argument("--headless")

# Initialize the WebDriver (ensure chromedriver is installed and in your PATH)
driver = webdriver.Chrome(options=chrome_options)

# List to store extracted data
data = []

for url in urls:
    try:
        # Parse the company name from the URL query string
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        company = query_params.get('company', ['Unknown'])[0]

        # Open the URL
        driver.get(url)

        # Wait 10 seconds to allow dynamic content to load
        time.sleep(10)

        # Get the updated HTML after JavaScript has rendered the page
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Extract the text content from the div with id "hype-market-cap"
        hype_market_cap_div = soup.find("div", id="hype-market-cap")
        hype_market_cap = hype_market_cap_div.text.strip() if hype_market_cap_div else "Not found"

        # Extract the width from the style attribute of the div with id "hype-meter-hype"
        hype_meter_hype_div = soup.find("div", id="hype-meter-hype")
        hype_meter_value = "Not found"
        if hype_meter_hype_div:
            style_attr = hype_meter_hype_div.get("style", "")
            for part in style_attr.split(";"):
                if "width:" in part:
                    hype_meter_value = part.split("width:")[1].strip()
                    break

        # Append the extracted data into our list
        data.append({
            "company": company,
            "hype-market-cap": hype_market_cap,
            "hype-meter-value": hype_meter_value
        })

        print(f"Processed {company}: Hype Market Cap = {hype_market_cap}, Hype Meter Value = {hype_meter_value}")

    except Exception as e:
        print(f"Error processing {url}: {e}")

# Close the browser once processing is complete
driver.quit()

# -------------------------------
# Write data to Airtable
# -------------------------------

# Replace the following placeholders with your actual Airtable credentials
AIRTABLE_API_KEY = "YOUR_API_KEY_HERE"
AIRTABLE_BASE_ID = "YOUR_BASE_ID_HERE"
AIRTABLE_TABLE_NAME = "YOUR_TABLE_NAME_HERE"

airtable_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

headers = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

# Prepare payload as a list of records in Airtable format
records = [{"fields": record} for record in data]
payload = {"records": records}

response = requests.post(airtable_url, headers=headers, json=payload)

if response.status_code in [200, 201]:
    print("Data successfully written to Airtable!")
else:
    print(f"Failed to write data to Airtable: {response.text}")

'''