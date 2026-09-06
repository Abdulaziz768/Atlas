from datetime import date

from atlas.ingestion.company import CompanyService
from atlas.ingestion.stock_price import StockPriceService
from atlas.pipelines.company import CompanyPipeline
from atlas.pipelines.stock_price import StockPricePipeline
from atlas.quality.company import CompanyQualityChecker
from atlas.quality.processor import QualityProcessor
from atlas.quality.stock_price import StockPriceQualityChecker
from atlas.storage.paths import S3PathBuilder
from atlas.transformation.company import CompanyTransformer
from atlas.transformation.stock_price import StockPriceTransformer


class FakeStorage:

    def __init__(self):
        self.uploaded_data = None
        self.uploaded_key = None
        self.raw_data = None

    def upload_json(self, data, key):
        self.uploaded_data = data
        self.uploaded_key = key
        self.raw_data = data
        
    def upload_csv(self, data, key):
        self.uploaded_data = data
        self.uploaded_key = key

    def read_json(self, key):
        return self.raw_data


class FakeCompanyAPIClient:

    def get(self, endpoint, params=None):
        return {
            "Symbol": "AAPL",
            "Name": "Apple Inc.",
            "Exchange": "NASDAQ",
            "Sector": "TECHNOLOGY",
            "Industry": "CONSUMER ELECTRONICS",
            "Currency": "USD",
            "MarketCapitalization": "3000000000000",
        }


class FakeStockPriceAPIClient:

    def get(self, endpoint, params=None):
        return {
            "Time Series (Daily)": {
                "2026-09-05": {
                    "1. open": "240.50",
                    "2. high": "245.20",
                    "3. low": "238.70",
                    "4. close": "243.10",
                    "5. volume": "58123456",
                }
            }
        }


def create_company_pipeline(storage):
    return CompanyPipeline(
        service=CompanyService(FakeCompanyAPIClient()),
        transformer=CompanyTransformer(),
        quality_processor=QualityProcessor(
            CompanyQualityChecker()
        ),
        storage=storage,
        paths=S3PathBuilder(
            processing_date=date(2026, 9, 5)
        ),
    )


def create_stock_price_pipeline(storage):
    return StockPricePipeline(
        service=StockPriceService(FakeStockPriceAPIClient()),
        transformer=StockPriceTransformer(),
        quality_processor=QualityProcessor(
            StockPriceQualityChecker()
        ),
        storage=storage,
        paths=S3PathBuilder(
            processing_date=date(2026, 9, 5)
        ),
    )


def test_company_pipeline_stores_valid_company():
    storage = FakeStorage()
    pipeline = create_company_pipeline(storage)

    company = pipeline.ingest("AAPL")

    assert company.ticker == "AAPL"
    assert company.name == "Apple Inc."

    assert storage.uploaded_key == (
        "processed/company_overview/2026-09-05/AAPL.json"
    )

    assert storage.uploaded_data["ticker"] == "AAPL"
    assert storage.uploaded_data["market_cap"] == 3000000000000


def test_company_pipeline_quarantines_invalid_company():
    storage = FakeStorage()
    pipeline = create_company_pipeline(storage)

    storage.raw_data = {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
        "Exchange": "NASDAQ",
        "Sector": "TECHNOLOGY",
        "Industry": "CONSUMER ELECTRONICS",
        "Currency": "USD",
        "MarketCapitalization": "-1000000",
    }

    result = pipeline.process_from_s3(
        "raw/company_overview/2026-09-05/AAPL.json"
    )

    assert result is None

    assert storage.uploaded_key == (
        "quarantine/company_overview/2026-09-05/AAPL.json"
    )

    assert storage.uploaded_data["ticker"] == "AAPL"
    assert storage.uploaded_data["errors"] == [
        "market cap cannot be negative"
    ]


def test_stock_price_pipeline_stores_valid_records():
    storage = FakeStorage()
    pipeline = create_stock_price_pipeline(storage)

    stock_prices = pipeline.ingest("AAPL")

    assert len(stock_prices) == 1

    record = stock_prices[0]

    assert record.ticker == "AAPL"
    assert record.date == date(2026, 9, 5)
    assert record.open == 240.50
    assert record.close == 243.10
    assert record.volume == 58123456

    assert storage.uploaded_key == (
        "processed/stock_price/2026-09-05/AAPL.csv"
    )

    assert storage.uploaded_data[0]["ticker"] == "AAPL"
    assert storage.uploaded_data[0]["date"] == "2026-09-05"


def test_stock_price_pipeline_quarantines_invalid_records():
    storage = FakeStorage()
    pipeline = create_stock_price_pipeline(storage)

    storage.raw_data = [
        {
            "symbol": "AAPL",
            "date": "2026-09-05",
            "open": "240.50",
            "high": "230.20",
            "low": "238.70",
            "close": "243.10",
            "volume": "58123456",
        }
    ]

    result = pipeline.process_from_s3(
        "raw/stock_price/2026-09-05/AAPL.json"
    )

    assert result == []

    assert storage.uploaded_key == (
        "quarantine/stock_price/2026-09-05/AAPL.json"
    )

    assert storage.uploaded_data["ticker"] == "AAPL"
    assert storage.uploaded_data["record"]["date"] == "2026-09-05"
    assert "high price cannot be lower than open price" in (
        storage.uploaded_data["errors"]
    )