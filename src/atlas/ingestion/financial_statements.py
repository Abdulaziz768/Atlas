import time
from typing import Any

from atlas.config.settings import FINANCIAL_API_KEY
from atlas.ingestion.client import APIClient


class FinancialStatementService:
    """Service responsible for fetching financial statement data."""

    def __init__(
        self,
        client: APIClient,
        max_retries: int = 3,
        retry_delay: float = 5,
    ):
        self.client = client
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _get_statement(
        self,
        function: str,
        ticker: str,
    ) -> dict[str, Any]:

        for attempt in range(self.max_retries + 1):
            data = self.client.get(
                "",
                params={
                    "function": function,
                    "symbol": ticker,
                    "apikey": FINANCIAL_API_KEY,
                },
            )

            if "annualReports" in data and "quarterlyReports" in data:
                return data

            if "Information" in data and attempt < self.max_retries:
                time.sleep(self.retry_delay)
                continue

            raise RuntimeError(
                f"Alpha Vantage failed for {function}: {data}"
            )

        raise RuntimeError(
            f"Alpha Vantage failed for {function} after retries"
        )

    def get_financial_statements(self, ticker: str) -> dict[str, Any]:
        return {
            "income_statement": self._get_statement(
                "INCOME_STATEMENT",
                ticker,
            ),
            "balance_sheet": self._get_statement(
                "BALANCE_SHEET",
                ticker,
            ),
            "cash_flow": self._get_statement(
                "CASH_FLOW",
                ticker,
            ),
        }