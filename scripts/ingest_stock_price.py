import logging

from atlas.config.settings import FINANCIAL_API_BASE_URL
from atlas.config.tickers import TICKERS
from atlas.config.logging import configure_logging
from atlas.ingestion.client import APIClient
from atlas.ingestion.stock_price import StockPriceService
from atlas.storage.s3 import S3Storage
from atlas.storage.paths import S3PathBuilder
from atlas.pipelines.stock_price import StockPricePipeline
from atlas.transformation.stock_price import StockPriceTransformer
from atlas.quality.stock_price import StockPriceQualityChecker
from atlas.quality.processor import QualityProcessor


BUCKET_NAME = "atlas-raw-data-6304"

logger = logging.getLogger(__name__)


def main():

    configure_logging()

    logger.info("Starting stock price ingestion")
    logger.info("Tickers configured for ingestion: %s", TICKERS)

    client = APIClient(FINANCIAL_API_BASE_URL, min_request_interval=1.5)

    stock_price_service = StockPriceService(client)
    storage = S3Storage(BUCKET_NAME)

    pipeline = StockPricePipeline(
        service=stock_price_service,
        transformer=StockPriceTransformer(),
        quality_processor=QualityProcessor(
            StockPriceQualityChecker()
        ),
        storage=storage,
        paths=S3PathBuilder(),
    )

    for ticker in TICKERS:

        logger.info("Starting ingestion for ticker: %s", ticker)

        try:
            pipeline.ingest(ticker)

            logger.info(
                "Stock price ingestion completed successfully for ticker: %s",
                ticker,
            )

        except Exception:
            logger.exception(
                "Stock price ingestion failed for ticker: %s",
                ticker,
            )
            raise


if __name__ == "__main__":
    main()