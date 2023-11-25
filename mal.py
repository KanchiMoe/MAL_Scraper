from src.companies import companies_start

# Config settings
ROOT_URL = "https://myanimelist.net"
COMPANY_END_ID = 3000

companies_start(root_url=ROOT_URL, end_number=COMPANY_END_ID)
