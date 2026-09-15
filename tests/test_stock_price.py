from datetime import date, datetime

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
    "ingestion_time": datetime(2026, 9, 12, 5, 0, 0),
    }


    data.update(overrides)
    return StockPriceRecord(**data)


def test_get_stock_price_data():
    service = StockPriceService(FakeStockPriceClient())


    records = service.get_stock_price_data("AAPL")

    assert len(records) == 2
    assert records[0]["symbol"] == "AAPL"
    assert records[0]["date"] == "2026-09-05"
    assert records[0]["open"] == "240.50"
    assert records[0]["volume"] == "58123456"
    assert isinstance(records[0]["ingestion_time"], datetime)

    assert records[1]["symbol"] == "AAPL"
    assert records[1]["date"] == "2026-09-04"
    assert records[1]["ingestion_time"] == records[0]["ingestion_time"]


@pytest.mark.parametrize(
"volume, expected_volume",
[
("58123456", 58123456),
("", None),
],
)
def test_stock_price_transformation(volume, expected_volume):
    ingestion_time = datetime(2026, 9, 12, 5, 0, 0)


    data = {
        "symbol": "AAPL",
        "date": "2026-09-04",
        "open": "240.50",
        "high": "245.20",
        "low": "238.70",
        "close": "243.10",
        "volume": volume,
        "ingestion_time": ingestion_time,
    }

    record = StockPriceTransformer().transform(data)

    assert isinstance(record, StockPriceRecord)
    assert record.ticker == "AAPL"
    assert record.date == date(2026, 9, 4)
    assert record.open == 240.50
    assert record.high == 245.20
    assert record.low == 238.70
    assert record.close == 243.10
    assert record.volume == expected_volume
    assert record.ingestion_time == ingestion_time


def test_stock_price_quality_valid_record():
    result = StockPriceQualityChecker().check(create_stock_price())


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


@pytest.mark.parametrize(
"overrides, expected_error",
[
({"open": -240.50}, "open price cannot be negative"),
({"close": -243.10}, "close price cannot be negative"),
({"volume": -100}, "volume cannot be negative"),
],
)
def test_stock_price_quality_negative_values(overrides, expected_error):
    result = StockPriceQualityChecker().check(
    create_stock_price(**overrides)
    )


    assert result.valid is False
    assert expected_error in result.errors


def test_stock_price_quality_invalid_high_low_relationship():
    result = StockPriceQualityChecker().check(
    create_stock_price(
    high=230.00,
    low=250.00,
    )
    )


    assert result.valid is False
    assert result.errors == [
        "high price cannot be lower than open price",
        "high price cannot be lower than close price",
        "low price cannot be higher than open price",
        "low price cannot be higher than close price",
    ]
