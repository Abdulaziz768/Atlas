from atlas.ingestion.client import APIClient
from atlas.ingestion.models import Company
from atlas.config.settings import FINANCIAL_API_KEY

class CompanyService:
    """Service responsible for fetching and converting company data"""

    def __init__(self, client: APIClient):
        self.client = client

    def get_company(self, ticker: str) -> Company:

        data = self.get_company_data(ticker)

        return Company(
            ticker=data["Symbol"],
            name = data["Name"],
            exchange=data["Exchange"],
            sector=data["Sector"],
            industry=data["Industry"],
            currency=data["Currency"],
            market_cap=data.get("MarketCapitalization"),
            description=data.get("Description")
        )

    def get_company_data(self, ticker: str) -> dict:

        return self.client.get(
            "",
            params={
                "function" : "OVERVIEW",
                "symbol" : ticker,
                "apikey" : FINANCIAL_API_KEY,
            },
        )