from datetime import datetime

import pytest

from atlas.spark.session import create_spark_session
from atlas.spark.transformer import (
    split_stock_price_quality,
    transform_stock_price,
)
from atlas.spark.writer import write_stock_price_quarantine


test_data = [
    (
        "AAPL",
        "2026-09-11",
        327.45,
        336.22,
        326.30,
        -10.00,
        50716865,
        datetime(2026, 9, 12, 5, 33, 10),
    ),
]


test_columns = [
    "ticker",
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "ingestion_time",
]


@pytest.fixture(scope="module")
def spark():
    spark = create_spark_session()
    yield spark
    spark.stop()


def test_invalid_stock_price_is_written_to_quarantine(
    spark,
    tmp_path,
):
    df = spark.createDataFrame(
        test_data,
        test_columns,
    )

    transformed = transform_stock_price(df)

    valid, invalid = split_stock_price_quality(
        transformed
    )

    assert valid.count() == 0
    assert invalid.count() == 1

    output_path = str(
        tmp_path / "quarantine"
    )

    write_stock_price_quarantine(
        invalid,
        output_path,
    )

    result = spark.read.json(output_path)

    assert result.count() == 1

    row = result.first()

    assert row["ticker"] == "AAPL"
    assert row["close"] == -10.00
    assert row["price_status"] == "invalid"