from atlas.config.settings import FINANCIAL_API_BASE_URL
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
    client = APIClient(FINANCIAL_API_BASE_URL)
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

    result = pipeline.ingest("AAPL")

    print(f"Records produced: {len(result)}")
    print(result[0])
    print(result[-1])

if __name__ == "__main__":
    main()