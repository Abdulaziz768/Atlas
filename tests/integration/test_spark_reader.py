from atlas.spark.session import create_spark_session
from atlas.spark.reader import read_stock_price
from atlas.spark.transformer import deduplicate_stock_price


def test_read_stock_price():
    spark = create_spark_session()

    try:
        df = read_stock_price(
            spark,
            "s3a://atlas-raw-data-6304/processed/stock_price/",
        )
        deduplicated = deduplicate_stock_price(df)

        print("Rows after deduplication:", deduplicated.count())

        deduplicated.groupBy("ticker", "date").count().filter("count > 1").show()

    finally:
        spark.stop()


if __name__ == "__main__":
    test_read_stock_price()