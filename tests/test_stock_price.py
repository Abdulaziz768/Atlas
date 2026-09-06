from datetime import date

import pytest

from atlas.ingestion.stock_price import StockPriceService
from atlas.quality.stock_price import StockPriceQualityChecker
from atlas.transformation.models import StockPriceRecord
from atlas.transformation.stock_price import StockPriceTransformer


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


def create_stock_price(**overrides):
    data = {
        "ticker": "AAPL",
        "date": date(2026, 9, 4),
        "open": 240.50,
        "high": 245.20,
        "low": 238.70,
        "close": 243.10,
        "volume": 58123456,
    }

    data.update(overrides)
    return StockPriceRecord(**data)


def test_get_stock_price_data():
    service = StockPriceService(FakeStockPriceClient())

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


@pytest.mark.parametrize(
    "volume, expected_volume",
    [
        ("58123456", 58123456),
        ("", None),
    ],
)
def test_stock_price_transformation(volume, expected_volume):
    transformer = StockPriceTransformer()

    data = {
        "symbol": "AAPL",
        "date": "2026-09-04",
        "open": "240.50",
        "high": "245.20",
        "low": "238.70",
        "close": "243.10",
        "volume": volume,
    }

    record = transformer.transform(data)

    assert isinstance(record, StockPriceRecord)
    assert record.ticker == "AAPL"
    assert record.date == date(2026, 9, 4)
    assert record.open == 240.50
    assert record.high == 245.20
    assert record.low == 238.70
    assert record.close == 243.10
    assert record.volume == expected_volume


def test_stock_price_quality_valid_record():
    record = create_stock_price()

    result = StockPriceQualityChecker().check(record)

    assert result.valid is True
    assert result.errors == []


def test_stock_price_quality_missing_required_fields():
    record = create_stock_price(
        ticker="",
        date=None,
        open=None,
        high=None,
        low=None,
        close=None,
        volume=None,
    )

    result = StockPriceQualityChecker().check(record)

    assert result.valid is False
    assert result.errors == [
        "ticker is missing",
        "date is missing",
        "open price is missing",
        "high price is missing",
        "low price is missing",
        "close price is missing",
    ]


def test_stock_price_quality_negative_values():
    record = create_stock_price(
        open=-240.50,
        close=-243.10,
        volume=-100,
    )

    result = StockPriceQualityChecker().check(record)

    assert result.valid is False
    assert "open price cannot be negative" in result.errors
    assert "close price cannot be negative" in result.errors
    assert "volume cannot be negative" in result.errors


def test_stock_price_quality_invalid_high_low_relationship():
    record = create_stock_price(
        high=230.00,
        low=250.00,
    )

    result = StockPriceQualityChecker().check(record)

    assert result.valid is False
    assert "high price cannot be lower than open price" in result.errors
    assert "high price cannot be lower than close price" in result.errors
    assert "low price cannot be higher than open price" in result.errors
    assert "low price cannot be higher than close price" in result.errors