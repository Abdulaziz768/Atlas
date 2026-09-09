from atlas.config.settings import FINANCIAL_API_BASE_URL
from atlas.config.tickers import TICKERS
from atlas.ingestion.client import APIClient
from atlas.ingestion.stock_price import StockPriceService
from atlas.storage.s3 import S3Storage
from atlas.storage.paths import S3PathBuilder
from atlas.pipelines.stock_price import StockPricePipeline
from atlas.transformation.stock_price import StockPriceTransformer
from atlas.quality.stock_price import StockPriceQualityChecker
from atlas.quality.processor import QualityProcessor


BUCKET_NAME = "atlas-raw-data-6304"


def main():
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
        pipeline.ingest(ticker)
        print(f"{ticker} stock price ingestion completed successfully")

if __name__ == "__main__":
    main()