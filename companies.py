from bs4 import BeautifulSoup
from datetime import datetime
import json
import logging
import os
import requests
import time

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

def companies_start(ROOT_URL):
    start_number = 5
    end_number = 3000
    sleep_time = 1
    consecutive_404_count = 0    

    for page_number in range(start_number, end_number):
        url = f"{ROOT_URL}/anime/producer/{page_number}"
        logging.info(f"Requesting {url}")
        request = requests.get(url)
        response_code = request.status_code

        if response_code == 200:
            companies_200(page_number)
            consecutive_404_count = 0
        elif response_code == 404:
            consecutive_404_count += 1
            companies_404(page_number, consecutive_404_count)
        else:
            print(f"Error, got {response_code} at {url}")
        time.sleep(sleep_time)

def companies_200(page_number):
    logging.info(f"Response 200 for {page_number}")


def companies_404(page_number, consecutive_404_count):
    max_consecutive_404 = 5
    logging.info(f"Response 404 for {page_number}")

    template_file_path = "data/templates/company404.json" # 
    with open(template_file_path, "r") as template_file:
        template_data = json.load(template_file)
   
    template_data["metadata"]["id"] = page_number
    template_data["metadata"]["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    directory = "data/company"
    filename = f"{page_number}.json"
    filepath = os.path.join(directory, filename)

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(filepath, "w") as json_file:
        json.dump(template_data, json_file, indent=2)

    if consecutive_404_count >= max_consecutive_404:
        raise RuntimeError(f"Reached {max_consecutive_404} consecutive 404 responses.")
