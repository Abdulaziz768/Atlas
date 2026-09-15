from datetime import datetime

import pytest

from atlas.spark.session import create_spark_session
from atlas.spark.writer import (
    write_stock_price_processed,
    write_stock_price_quarantine,
)


@pytest.fixture(scope="module")
def spark():
    spark = create_spark_session()
    yield spark
    spark.stop()


def test_write_stock_price_processed(spark, tmp_path):
    data = [
        (
            "AAPL",
            datetime(2026, 9, 11),
            327.45,
            336.22,
            326.30,
            332.27,
            50716865,
            datetime(2026, 9, 12, 5, 33, 10),
        ),
    ]

    columns = [
        "ticker",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "ingestion_time",
    ]

    df = spark.createDataFrame(data, columns)

    output_path = str(tmp_path / "processed")

    write_stock_price_processed(
        df,
        output_path,
    )

    result = spark.read.option(
        "header",
        True,
    ).csv(output_path)

    assert result.count() == 1
    assert result.first()["ticker"] == "AAPL"


def test_write_stock_price_quarantine(spark, tmp_path):
    data = [
        (
            "AAPL",
            datetime(2026, 9, 11),
            327.45,
            336.22,
            326.30,
            -10.00,
            50716865,
            datetime(2026, 9, 12, 5, 33, 10),
        ),
    ]

    columns = [
        "ticker",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "ingestion_time",
    ]

    df = spark.createDataFrame(data, columns)

    output_path = str(tmp_path / "quarantine")

    write_stock_price_quarantine(
        df,
        output_path,
    )

    result = spark.read.json(output_path)

    assert result.count() == 1
    assert result.first()["ticker"] == "AAPL"
    assert result.first()["close"] == -10.00