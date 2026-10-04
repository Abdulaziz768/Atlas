import logging

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum, when

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


logger = logging.getLogger(__name__)


def run_stock_price_job(
    spark: SparkSession,
    input_path: str,
    clean_output_path: str,
    quarantine_output_path: str,
) -> None:
    """Process stock price data using PySpark."""

    logger.info("Reading stock price data from: %s", input_path)

    df = read_stock_price(
        spark,
        input_path,
    )

    transformed = transform_stock_price(df)

    counts = (
        transformed
        .agg(
            count("*").alias("input_rows"),
            sum(
                when(col("price_status") == "valid", 1)
                .otherwise(0)
            ).alias("valid_rows"),
        )
        .collect()[0]
    )

    input_rows = counts["input_rows"]
    valid_rows = counts["valid_rows"]
    invalid_rows = input_rows - valid_rows

    logger.info("Stock price transformation completed")
    logger.info("Input rows: %s", input_rows)
    logger.info("Valid rows: %s", valid_rows)
    logger.info("Invalid/quarantined rows: %s", invalid_rows)

    valid, invalid = split_stock_price_quality(
        transformed
    )

    clean = deduplicate_stock_price(valid).drop("price_status")

    clean_rows = clean.count()

    logger.info("Rows after deduplication: %s", clean_rows)

    logger.info("Writing clean data to: %s", clean_output_path)

    write_stock_price_clean(
        clean,
        clean_output_path,
    )

    logger.info("Writing quarantined data to: %s", quarantine_output_path)

    write_stock_price_quarantine(
        invalid,
        quarantine_output_path,
    )

    logger.info("Stock price PySpark processing completed successfully")
