import requests
import logging
from bs4 import BeautifulSoup
import time

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

def companies_start(ROOT_URL):
    start_number = 1
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
    if consecutive_404_count >= max_consecutive_404:
        raise RuntimeError(f"Reached {max_consecutive_404} consecutive 404 responses.")
