from atlas.config.settings import FINANCIAL_API_BASE_URL
from atlas.config.tickers import TICKERS
from atlas.ingestion.client import APIClient
from atlas.ingestion.financial_statements import FinancialStatementService
from atlas.quality.financial_statements import FinancialStatementQualityChecker
from atlas.quality.processor import QualityProcessor
from atlas.pipelines.financial_statements import FinancialStatementPipeline
from atlas.storage.paths import S3PathBuilder
from atlas.storage.s3 import S3Storage
from atlas.transformation.financial_statements import FinancialStatementTransformer


BUCKET_NAME = "atlas-raw-data-6304"


def main():
    client = APIClient(FINANCIAL_API_BASE_URL, min_request_interval=1.5)
    financial_statement_service = FinancialStatementService(client)
    storage = S3Storage(BUCKET_NAME)

    pipeline = FinancialStatementPipeline(
        service=financial_statement_service,
        transformer=FinancialStatementTransformer(),
        quality_processor=QualityProcessor(
            FinancialStatementQualityChecker()
        ),
        storage=storage,
        paths=S3PathBuilder(),
    )
    for ticker in TICKERS:
        result = pipeline.ingest(ticker)
        print(
            f"{ticker} financial statements ingestion completed successfully "
            f"({len(result)} records)"
        )
if __name__ == "__main__":
    main()