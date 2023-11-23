from bs4 import BeautifulSoup
from datetime import datetime
import json
import logging
import os
import re
import requests
import time

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

def companies_start(ROOT_URL):
    start_number = 7
    end_number = 20
    sleep_time = 1
    consecutive_404_count = 0    

    for page_number in range(start_number, end_number):
        url = f"{ROOT_URL}/anime/producer/{page_number}"
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
            print(f"Error, got {response_code} at {url}")
        time.sleep(sleep_time)

def companies_200(page_number, soup):
    logging.info(f"Response 200 for {page_number}")

    EN_NAME = company_get_en_name(soup)
    sidebar_data = company_get_sidebar_data(soup)

    # Pass the data to be saved to a file
    company_save_data(page_number, en_name=EN_NAME)

def company_get_en_name(soup):
    en_name_element = soup.find("h1", class_="title-name")
    if en_name_element:
        print(en_name_element.get_text())
    
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
                data['Keyless'] = keyless_value

        json_data = json.dumps(data, indent=2, ensure_ascii=False)

        return json_data
    else:
        raise RuntimeError(f"Second div with class 'mb16' not found in the soup.") 

def companies_404(page_number, consecutive_404_count):
    logging.info(f"Response 404 for {page_number}")
    company_save_data(page_number)

    # Count how many 404's there has been in a row.
    # if >= 5, throw an error
    max_consecutive_404 = 5
    if consecutive_404_count >= max_consecutive_404:
        raise IndexError(f"Reached {max_consecutive_404} consecutive 404 responses.")

def company_save_data(page_number):
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

    template_data["id"] = page_number
    template_data["metadata"]["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    with open(filepath, "w") as json_file:
        json.dump(template_data, json_file, indent=2)
