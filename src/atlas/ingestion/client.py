import time
from typing import Any

import requests


class APIClient:
    """Client responsible for communicating with external APIs."""

    def __init__(
        self,
        base_url: str,
        min_request_interval: float = 0,
    ):
        self.base_url = base_url.rstrip("/")
        self.min_request_interval = min_request_interval
        self._last_request_time = 0.0

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        elapsed = time.monotonic() - self._last_request_time

        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)

        url = f'{self.base_url}/{endpoint.lstrip("/")}'

        response = requests.get(
            url,
            params=params,
            timeout=30,
        )

        self._last_request_time = time.monotonic()

        response.raise_for_status()

        return response.json()