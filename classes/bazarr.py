import os
import requests
from classes.wanted import Wanted
from typing import List


class Bazarr:
    def __init__(self) -> None:
        self.url = os.getenv("BAZARR_SERVER")
        self.headers = {"X-API-KEY": os.getenv("BAZARR_API_KEY"), "accept": "application/json", "accept-encoding": "identity"}

    def wanted(self, _type: str) -> List[Wanted]:
        resp = requests.get(f"{self.url}/api/{_type}s/wanted", headers=self.headers)
        return [Wanted(x, _type) for x in resp.json()['data']]
 