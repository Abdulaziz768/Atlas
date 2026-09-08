from datetime import date

from atlas.transformation.fundamentals import FundamentalsTransformer
from atlas.quality.fundamentals import FundamentalsQualityChecker
from atlas.pipelines.fundamentals import FundamentalsPipeline
from atlas.quality.processor import QualityProcessor


def create_fundamentals_data(**overrides):
    data = {
        "Symbol": "AAPL",
        "Currency": "USD",
        "MarketCapitalization": "4669700047000",
        "PERatio": "36.61",
        "ForwardPE": "33.56",
        "PEGRatio": "2.58",
        "PriceToSalesRatioTTM": "10.0",
        "PriceToBookRatio": "44.55",
        "EVToRevenue": "10.31",
        "EVToEBITDA": "28.65",
        "EPS": "8.74",
        "DilutedEPSTTM": "8.74",
        "RevenueTTM": "466822988000",
        "RevenuePerShareTTM": "31.71",
        "GrossProfitTTM": "227123003000",
        "EBITDA": "167959003000",
        "ProfitMargin": "0.276",
        "OperatingMarginTTM": "0.326",
        "ReturnOnAssetsTTM": "0.271",
        "ReturnOnEquityTTM": "1.488",
        "QuarterlyEarningsGrowthYOY": "0.287",
        "QuarterlyRevenueGrowthYOY": "0.164",
        "DividendPerShare": "1.05",
        "DividendYield": "0.0032",
        "Beta": "1.085",
        "52WeekHigh": "344.27",
        "52WeekLow": "225.12",
        "50DayMovingAverage": "315.15",
        "200DayMovingAverage": "283.87",
        "SharesOutstanding": "14594180000",
        "SharesFloat": "14569078000",
        "PercentInsiders": "1.648",
        "PercentInstitutions": "66.435",
    }

    data.update(overrides)
    return data


def test_fundamentals_transformation():
    record = FundamentalsTransformer(
        as_of_date=date(2026, 9, 8)
    ).transform(create_fundamentals_data())

    assert record.ticker == "AAPL"
    assert record.as_of_date == date(2026, 9, 8)
    assert record.currency == "USD"

    assert record.market_cap == 4669700047000
    assert isinstance(record.market_cap, int)

    assert record.pe_ratio == 36.61
    assert record.forward_pe == 33.56
    assert record.peg_ratio == 2.58

    assert record.revenue_ttm == 466822988000
    assert record.gross_profit_ttm == 227123003000
    assert record.ebitda == 167959003000

    assert record.return_on_assets == 0.271
    assert record.return_on_equity == 1.488

    assert record.week_52_high == 344.27
    assert record.week_52_low == 225.12

    assert record.shares_outstanding == 14594180000
    assert record.percent_institutions == 66.435


def test_fundamentals_transformation_handles_missing_optional_fields():
    data = create_fundamentals_data()

    optional_fields = [
        "MarketCapitalization",
        "PERatio",
        "ForwardPE",
        "PEGRatio",
        "PriceToSalesRatioTTM",
        "PriceToBookRatio",
        "EVToRevenue",
        "EVToEBITDA",
        "EPS",
        "DilutedEPSTTM",
        "RevenueTTM",
        "RevenuePerShareTTM",
        "GrossProfitTTM",
        "EBITDA",
        "ProfitMargin",
        "OperatingMarginTTM",
        "ReturnOnAssetsTTM",
        "ReturnOnEquityTTM",
        "QuarterlyEarningsGrowthYOY",
        "QuarterlyRevenueGrowthYOY",
        "DividendPerShare",
        "DividendYield",
        "Beta",
        "52WeekHigh",
        "52WeekLow",
        "50DayMovingAverage",
        "200DayMovingAverage",
        "SharesOutstanding",
        "SharesFloat",
        "PercentInsiders",
        "PercentInstitutions",
    ]

    for field in optional_fields:
        data.pop(field)

    record = FundamentalsTransformer(
        as_of_date=date(2026, 9, 8)
    ).transform(data)

    assert record.ticker == "AAPL"
    assert record.currency == "USD"
    assert record.market_cap is None
    assert record.pe_ratio is None
    assert record.revenue_ttm is None
    assert record.beta is None
    assert record.shares_outstanding is None

def test_fundamentals_quality_accepts_valid_record():
    record = FundamentalsTransformer(
        as_of_date=date(2026, 9, 6)
    ).transform(create_fundamentals_data())

    result = FundamentalsQualityChecker().check(record)

    assert result.valid is True
    assert result.errors == []


def test_fundamentals_quality_rejects_missing_required_fields():
    record = FundamentalsTransformer(
        as_of_date=date(2026, 9, 6)
    ).transform(create_fundamentals_data())

    record.ticker = ""
    record.currency = ""
    record.as_of_date = None

    result = FundamentalsQualityChecker().check(record)

    assert result.valid is False
    assert "ticker is missing" in result.errors
    assert "currency is missing" in result.errors
    assert "as of date is missing" in result.errors


def test_fundamentals_quality_rejects_invalid_numeric_values():
    record = FundamentalsTransformer(
        as_of_date=date(2026, 9, 6)
    ).transform(create_fundamentals_data())

    record.market_cap = -1
    record.revenue_ttm = -1
    record.pe_ratio = float("inf")

    result = FundamentalsQualityChecker().check(record)

    assert result.valid is False
    assert "market_cap cannot be negative" in result.errors
    assert "revenue_ttm cannot be negative" in result.errors
    assert "pe_ratio must be finite" in result.errors

def test_fundamentals_pipeline_processes_valid_data():
    class FakeStorage:
        def __init__(self):
            self.uploaded_csv = None

        def read_json(self, key):
            return create_fundamentals_data()

        def upload_csv(self, data, key):
            self.uploaded_csv = {
                "data": data,
                "key": key,
            }

        def upload_json(self, data, key):
            raise AssertionError("Quarantine should not be written")

    class FakePaths:
        def fundamentals_processed(self, ticker):
            return f"processed/fundamentals/{ticker}.csv"

        def fundamentals_quarantine(self, ticker):
            return f"quarantine/fundamentals/{ticker}.json"

    storage = FakeStorage()

    pipeline = FundamentalsPipeline(
        transformer=FundamentalsTransformer(
            as_of_date=date(2026, 9, 6)
        ),
        quality_processor=QualityProcessor(
            FundamentalsQualityChecker()
        ),
        storage=storage,
        paths=FakePaths(),
    )

    result = pipeline.process_from_s3(
        "raw/company_overview/AAPL.json"
    )

    assert result is not None
    assert result.ticker == "AAPL"

    assert storage.uploaded_csv["key"] == (
        "processed/fundamentals/AAPL.csv"
    )

    assert storage.uploaded_csv["data"][0]["ticker"] == "AAPL"

def test_fundamentals_pipeline_quarantines_invalid_data():
    class FakeStorage:
        def __init__(self):
            self.uploaded_json = None
            self.uploaded_csv = None

        def read_json(self, key):
            return create_fundamentals_data(
                MarketCapitalization="-1"
            )

        def upload_json(self, data, key):
            self.uploaded_json = {
                "data": data,
                "key": key,
            }

        def upload_csv(self, data, key):
            self.uploaded_csv = {
                "data": data,
                "key": key,
            }

    class FakePaths:
        def fundamentals_processed(self, ticker):
            return f"processed/fundamentals/{ticker}.csv"

        def fundamentals_quarantine(self, ticker):
            return f"quarantine/fundamentals/{ticker}.json"

    storage = FakeStorage()

    pipeline = FundamentalsPipeline(
        transformer=FundamentalsTransformer(
            as_of_date=date(2026, 9, 8)
        ),
        quality_processor=QualityProcessor(
            FundamentalsQualityChecker()
        ),
        storage=storage,
        paths=FakePaths(),
    )

    result = pipeline.process_from_s3(
        "raw/company_overview/AAPL.json"
    )

    assert result is None

    assert storage.uploaded_csv is None

    assert storage.uploaded_json["key"] == (
        "quarantine/fundamentals/AAPL.json"
    )

    assert storage.uploaded_json["data"]["ticker"] == "AAPL"
    assert "market_cap cannot be negative" in (
        storage.uploaded_json["data"]["errors"]
    )