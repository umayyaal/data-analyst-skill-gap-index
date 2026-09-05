import os
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

# Load API credentials from .env
load_dotenv()
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

# Countries we're tracking
COUNTRIES = {
    "in": "India",
    "us": "United States",
    "gb": "United Kingdom"
}

SEARCH_QUERY = "data analyst"
RESULTS_PER_PAGE = 50
PAGES_PER_COUNTRY = 3   # 3 pages x 50 = up to 150 postings per country per run
RAW_DATA_DIR = "data/raw"


def fetch_jobs(country_code, page):
    """Fetch one page of job postings for a given country."""
    url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/{page}"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": RESULTS_PER_PAGE,
        "what": SEARCH_QUERY,
        "content-type": "application/json"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # will raise an error if the call fails
    return response.json()


def save_raw_data(data, country_code, page):
    """Save the raw API response as a timestamped JSON file."""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"{RAW_DATA_DIR}/{country_code}_page{page}_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {filename}")


def main():
    for country_code, country_name in COUNTRIES.items():
        print(f"\nFetching jobs for {country_name} ({country_code})...")
        for page in range(1, PAGES_PER_COUNTRY + 1):
            try:
                data = fetch_jobs(country_code, page)
                save_raw_data(data, country_code, page)
                time.sleep(1)  # be polite to the API, avoid hammering it
            except requests.exceptions.HTTPError as e:
                print(f"Error fetching {country_name} page {page}: {e}")


if __name__ == "__main__":
    main()