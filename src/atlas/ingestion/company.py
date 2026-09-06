from atlas.ingestion.client import APIClient
from atlas.config.settings import FINANCIAL_API_KEY

class CompanyService:
    """Service responsible for fetching company data."""

    def __init__(self, client: APIClient):
        self.client = client

    def get_company_data(self, ticker: str) -> dict:
        return self.client.get(
            "",
            params={
                "function": "OVERVIEW",
                "symbol": ticker,
                "apikey": FINANCIAL_API_KEY,
            },
        )