from datetime import date

from atlas.quality.stock_price import StockPriceQualityChecker
from atlas.transformation.stock_price import StockPriceTransformer
from atlas.ingestion.company import CompanyService
from atlas.ingestion.pipeline import AtlasPipeline
from atlas.quality.company import CompanyQualityChecker
from atlas.quality.processor import QualityProcessor
from atlas.transformation.company import CompanyTransformer
from atlas.ingestion.stock_price import StockPriceService

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

    def upload_csv(self, data, key):
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


def test_process_stock_price():
    storage = FakeStorage()

    pipeline = AtlasPipeline(
        company_service=None,
        storage=storage,
        transformer=CompanyTransformer(),
        quality_processor=QualityProcessor(CompanyQualityChecker()),
        stock_price_transformer=StockPriceTransformer(),
        stock_price_quality_processor=QualityProcessor(
            StockPriceQualityChecker()
        ),
    )

    data = [
        {
            "symbol": "AAPL",
            "date": "2026-09-05",
            "open": "240.50",
            "high": "245.20",
            "low": "238.70",
            "close": "243.10",
            "volume": "58123456",
        }
    ]

    stock_price, quarantine = pipeline.process_stock_price(data)

    assert len(stock_price) == 1
    assert stock_price[0].ticker == "AAPL"
    assert stock_price[0].date == date(2026, 9, 5)
    assert stock_price[0].open == 240.50
    assert stock_price[0].high == 245.20
    assert stock_price[0].low == 238.70
    assert stock_price[0].close == 243.10
    assert stock_price[0].volume == 58123456
    assert quarantine == []


def test_process_invalid_stock_price_routes_to_quarantine():
    storage = FakeStorage()

    pipeline = AtlasPipeline(
        company_service=None,
        storage=storage,
        transformer=CompanyTransformer(),
        quality_processor=QualityProcessor(CompanyQualityChecker()),
        stock_price_transformer=StockPriceTransformer(),
        stock_price_quality_processor=QualityProcessor(
            StockPriceQualityChecker()
        ),
    )

    data = [
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

    stock_prices, quarantines = pipeline.process_stock_price(data)

    assert stock_prices == []
    assert len(quarantines) == 1
    assert quarantines[0].ticker == "AAPL"
    assert "high price cannot be lower than open price" in quarantines[0].errors

def test_process_valid_stock_price_stores_processed_record():
    storage = FakeStorage()

    pipeline = AtlasPipeline(
        company_service=None,
        storage=storage,
        transformer=CompanyTransformer(),
        quality_processor=QualityProcessor(CompanyQualityChecker()),
        stock_price_transformer=StockPriceTransformer(),
        stock_price_quality_processor=QualityProcessor(
            StockPriceQualityChecker()
        ),
    )

    data = [
        {
            "symbol": "AAPL",
            "date": "2026-09-05",
            "open": "240.50",
            "high": "245.20",
            "low": "238.70",
            "close": "243.10",
            "volume": "58123456",
        }
    ]

    pipeline.process_and_store_stock_price(data)

    assert storage.uploaded_key.startswith(
        "processed/stock_price/"
    )

    assert storage.uploaded_data[0]["ticker"] == "AAPL"
    assert storage.uploaded_data[0]["date"] == "2026-09-05"
    assert storage.uploaded_data[0]["open"] == 240.50
    assert storage.uploaded_data[0]["high"] == 245.20
    assert storage.uploaded_data[0]["low"] == 238.70
    assert storage.uploaded_data[0]["close"] == 243.10
    assert storage.uploaded_data[0]["volume"] == 58123456


def test_process_invalid_stock_price_stores_quarantine():
    storage = FakeStorage()

    pipeline = AtlasPipeline(
        company_service=None,
        storage=storage,
        transformer=CompanyTransformer(),
        quality_processor=QualityProcessor(CompanyQualityChecker()),
        stock_price_transformer=StockPriceTransformer(),
        stock_price_quality_processor=QualityProcessor(
            StockPriceQualityChecker()
        ),
    )

    data = [
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

    pipeline.process_and_store_stock_price(data)

    assert storage.uploaded_key.startswith(
        "quarantine/stock_price/"
    )

    assert storage.uploaded_data["ticker"] == "AAPL"
    assert storage.uploaded_data["record"]["date"] == "2026-09-05"
    assert "high price cannot be lower than open price" in (
        storage.uploaded_data["errors"]
    )


def test_process_stock_price_from_s3():
    storage = FakeStorage()

    storage.raw_data = [
        {
            "symbol": "AAPL",
            "date": "2026-09-05",
            "open": "240.50",
            "high": "245.20",
            "low": "238.70",
            "close": "243.10",
            "volume": "58123456",
        }
    ]

    pipeline = AtlasPipeline(
        company_service=None,
        storage=storage,
        transformer=CompanyTransformer(),
        quality_processor=QualityProcessor(CompanyQualityChecker()),
        stock_price_transformer=StockPriceTransformer(),
        stock_price_quality_processor=QualityProcessor(
            StockPriceQualityChecker()
        ),
    )

    stock_prices, quarantines = pipeline.process_stock_price_from_s3(
        "raw/stock_price/2026-09-05/AAPL.json"
    )

    assert len(stock_prices) == 1
    assert stock_prices[0].ticker == "AAPL"
    assert stock_prices[0].date == date(2026, 9, 5)
    assert quarantines == []

def test_ingest_stock_price():
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

    client = FakeStockPriceAPIClient()
    stock_price_service = StockPriceService(client)
    storage = FakeStorage()

    storage.raw_data = [
        {
            "symbol": "AAPL",
            "date": "2026-09-05",
            "open": "240.50",
            "high": "245.20",
            "low": "238.70",
            "close": "243.10",
            "volume": "58123456",
        }
    ]

    pipeline = AtlasPipeline(
        company_service=None,
        storage=storage,
        transformer=CompanyTransformer(),
        quality_processor=QualityProcessor(CompanyQualityChecker()),
        stock_price_transformer=StockPriceTransformer(),
        stock_price_quality_processor=QualityProcessor(
            StockPriceQualityChecker()
        ),
        stock_price_service=stock_price_service,
    )

    stock_prices = pipeline.ingest_stock_price("AAPL")

    assert len(stock_prices) == 1
    assert stock_prices[0].ticker == "AAPL"

    assert storage.uploaded_key.startswith(
        "processed/stock_price/"
    )