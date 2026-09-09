import time
from typing import Any

import requests


class APIClient:
    """Client responsible for communicating with external APIs."""

    def __init__(
        self,
        base_url: str,
        min_request_interval: float = 0,
        max_retries: int = 3,
        retry_backoff: float = 2.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.min_request_interval = min_request_interval
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self._last_request_time = 0.0

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        url = f'{self.base_url}/{endpoint.lstrip("/")}'

        for attempt in range(self.max_retries + 1):

            elapsed = time.monotonic() - self._last_request_time

            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)

            response = requests.get(
                url,
                params=params,
                timeout=30,
            )

            self._last_request_time = time.monotonic()

            response.raise_for_status()

            data = response.json()

            if "Information" in data:
                if attempt == self.max_retries:
                    raise RuntimeError(
                        f"API provider returned an error: {data['Information']}"
                    )

                time.sleep(self.retry_backoff ** (attempt + 1))
                continue

            return data

        raise RuntimeError("API request failed")