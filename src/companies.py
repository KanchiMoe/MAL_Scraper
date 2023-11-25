from bs4 import BeautifulSoup
from datetime import datetime
import json
import logging
import os
import requests
import time

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

def companies_start(root_url: str, ):
    start_number = 1
    end_number = 3000
    sleep_time = 1
    consecutive_404_count = 0    

    for page_number in range(start_number, end_number):
        url = f"{root_url}/anime/producer/{page_number}"
        logging.info(f"Requesting {url}")
        response = requests.get(url)
        response_code = response.status_code

        if response_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            companies_200(page_number, soup)
            consecutive_404_count = 0
        elif response_code == 404:
            consecutive_404_count += 1
            companies_404(page_number, consecutive_404_count)
        else:
            # Throw error if any other response
            print(f"Error, got {response_code} at {url}")
        time.sleep(sleep_time)

def companies_200(page_number, soup):
    logging.info(f"Response: 200")

    EN_NAME = company_get_en_name(soup)
    sidebar_data = company_get_sidebar_data(soup)
    amounts = company_get_anime_numbers(soup, page_number)

    # Debug logging
    logging.debug(f"EN_NAME: {EN_NAME}")
    logging.debug(f"SIDEBAR: {sidebar_data}")
    logging.debug(f"AMOUNTS: {amounts}")

    # Pass the data to be saved to a file
    company_save_data(page_number, en_name=EN_NAME, sidebar_data=sidebar_data, amounts=amounts)

def company_get_en_name(soup):
    # Get English name from page header
    producer_name_element = soup.find("h1", class_="title-name")
    if producer_name_element:
        return producer_name_element.get_text()
    
def company_get_sidebar_data(soup):
    mb16_elements = soup.find_all('div', class_='mb16')

    if len(mb16_elements) >= 2:
        mb16_find = mb16_elements[1]

        data = {}

        for element in mb16_find.find_all('div', class_='spaceit_pad'):
            dark_text_span = element.find('span', class_='dark_text')
            if dark_text_span:
                key = dark_text_span.get_text(strip=True).strip(':')
                value = element.contents[-1].strip() if element.contents else None

                data[key] = value
            else:
                # Handle keyless value
                keyless_value = element.get_text(strip=True)
                data['Description'] = keyless_value

        json_data = json.dumps(data, indent=2, ensure_ascii=False)

        return json_data
    else:
        raise RuntimeError(f"Second div with class 'mb16' not found in the soup.") 

def company_get_anime_numbers(soup, page_number):
    result = {}
    valid_keys = {'all', 'tv', 'ona', 'ova', 'movie', 'other'}

    for li in soup.select('li.js-btn-anime-type'):
        key = li.text.split('(')[0].strip().lower()  # Extract the key from the text
        if key not in valid_keys:
            raise IndexError(f"Invalid key: {key}. Expected one of {valid_keys}. Page: {page_number}")

        value = int(li.text.split('(')[-1].split(')')[0])  # Extract the numeric value between parentheses
        result[key] = value

    return result

def companies_404(page_number, consecutive_404_count):
    logging.info(f"Response: 404")
    company_save_data(page_number, en_name=None, sidebar_data={}, amounts={})

    # Count how many 404's there has been in a row.
    # if >= 5, throw an error
    max_consecutive_404 = 5
    if consecutive_404_count >= max_consecutive_404:
        raise IndexError(f"Reached {max_consecutive_404} consecutive 404 responses.")

def company_save_data(page_number, en_name, sidebar_data, amounts):
    # Set where to save the json files
    directory = "data/company"
    filename = f"{page_number}.json"
    filepath = os.path.join(directory, filename)

    # If the path doesn't exist, create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Open a template file
    template_file_path = "data/templates/company.json"
    with open(template_file_path, "r") as template_file:
        template_data = json.load(template_file)

    # Set the data 
    template_data["id"] = page_number
    template_data["metadata"] = {
        "status": 404 if isinstance(sidebar_data, dict) else 200,
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    template_data["amounts"] = amounts if amounts else {"all": 0, "tv": 0, "ona": 0, "ova": 0, "movie": 0, "others": 0}

    # Convert sidebar_data to a dictionary if it's a string
    if isinstance(sidebar_data, str):
        try:
            sidebar_data = json.loads(sidebar_data)
        except json.JSONDecodeError:
            # Handle the case where sidebar_data is not valid JSON
            print("Error decoding sidebar_data as JSON")
            sidebar_data = {}

    if en_name and isinstance(sidebar_data, dict):
        template_data["en_name"] = en_name
        template_data["jp_name"] = sidebar_data["Japanese"] if "Japanese" in sidebar_data else None
        template_data["established"] = sidebar_data["Established"] if "Established" in sidebar_data else None
        template_data["member_favorites"] = int(sidebar_data.get("Member Favorites", "").replace(",", "")) if sidebar_data.get("Member Favorites", "").replace(",", "").isdigit() else None
        template_data["description"] = sidebar_data["Description"] if "Description" in sidebar_data else None
    else:
        template_data["en_name"] = None
        template_data["jp_name"] = None
        template_data["established"] = None
        template_data["member_favorites"] = None
        template_data["description"] = None

    # Save the data to a file
    with open(filepath, "w", encoding="utf-8") as json_file:
        json.dump(template_data, json_file, indent=2, ensure_ascii=False)
