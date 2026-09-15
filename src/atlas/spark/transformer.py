from pyspark.sql import DataFrame
from pyspark.sql.functions import col, row_number, when
from pyspark.sql.window import Window


def transform_stock_price(df: DataFrame) -> DataFrame:

    return df.withColumn(
        "price_status",
        when(col("ticker").isNull(), "invalid")
        .when(col("date").isNull(), "invalid")
        .when(col("open").isNull(), "invalid")
        .when(col("high").isNull(), "invalid")
        .when(col("low").isNull(), "invalid")
        .when(col("close").isNull(), "invalid")
        .when(col("open") < 0, "invalid")
        .when(col("high") < 0, "invalid")
        .when(col("low") < 0, "invalid")
        .when(col("close") < 0, "invalid")
        .when(col("volume") < 0, "invalid")
        .when(col("high") < col("open"), "invalid")
        .when(col("high") < col("close"), "invalid")
        .when(col("low") > col("open"), "invalid")
        .when(col("low") > col("close"), "invalid")
        .otherwise("valid"),
    )


def split_stock_price_quality(
    df: DataFrame,
) -> tuple[DataFrame, DataFrame]:

    valid = df.filter(col("price_status") == "valid")
    invalid = df.filter(col("price_status") == "invalid")

    return valid, invalid


def deduplicate_stock_price(df: DataFrame) -> DataFrame:

    window = Window.partitionBy(
        "ticker",
        "date",
    ).orderBy(
        col("ingestion_time").desc(),
    )

    return (
        df.withColumn(
            "row_num",
            row_number().over(window),
        )
        .filter(col("row_num") == 1)
        .drop("row_num")
    )