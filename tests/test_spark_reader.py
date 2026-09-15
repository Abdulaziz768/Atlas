from atlas.spark.session import create_spark_session
from atlas.spark.reader import read_stock_price
from pyspark.sql.functions import col, when, window

def test_read_stock_price():
    spark = create_spark_session()

    df = read_stock_price(
        spark,
        "s3a://atlas-raw-data-6304/processed/stock_price/2026-09-12/AAPL.csv"
    )
    # # df_transformed = df.withColumn(
    # #     "volume_string",
    # #     df["volume"]
    # #     .cast("string"),
    # # )
    # # df_transformed.explain()
    # # df_transformed.show()
    # # df_selected = df.select(
    # #     "ticker",
    # #     "date",
    # #     "close",
    # #     "volume",
    # # )
    # # df_selected.explain()
    # # df_selected.show()
    # # df_filtered = df.filter(df["close"] > 300)
    # # df_filtered.explain()
    # # df_grouped = df.groupBy("ticker").count()
    # # df_grouped.explain()
    # # df_grouped.show()
    # # df.printSchema()
    # df_cleaned = df.select(
    #     "ticker",
    #     "date",
    #     "close",
    #     "volume",
    # ).withColumn(
    #     "volume_status",
    #     when(col("volume") > 0, "valid")
    #     .otherwise("invalid")
     # )
    
    df.printSchema()
    df.show()
    spark.stop()