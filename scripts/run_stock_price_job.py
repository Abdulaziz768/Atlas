from atlas.spark.session import create_spark_session
from atlas.spark.stock_price_job import run_stock_price_job
from atlas.storage.paths import S3PathBuilder


BUCKET_NAME = "atlas-raw-data-6304"

paths = S3PathBuilder()

spark = create_spark_session()

try:
    run_stock_price_job(
        spark=spark,
        input_path=(
            f"s3a://{BUCKET_NAME}/"
            f"{paths.stock_price_processed_date()}"
        ),
        clean_output_path=(
            f"s3a://{BUCKET_NAME}/"
            f"{paths.stock_price_clean_date()}"
        ),
        quarantine_output_path=(
            f"s3a://{BUCKET_NAME}/"
            f"{paths.stock_price_quarantine_date()}"
        ),
    )
finally:
    spark.stop()