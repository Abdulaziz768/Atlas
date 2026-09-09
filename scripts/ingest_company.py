from atlas.config.settings import FINANCIAL_API_BASE_URL
from atlas.config.tickers import TICKERS
from atlas.ingestion.client import APIClient
from atlas.ingestion.company import CompanyService
from atlas.storage.s3 import S3Storage
from atlas.storage.paths import S3PathBuilder
from atlas.pipelines.company import CompanyPipeline
from atlas.transformation.company import CompanyTransformer
from atlas.quality.company import CompanyQualityChecker
from atlas.quality.processor import QualityProcessor


BUCKET_NAME = "atlas-raw-data-6304"


def main():
    client = APIClient(FINANCIAL_API_BASE_URL, min_request_interval=1.5)
    company_service = CompanyService(client)
    storage = S3Storage(BUCKET_NAME)

    pipeline = CompanyPipeline(
        service=company_service,
        transformer=CompanyTransformer(),
        quality_processor=QualityProcessor(
            CompanyQualityChecker()
        ),
        storage=storage,
        paths=S3PathBuilder(),
    )
    for ticker in TICKERS:
        pipeline.ingest(ticker)

        print(f"{ticker} ingestion completed successfully")


if __name__ == "__main__":
    main()