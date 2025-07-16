import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from dotenv import load_dotenv

load_dotenv()

polling_interval = 1
DAILY_RISK = -1500
base_url = "https://api.dhan.co/v2"
timeout = 5

def create_session():
    retry = Retry(
        total=3, # total retries
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "DELETE"],
        raise_on_status=False
    )
    adapter = HTTPAdapter(
        max_retries=retry
        #pool_connections=10, # You can keep a maximum of 10 different sites active with connection reuse.
        #pool_maxsize=100 # For each API host, allow 100 open lanes to send/receive requests without blocking.
    )
    s = requests.Session()
    s.mount("https://", adapter)
    s.mount("http://", adapter)

    s.headers.update({
        "access-token": os.getenv("ACCESS_TOKEN"),
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    return s

session = create_session()
