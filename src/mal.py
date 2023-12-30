import os
import logging

class MAL:
    def __init__(self):
        self.root_url = "https://myanimelist.net"
    def SaveAsJson():
        if not os.path.exists(directory):
            MAL.CreateDirectory(directory)

        xxx

    def CreateDirectory(self, directory: str):
        logging.debug(f"Directory {directory} does not exist, attempting to create it.")

        try:
            os.makedirs(directory)
        except:
            msg = f"Unable to create the directory: {directory} "
            logging.critical(msg)
            raise RuntimeError(msg)

class MAL_http_handler(MAL):
    def __init__(self):
        foo = "bar"

    def http_response_handler(self, response_code: int, url: str):
        status_functions = {
            200: self.http_200,
            404: self.http_404,
            405: self.http_405,
            429: self.http_429,
            }

        if response_code in status_functions:
            status_functions[response_code](url)
        else:
            self.http_unknown(url, response_code)

    def http_200(self, url: str):
        print(f"Got 200 at {url}")

    def http_404(self, url: str):
        print(f"Got 404 at {url}")

    def http_405(self, url: str):
        msg = f"Got 405, at {url}. MAL seems to use this for rate-limiting. Passing handling to 429."
        logging.warn(msg)
        self.http_429(url)

    def http_429(self, url: str):
        msg = f"We've been rate limited. Last page: {url}"
        logging.critical(msg)
        raise RuntimeError(msg)

    def http_unknown(self, url: str, response_code: int):
        msg = f"Got {response_code} at {url}"
        logging.error(msg)
        raise RuntimeError(msg)
