from pyspark.sql import SparkSession

from atlas.spark.reader import read_stock_price
from atlas.spark.transformer import (
    deduplicate_stock_price,
    split_stock_price_quality,
    transform_stock_price,
)
from atlas.spark.writer import (
    write_stock_price_clean,
    write_stock_price_quarantine,
)


def run_stock_price_job(
    spark: SparkSession,
    input_path: str,
    clean_output_path: str,
    quarantine_output_path: str,
) -> None:
    """Process stock price data using PySpark."""

    df = read_stock_price(
        spark,
        input_path,
    )

    transformed = transform_stock_price(df)

    valid, invalid = split_stock_price_quality(
        transformed
    )

    clean = deduplicate_stock_price(valid).drop("price_status")
    
    write_stock_price_clean(
        clean,
        clean_output_path,
    )

    write_stock_price_quarantine(
        invalid,
        quarantine_output_path,
    )