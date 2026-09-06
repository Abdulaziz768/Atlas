from atlas.config.settings import FINANCIAL_API_BASE_URL
from atlas.ingestion.client import APIClient
from atlas.ingestion.stock_price import StockPriceService
from atlas.storage.s3 import S3Storage
from atlas.ingestion.pipeline import AtlasPipeline
from atlas.transformation.company import CompanyTransformer
from atlas.transformation.stock_price import StockPriceTransformer
from atlas.quality.company import CompanyQualityChecker
from atlas.quality.stock_price import StockPriceQualityChecker
from atlas.quality.processor import QualityProcessor

BUCKET_NAME = "atlas-raw-data-6304"


def main():
    client = APIClient(FINANCIAL_API_BASE_URL)

    stock_price_service = StockPriceService(client)
    storage = S3Storage(BUCKET_NAME)

    pipeline = AtlasPipeline(
        company_service=None,
        storage=storage,
        transformer=CompanyTransformer(),
        quality_processor=QualityProcessor(CompanyQualityChecker()),
        stock_price_transformer=StockPriceTransformer(),
        stock_price_quality_processor=QualityProcessor(
            StockPriceQualityChecker()
        ),
        stock_price_service=stock_price_service,
    )

    pipeline.ingest_stock_price("AAPL")

    print("AAPL stock price ingestion completed successfully")


if __name__ == "__main__":
    main()