from pyspark.sql import DataFrame


def write_stock_price_clean(
    df: DataFrame,
    path: str,
) -> None:
    """Write clean stock price data to S3 as CSV."""

    (
        df.write
        .mode("overwrite")
        .option("header", True)
        .csv(path)
    )


def write_stock_price_quarantine(
    df: DataFrame,
    path: str,
) -> None:
    """Write invalid stock price data to S3 as JSON."""

    (
        df.write
        .mode("overwrite")
        .json(path)
    )