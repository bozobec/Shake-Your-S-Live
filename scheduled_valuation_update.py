import time
import json
import schedule
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pyairtable import Api
from src.API.AirTableAPI import AirTableAPI

# --- CONFIGURATION ---
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = 'appm3ffcu38jyqhi3'
TABLE_NAME = 'Companies'
DASH_APP_URL = 'https://app.rast.guru/'
#DASH_APP_URL = 'http://127.0.0.1:8050/'

# Companies to track
#ToDo: Important: update the companies array dynamically instead of hardcoding it
COMPANIES = [
    'Accenture', 'Adobe', 'Adyen', 'Affirm', 'Airbnb', 'Alphabet', 'Amazon',
    'Atlassian', 'Beyond Meat', 'BILL Holdings', 'Block', 'Booking Holdings',
    'Bumble', 'Carvana', 'CAVA Group', 'Centene Corporation', 'Charles Schwab',
    'Chegg', 'Chewy', 'Chime', 'Chipotle', 'Circle Internet', 'Cloudflare',
    'Coinbase', 'Costco', 'Crocs', 'Datadog', 'Dayforce', 'Diageo', 'DocuSign',
    'Domino\'s Pizza', 'Doordash', 'DraftKings', 'Dropbox', 'Duolingo',
    'Dutch Bros', 'Ebay', 'Elastic N.V. (Elasticsearch)', 'Equinix', 'Etsy',
    'Expedia Group', 'Fastly', 'Figma', 'Freshpet', 'Gambling.com', 'Gitlab',
    'GoDaddy Inc.', 'GoPro', 'Grindr', 'Hims and Hers Health Inc', 'Hubspot',
    'Instacart (Maplebear Inc.)', 'Interactive Brokers', 'Jamf', 'Kazatomprom',
    'Live Nation Entertainment', 'Lululemon', 'Lyft', 'Mastercard', 'Match Group',
    'Mcdonald\'s', 'MercadoLibre', 'Meta', 'Microsoft', 'MongoDB', 'Morningstar',
    'Netflix', 'Nike', 'Nintendo', 'Nubank', 'Nvidia', 'Oatly', 'Opendoor',
    'Opera', 'Oscar Health', 'Palantir', 'Palo Alto Networks', 'Papa John\'s',
    'Paypal', 'Peloton', 'Petco', 'Pinterest', 'Procore',
    'RBI - Restaurant Brands International', 'Reddit', 'Revolve', 'Rivian',
    'Robinhood', 'Roblox', 'Rocket Companies', 'Roku', 'Rubrik', 'Salesforce',
    'Samsara', 'Sea Limited', 'ServiceNow', 'Shopify', 'Snap Inc.', 'Snowflake',
    'SoFi', 'Spotify', 'Sprinklr', 'Starbucks', 'Stitch Fix', 'StoneCo',
    'Surf Air', 'Sweetgreen', 'Tesla', 'Toast Inc.', 'Twilio', 'Uber', 'UI Path',
    'Ulta Beauty', 'United Rentals', 'United Wholesale Mortgage (UWM)', 'Unity',
    'Upstart', 'Veeva', 'Verisign', 'Victoria\'s Secret', 'Visa',
    'Warby Parker Inc.', 'Warner Bros Discovery Inc', 'Wayfair', 'Webull',
    'Wendy\'s', 'Wheels Up', 'Wise', 'Wix', 'Yelp', 'Yum! Brands', 'Zalando',
    'Zeta', 'Zillow', 'Zoom Communications Inc.'
]

# Initialize Airtable
api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, TABLE_NAME)

print(COMPANIES)
def get_hype_score(driver, company_id):
    """
    Navigates to the company page and extracts the hype score 
    specifically from Session Storage.
    """
    url = f"{DASH_APP_URL}?company={company_id}"
    print(f"Checking: {url}")

    driver.get(url)

    # Wait for Dash callbacks to fire and popuplate the store
    # If your app calculates this slowly, increase this time
    time.sleep(15)

    try:
        # EXECUTE JAVASCRIPT
        # Directly retrieve the value associated with the component ID
        # Since storage_type='session', it lives in sessionStorage under the ID.
        storage_value = driver.execute_script(
            "return window.sessionStorage.getItem('hype-score');"
        )

        if storage_value:
            # Dash stores data as a JSON string. We must parse it.
            # Example: storage_value might be '{"score": 88, "trend": "up"}'
            parsed_data = json.loads(storage_value)

            # CASE 1: The store contains a simple number/string
            if isinstance(parsed_data, (int, float, str)):
                return parsed_data

            # CASE 2: The store contains a dictionary (e.g. {'value': 10})
            # Adjust 'score' to whatever key your actual data uses
            elif isinstance(parsed_data, dict):
                return parsed_data.get('score', parsed_data)

            return parsed_data

        else:
            print(f"Warning: 'hype-score' not found in sessionStorage for {company_id}")
            return None

    except json.JSONDecodeError:
        print(f"Error: Data found but could not parse JSON for {company_id}")
        return None
    except Exception as e:
        print(f"Error extracting data for {company_id}: {e}")
        return None


def update_airtable_record(company_name, score):
    """
    Finds the company in Airtable and updates the score.
    """
    # 1. Search for the company record
    formula = f"{{Company_Name}} = '{company_name}'"
    matches = table.all(formula=formula)

    if not matches:
        print(f"Skipping: {company_name} not found in Airtable.")
        return

    record_id = matches[0]['id']

    # 2. Update the Hype Score
    # Note: Ensure the Airtable column is a Number or Text field as appropriate
    try:
        table.update(record_id, {'Hype_meter_value': score})
        print(f"Success: Updated {company_name} with score {score}")
    except Exception as e:
        print(f"Failed to write to Airtable: {e}")


def job():
    print(f"--- Starting Weekly Job: {datetime.now()} ---")

    chrome_options = Options()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")  # Vital for Heroku
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Use the binary location in the Service
    driver = webdriver.Chrome(
        service=Service(executable_path=os.environ.get("CHROMEDRIVER_PATH")),
        options=chrome_options
    )

    try:
        for company in COMPANIES:
            score = get_hype_score(driver, company)

            if score is not None:
                update_airtable_record(company, score)

            # Short sleep to prevent overwhelming the server/browser
            time.sleep(2)

    finally:
        driver.quit()
        print("--- Job Finished ---")

if __name__ == "__main__":
    job()  # The Heroku Scheduler triggers this
