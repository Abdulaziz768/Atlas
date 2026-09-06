from typing import Any

from atlas.ingestion.client import APIClient
from atlas.config.settings import FINANCIAL_API_KEY

class StockPriceService:
    """Service responsible for fetching daily stock price data."""

    def __init__(self, client: APIClient):
        self.client = client

    def get_stock_price_data(self, ticker: str) -> list[dict[str, Any]]:
        data = self.client.get(
            "",
            params={
                "function": "TIME_SERIES_DAILY",
                "symbol": ticker,
                "apikey": FINANCIAL_API_KEY,
            },
        )

        time_series = data["Time Series (Daily)"]

        records = []

        for date, values in time_series.items():
            records.append(
                {
                    "symbol": ticker,
                    "date": date,
                    "open":values["1. open"],
                    "high":values["2. high"],
                    "low":values["3. low"],
                    "close":values["4. close"],
                    "volume":values["5. volume"]
                }
            )

        return records
