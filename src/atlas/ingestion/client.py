from typing import Any

import requests

class APIClient:
    """client responsible for communicating with external APIs"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:

        url = f"{self.base_url}/{endpoint.lstrip("/")}"

        response = requests.get(url, params=params, timeout=30)

        response.raise_for_status()

        return response.json()
