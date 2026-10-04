import logging 

from atlas.spark.session import create_spark_session
from atlas.spark.stock_price_job import run_stock_price_job
from atlas.storage.paths import S3PathBuilder
from atlas.config.logging import configure_logging

BUCKET_NAME = "atlas-raw-data-6304"

logger = logging.getLogger(__name__)


def main():
    configure_logging()

    logger.info("Starting stock price PySpark job")

    spark = None

    try:
        paths = S3PathBuilder()
        spark = create_spark_session()

        run_stock_price_job(
            spark=spark,
            input_path=(
                f"s3a://{BUCKET_NAME}/"
                "processed/stock_price/"
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
        logger.info("Stock price PySpark job completed successfully") 
    except Exception: 
        logger.exception("Stock price PySpark job failed") 
        raise 
    finally: 
        if spark is not None:
            spark.stop() 
            logger.info("Spark session stopped")


if __name__ == "__main__":
    main()