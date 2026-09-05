from atlas.ingestion.company import CompanyService
from atlas.ingestion.pipeline import AtlasPipeline
from atlas.quality.company import CompanyQualityChecker
from atlas.quality.processor import QualityProcessor
from atlas.transformation.company import CompanyTransformer

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



def test_ingest_company():
    client = FakeAPIClient()
    company_service = CompanyService(client)
    storage = FakeStorage()

    storage.raw_data = {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
        "Exchange": "NASDAQ",
        "Sector": "TECHNOLOGY",
        "Industry": "CONSUMER ELECTRONICS",
        "Currency": "USD",
        "MarketCapitalization": "3000000000000",
    }

    pipeline = AtlasPipeline(
        company_service,
        storage,
        transformer=CompanyTransformer(),
        quality_processor=QualityProcessor(CompanyQualityChecker()),
    )

    company = pipeline.ingest_company("AAPL")

    assert company.ticker == "AAPL"
    assert company.name == "Apple Inc."

def test_process_company_routes_valid_company():
    transformer = CompanyTransformer()
    quality_processor = QualityProcessor(CompanyQualityChecker())

    pipeline = AtlasPipeline(
        company_service=None,
        storage=None,
        transformer=transformer,
        quality_processor=quality_processor,
    )

    data = {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
        "Exchange": "NASDAQ",
        "Sector": "TECHNOLOGY",
        "Industry": "CONSUMER ELECTRONICS",
        "Currency": "USD",
        "MarketCapitalization": "3000000000000",
        "EBITDA": "167959003000",
        "PERatio": "37.31",
        "EPS": "8.71",
        "RevenueTTM": "466822988000",
        "ProfitMargin": "0.276",
        "OperatingMarginTTM": "0.326",
        "ReturnOnEquityTTM": "1.488",
        "Beta": "1.086",
    }

    company, quarantine = pipeline.process_company(data)

    assert company.ticker == "AAPL"
    assert quarantine is None

def test_process_company_routes_invalid_company_to_quarantine():
    transformer = CompanyTransformer()
    quality_processor = QualityProcessor(CompanyQualityChecker())

    pipeline = AtlasPipeline(
        company_service=None,
        storage=None,
        transformer=transformer,
        quality_processor=quality_processor,
    )

    data = {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
        "Exchange": "NASDAQ",
        "Sector": "TECHNOLOGY",
        "Industry": "CONSUMER ELECTRONICS",
        "Currency": "USD",
        "MarketCapitalization": "-1000000",
        "EBITDA": "167959003000",
        "PERatio": "37.31",
        "EPS": "8.71",
        "RevenueTTM": "466822988000",
        "ProfitMargin": "0.276",
        "OperatingMarginTTM": "0.326",
        "ReturnOnEquityTTM": "1.488",
        "Beta": "1.086",
    }

    company, quarantine = pipeline.process_company(data)

    assert company is None
    assert quarantine.ticker == "AAPL"
    assert quarantine.errors == ["market cap cannot be negative"]

def test_process_invalid_company_stores_quarantine():
    client = FakeAPIClient()
    company_service = CompanyService(client)
    storage = FakeStorage()

    pipeline = AtlasPipeline(
        company_service=company_service,
        storage=storage,
        transformer=CompanyTransformer(),
        quality_processor=QualityProcessor(CompanyQualityChecker()),
    )

    invalid_data = {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
        "Exchange": "NASDAQ",
        "Sector": "TECHNOLOGY",
        "Industry": "CONSUMER ELECTRONICS",
        "Currency": "USD",
        "MarketCapitalization": "-1000000",
        "EBITDA": "167959003000",
        "PERatio": "37.31",
        "EPS": "8.71",
        "RevenueTTM": "466822988000",
        "ProfitMargin": "0.276",
        "OperatingMarginTTM": "0.326",
        "ReturnOnEquityTTM": "1.488",
        "Beta": "1.086",
    }

    pipeline.process_and_store_company(invalid_data)

    assert storage.uploaded_data["ticker"] == "AAPL"
    assert storage.uploaded_data["errors"] == [
        "market cap cannot be negative"
    ]

class FakeStorage:

    def __init__(self):
        self.uploaded_data = None
        self.uploaded_key = None
        self.raw_data = None

    def upload_json(self, data, key):
        self.uploaded_data = data
        self.uploaded_key = key

    def read_json(self, key):
        return self.raw_data

def test_process_company_from_s3():
    client = FakeAPIClient()
    company_service = CompanyService(client)
    storage = FakeStorage()

    storage.raw_data = {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
        "Exchange": "NASDAQ",
        "Sector": "TECHNOLOGY",
        "Industry": "CONSUMER ELECTRONICS",
        "Currency": "USD",
        "MarketCapitalization": "3000000000000",
    }

    pipeline = AtlasPipeline(
        company_service,
        storage,
        transformer=CompanyTransformer(),
        quality_processor=QualityProcessor(CompanyQualityChecker()),
    )

    company, quarantine = pipeline.process_from_s3("raw/company_overview/2026-09-05/AAPL.json")

    assert company.ticker == "AAPL"
    assert company.name == "Apple Inc."
    assert quarantine is None

def test_ingest_company_processes_data_from_s3():
    client = FakeAPIClient()
    company_service = CompanyService(client)
    storage = FakeStorage()

    storage.raw_data = {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
        "Exchange": "NASDAQ",
        "Sector": "TECHNOLOGY",
        "Industry": "CONSUMER ELECTRONICS",
        "Currency": "USD",
        "MarketCapitalization": "3000000000000",
    }

    pipeline = AtlasPipeline(
        company_service=company_service,
        storage=storage,
        transformer=CompanyTransformer(),
        quality_processor=QualityProcessor(CompanyQualityChecker()),
    )

    company = pipeline.ingest_company("AAPL")

    assert company.ticker == "AAPL"
    assert company.name == "Apple Inc."

def test_process_valid_company_stores_processed_record():
    storage = FakeStorage()

    pipeline = AtlasPipeline(
        company_service=None,
        storage=storage,
        transformer=CompanyTransformer(),
        quality_processor=QualityProcessor(CompanyQualityChecker()),
    )

    data = {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
        "Exchange": "NASDAQ",
        "Sector": "TECHNOLOGY",
        "Industry": "CONSUMER ELECTRONICS",
        "Currency": "USD",
        "MarketCapitalization": "3000000000000",
    }

    pipeline.process_and_store_company(data)

    assert storage.uploaded_key.startswith(
        "processed/company_overview/"
    )

    assert storage.uploaded_data["ticker"] == "AAPL"
    assert storage.uploaded_data["name"] == "Apple Inc."
    assert storage.uploaded_data["market_cap"] == 3000000000000

def test_ingest_company_stores_processed_record():
    client = FakeAPIClient()
    company_service = CompanyService(client)
    storage = FakeStorage()

    storage.raw_data = {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
        "Exchange": "NASDAQ",
        "Sector": "TECHNOLOGY",
        "Industry": "CONSUMER ELECTRONICS",
        "Currency": "USD",
        "MarketCapitalization": "3000000000000",
    }

    pipeline = AtlasPipeline(
        company_service=company_service,
        storage=storage,
        transformer=CompanyTransformer(),
        quality_processor=QualityProcessor(CompanyQualityChecker()),
    )

    pipeline.ingest_company("AAPL")

    assert storage.uploaded_key.startswith(
        "processed/company_overview/"
    )

    assert storage.uploaded_data["ticker"] == "AAPL"
    assert storage.uploaded_data["name"] == "Apple Inc."
    assert storage.uploaded_data["market_cap"] == 3000000000000