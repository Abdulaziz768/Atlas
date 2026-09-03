from atlas.ingestion.company import CompanyService
from atlas.ingestion.pipeline import AtlasPipeline


class FakeAPIClient:
    def get(self, endpoint, params=None):
        return {
            "Symbol": "AAPL",
            "Name": "Apple Inc.",
            "Exchange": "NASDAQ",
            "Sector": "TECHNOLOGY",
            "Industry": "CONSUMER ELECTRONICS",
            "Currency": "USD",
            "MarketCapitalization": "3000000000000",
            "Description": "Technology company",
        }


class FakeStorage:
    def __init__(self):
        self.uploaded_data = None
        self.uploaded_key = None

    def upload_json(self, data, key):
        self.uploaded_data = data
        self.uploaded_key = key


def test_ingest_company():
    client = FakeAPIClient()
    company_service = CompanyService(client)
    storage = FakeStorage()

    pipeline = AtlasPipeline(company_service, storage)

    pipeline.ingest_company(
        ticker="AAPL",
    )

    assert storage.uploaded_data["Symbol"] == "AAPL"
    assert storage.uploaded_data["Name"] == "Apple Inc."
