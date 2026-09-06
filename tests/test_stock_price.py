from datetime import date

from atlas.transformation.models import StockPriceRecord
from atlas.transformation.stock_price import StockPriceTransformer

from atlas.quality.processor import QualityProcessor
from atlas.quality.stock_price import StockPriceQualityChecker

from atlas.ingestion.stock_price import StockPriceService


class FakeStockPriceClient:

    def get(self, endpoint, params=None):
        return {
            "Time Series (Daily)": {
                "2026-09-05": {
                    "1. open": "240.50",
                    "2. high": "245.20",
                    "3. low": "238.70",
                    "4. close": "243.10",
                    "5. volume": "58123456",
                },
                "2026-09-04": {
                    "1. open": "239.10",
                    "2. high": "242.30",
                    "3. low": "237.80",
                    "4. close": "240.20",
                    "5. volume": "51234567",
                },
            }
        }


def test_get_stock_price_data():
    client = FakeStockPriceClient()
    service = StockPriceService(client)

    records = service.get_stock_price_data("AAPL")

    assert len(records) == 2

    assert records[0] == {
        "symbol": "AAPL",
        "date": "2026-09-05",
        "open": "240.50",
        "high": "245.20",
        "low": "238.70",
        "close": "243.10",
        "volume": "58123456",
    }

    assert records[1]["symbol"] == "AAPL"
    assert records[1]["date"] == "2026-09-04"
    
def test_stock_price_record():
    record = StockPriceRecord(
        ticker="AAPL",
        date=date(2026, 9, 4),
        open=240.50,
        high=245.20,
        low=238.70,
        close=243.10,
        volume=58123456,
    )

    assert record.ticker == "AAPL"
    assert record.date == date(2026, 9, 4)
    assert record.open == 240.50
    assert record.high == 245.20
    assert record.low == 238.70
    assert record.close == 243.10
    assert record.volume == 58123456

def test_stock_price_transformation():
    transformer = StockPriceTransformer()

    data = {
        "symbol": "AAPL",
        "date": "2026-09-04",
        "open": "240.50",
        "high": "245.20",
        "low": "238.70",
        "close": "243.10",
        "volume": "58123456",
    }

    record = transformer.transform(data)

    assert isinstance(record, StockPriceRecord)
    assert record.ticker == "AAPL"
    assert record.date == date(2026, 9, 4)
    assert record.open == 240.50
    assert record.high == 245.20
    assert record.low == 238.70
    assert record.close == 243.10
    assert record.volume == 58123456

def test_stock_price_transformation_handles_missing_volume():
    transformer = StockPriceTransformer()

    data = {
        "symbol": "AAPL",
        "date": "2026-09-04",
        "open": "240.50",
        "high": "245.20",
        "low": "238.70",
        "close": "243.10",
        "volume": "",
    }

    record = transformer.transform(data)

    assert record.volume is None

def test_stock_price_quality_valid_record():
    record = StockPriceRecord(
        ticker="AAPL",
        date=date(2026, 9, 4),
        open=240.50,
        high=245.20,
        low=238.70,
        close=243.10,
        volume=58123456,
    )

    checker = StockPriceQualityChecker()
    result = checker.check(record)

    assert result.valid is True
    assert result.errors == []


def test_stock_price_quality_missing_volume_is_valid():
    record = StockPriceRecord(
        ticker="AAPL",
        date=date(2026, 9, 4),
        open=240.50,
        high=245.20,
        low=238.70,
        close=243.10,
        volume=None,
    )

    checker = StockPriceQualityChecker()
    result = checker.check(record)

    assert result.valid is True
    assert result.errors == []


def test_stock_price_quality_negative_values():
    record = StockPriceRecord(
        ticker="AAPL",
        date=date(2026, 9, 4),
        open=-240.50,
        high=245.20,
        low=238.70,
        close=-243.10,
        volume=-100,
    )

    checker = StockPriceQualityChecker()
    result = checker.check(record)

    assert result.valid is False
    assert "open price cannot be negative" in result.errors
    assert "close price cannot be negative" in result.errors
    assert "volume cannot be negative" in result.errors


def test_stock_price_quality_invalid_high_low_relationship():
    record = StockPriceRecord(
        ticker="AAPL",
        date=date(2026, 9, 4),
        open=240.50,
        high=230.00,
        low=250.00,
        close=243.10,
        volume=58123456,
    )

    checker = StockPriceQualityChecker()
    result = checker.check(record)

    assert result.valid is False
    assert "high price cannot be lower than open price" in result.errors
    assert "high price cannot be lower than close price" in result.errors
    assert "low price cannot be higher than open price" in result.errors
    assert "low price cannot be higher than close price" in result.errors


def test_stock_price_quality_missing_required_fields():
    record = StockPriceRecord(
        ticker="",
        date=None,
        open=None,
        high=None,
        low=None,
        close=None,
        volume=None,
    )

    checker = StockPriceQualityChecker()
    result = checker.check(record)

    assert result.valid is False
    assert "ticker is missing" in result.errors
    assert "date is missing" in result.errors
    assert "open price is missing" in result.errors
    assert "high price is missing" in result.errors
    assert "low price is missing" in result.errors
    assert "close price is missing" in result.errors

def test_stock_price_quality_processor_returns_valid_record():
    record = StockPriceRecord(
        ticker="AAPL",
        date=date(2026, 9, 4),
        open=240.50,
        high=245.20,
        low=238.70,
        close=243.10,
        volume=58123456,
    )

    processor = QualityProcessor(
        StockPriceQualityChecker()
    )

    valid_record, quarantine = processor.process(record)

    assert valid_record == record
    assert quarantine is None

def test_stock_price_quality_processor_quarantines_invalid_record():
    record = StockPriceRecord(
        ticker="AAPL",
        date=date(2026, 9, 4),
        open=240.50,
        high=230.00,
        low=238.70,
        close=243.10,
        volume=58123456,
    )

    processor = QualityProcessor(
        StockPriceQualityChecker()
    )

    valid_record, quarantine = processor.process(record)

    assert valid_record is None
    assert quarantine is not None
    assert quarantine.ticker == "AAPL"
    assert "high price cannot be lower than open price" in quarantine.errors
    assert quarantine.record == record