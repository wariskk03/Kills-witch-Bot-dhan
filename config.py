import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

def load_config():
    with open("config_vars.json") as f:
        vars = json.load(f)
    return {
    "polling_interval" : 1,
    "daily_risk" : vars["daily_risk"],
    "base_url" : "https://api.dhan.co/v2",
    "timeout" : 5,
    "access_token": vars["access_token"]
    }

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
        "access-token": load_config()["access_token"],
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    return s

session = create_session()
