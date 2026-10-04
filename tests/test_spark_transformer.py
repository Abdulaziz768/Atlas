from datetime import datetime, timezone

import pytest

from pyspark.sql.types import (
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from atlas.spark.session import create_spark_session
from atlas.spark.transformer import (
    deduplicate_stock_price,
    split_stock_price_quality,
    transform_stock_price,
)


test_schema = StructType([
    StructField("ticker", StringType(), True),
    StructField("date", StringType(), True),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("volume", LongType(), True),
])


test_schema_with_ingestion_time = StructType([
    StructField("ticker", StringType(), True),
    StructField("date", StringType(), True),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("volume", LongType(), True),
    StructField("ingestion_time", TimestampType(), True),
])


@pytest.fixture(scope="module")
def spark():
    spark = create_spark_session()
    yield spark
    spark.stop()


@pytest.mark.parametrize(
    "data, expected_status",
    [
        (
            ("AAPL", "2026-09-11", -10.00, 336.22, 326.30, 332.27, 50716865),
            "invalid",
        ),
        (
            ("AAPL", "2026-09-11", 327.45, -10.00, 326.30, 332.27, 50716865),
            "invalid",
        ),
        (
            ("AAPL", "2026-09-11", 327.45, 336.22, -10.00, 332.27, 50716865),
            "invalid",
        ),
        (
            ("AAPL", "2026-09-11", 327.45, 336.22, 326.30, -10.00, 50716865),
            "invalid",
        ),
        (
            ("AAPL", "2026-09-11", 327.45, 336.22, 326.30, 332.27, -100),
            "invalid",
        ),
        (
            ("AAPL", "2026-09-11", 340.00, 336.22, 326.30, 332.27, 50716865),
            "invalid",
        ),
        (
            ("AAPL", "2026-09-11", 327.45, 336.22, 326.30, 340.00, 50716865),
            "invalid",
        ),
        (
            ("AAPL", "2026-09-11", 320.00, 336.22, 326.30, 332.27, 50716865),
            "invalid",
        ),
        (
            ("AAPL", "2026-09-11", 327.45, 336.22, 340.00, 332.27, 50716865),
            "invalid",
        ),
        (
            ("AAPL", "2026-09-11", 327.45, 336.22, 326.30, 332.27, 50716865),
            "valid",
        ),
        (
            (None, "2026-09-11", 327.45, 336.22, 326.30, 332.27, 50716865),
            "invalid",
        ),
        (
            ("AAPL", None, 327.45, 336.22, 326.30, 332.27, 50716865),
            "invalid",
        ),
        (
            ("AAPL", "2026-09-11", None, 336.22, 326.30, 332.27, 50716865),
            "invalid",
        ),
        (
            ("AAPL", "2026-09-11", 327.45, None, 326.30, 332.27, 50716865),
            "invalid",
        ),
        (
            ("AAPL", "2026-09-11", 327.45, 336.22, None, 332.27, 50716865),
            "invalid",
        ),
        (
            ("AAPL", "2026-09-11", 327.45, 336.22, 326.30, None, 50716865),
            "invalid",
        ),
        (
            ("AAPL", "2026-09-11", 327.45, 336.22, 326.30, 332.27, None),
            "valid",
        ),
    ],
)
def test_transform_stock_price(data, expected_status, spark):
    df = spark.createDataFrame(
        [data],
        test_schema,
    )

    transformed = transform_stock_price(df)

    row = transformed.collect()[0]

    assert row["price_status"] == expected_status


def test_split_stock_price_quality(spark):
    data = [
        (
            "AAPL",
            "2026-09-11",
            327.45,
            336.22,
            326.30,
            332.27,
            50716865,
        ),
        (
            "AAPL",
            "2026-09-10",
            -10.00,
            326.74,
            316.51,
            326.57,
            70011913,
        ),
    ]

    df = spark.createDataFrame(
        data,
        test_schema,
    )

    transformed = transform_stock_price(df)

    valid, invalid = split_stock_price_quality(transformed)

    assert valid.count() == 1
    assert invalid.count() == 1

    valid_row = valid.collect()[0]
    invalid_row = invalid.collect()[0]

    assert valid_row["ticker"] == "AAPL"
    assert valid_row["date"] == "2026-09-11"

    assert invalid_row["ticker"] == "AAPL"
    assert invalid_row["date"] == "2026-09-10"

def test_deduplicate_stock_price_keeps_latest_ingestion(spark):
    data = [
        (
            "AAPL",
            "2026-09-11",
            327.45,
            336.22,
            326.30,
            332.27,
            50716865,
            datetime(2026, 9, 12, 5, 0, tzinfo=timezone.utc),
        ),
        (
            "AAPL",
            "2026-09-11",
            328.00,
            337.00,
            327.00,
            333.00,
            51000000,
            datetime(2026, 9, 12, 6, 0, tzinfo=timezone.utc),
        ),
    ]

    df = spark.createDataFrame(
        data,
        test_schema_with_ingestion_time,
    )

    result = deduplicate_stock_price(df)

    row = result.selectExpr(
        "close",
        "unix_timestamp(ingestion_time) as ingestion_timestamp",
    ).collect()[0]

    assert row["close"] == 333.00

    assert row["ingestion_timestamp"] == int(
        datetime(
            2026,
            9,
            12,
            6,
            0,
            tzinfo=timezone.utc,
        ).timestamp()
    )


def test_quality_before_deduplication_keeps_valid_older_record(spark):
    data = [
        (
            "AAPL",
            "2026-09-11",
            327.45,
            336.22,
            326.30,
            332.27,
            50716865,
            datetime(2026, 9, 12, 5, 0, tzinfo=timezone.utc),
        ),
        (
            "AAPL",
            "2026-09-11",
            327.45,
            336.22,
            326.30,
            -10.00,
            50716865,
            datetime(2026, 9, 12, 6, 0, tzinfo=timezone.utc),
        ),
    ]

    df = spark.createDataFrame(
        data,
        test_schema_with_ingestion_time,
    )

    transformed = transform_stock_price(df)

    valid, invalid = split_stock_price_quality(transformed)

    result = deduplicate_stock_price(valid)

    assert valid.count() == 1
    assert invalid.count() == 1

    row = result.selectExpr(
        "ticker",
        "date",
        "close",
        "unix_timestamp(ingestion_time) as ingestion_timestamp",
    ).collect()[0]

    assert row["ticker"] == "AAPL"
    assert row["date"] == "2026-09-11"
    assert row["close"] == 332.27

    assert row["ingestion_timestamp"] == int(
        datetime(
            2026,
            9,
            12,
            5,
            0,
            tzinfo=timezone.utc,
        ).timestamp()
    )


def test_transform_stock_price_fingerprint(spark):
    data = [
        (
            "A",
            "2026-09-20",
            100.123,
            105.50,
            99.80,
            103.25,
            1000,
        ),
        (
            "B",
            "2026-09-20",
            100.124,
            105.50,
            99.80,
            103.25,
            1000,
        ),
        (
            "C",
            "2026-09-20",
            100.130,
            105.50,
            99.80,
            103.25,
            1000,
        ),
    ]

    df = spark.createDataFrame(
        data,
        test_schema,
    )

    transformed = transform_stock_price(df)

    rows = transformed.select(
        "ticker",
        "fingerprint",
    ).collect()

    fingerprints = {
        row["ticker"]: row["fingerprint"]
        for row in rows
    }

    assert fingerprints["A"] == fingerprints["B"]
    assert fingerprints["A"] != fingerprints["C"]


def test_fingerprint_survives_quality_and_deduplication(spark):
    data = [
        (
            "AAPL",
            "2026-09-20",
            100.123,
            105.50,
            99.80,
            103.25,
            1000,
            datetime(2026, 9, 20, 10, 0, tzinfo=timezone.utc),
        ),
        (
            "AAPL",
            "2026-09-20",
            100.13,
            105.50,
            99.80,
            103.25,
            1000,
            datetime(2026, 9, 20, 11, 0, tzinfo=timezone.utc),
        ),
        (
            "AAPL",
            "2026-09-20",
            100.13,
            105.50,
            99.80,
            103.25,
            1000,
            datetime(2026, 9, 20, 12, 0, tzinfo=timezone.utc),
        ),
    ]

    df = spark.createDataFrame(
        data,
        test_schema_with_ingestion_time,
    )

    transformed = transform_stock_price(df)

    valid, invalid = split_stock_price_quality(transformed)

    clean = deduplicate_stock_price(valid).drop("price_status")

    assert valid.count() == 3
    assert invalid.count() == 0
    assert clean.count() == 1

    row = clean.selectExpr(
        "ticker",
        "date",
        "unix_timestamp(ingestion_time) as ingestion_timestamp",
        "fingerprint",
    ).collect()[0]

    assert row["ticker"] == "AAPL"
    assert row["date"] == "2026-09-20"

    assert row["ingestion_timestamp"] == int(
        datetime(
            2026,
            9,
            20,
            12,
            0,
            tzinfo=timezone.utc,
        ).timestamp()
    )

    assert row["fingerprint"] is not None

