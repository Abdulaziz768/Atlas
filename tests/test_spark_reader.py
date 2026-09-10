from atlas.spark.session import create_spark_session
from atlas.spark.reader import read_stock_price

def test_read_stock_price():
    spark = create_spark_session()

    df = read_stock_price(
        spark,
        "s3a://atlas-raw-data-6304/processed/stock_price/2026-09-09/AAPL.csv"
    )
    # df_filtered = df.filter(df["close"] > 300)
    # df_filtered.explain()
    df_grouped = df.groupBy("ticker").count()
    df_grouped.explain()
    df_grouped.show()
    # df.printSchema()

    spark.stop()