from pyspark.sql import DataFrame, SparkSession

from pyspark.sql.types import (
    DateType,
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

stock_price_schema = StructType([
    StructField("ticker", StringType(), False),
    StructField("date", DateType(), False),
    StructField("open", DoubleType(), False),
    StructField("high", DoubleType(), False),
    StructField("low", DoubleType(), False),
    StructField("close", DoubleType(), False),
    StructField("volume", LongType(), True),
    StructField("ingestion_time", TimestampType(), False),
])


def read_stock_price(
        spark: SparkSession,
        path: str,
) -> DataFrame:

    return (
        spark.read
        .schema(stock_price_schema)
        .option("header", True)
        .csv(path)
    )