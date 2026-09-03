from atlas.config.settings import FINANCIAL_API_BASE_URL
from atlas.ingestion.client import APIClient
from atlas.ingestion.company import CompanyService
from atlas.storage.s3 import S3Storage
from atlas.ingestion.pipeline import AtlasPipeline

BUCKET_NAME = "atlas-raw-data-6304"

def main():
    client = APIClient(FINANCIAL_API_BASE_URL)
    company_service = CompanyService(client)
    storage = S3Storage(BUCKET_NAME)

    pipeline = AtlasPipeline(company_service, storage)

    pipeline.ingest_company("AAPL")

    print("AAPL ingestion completed successfully")

if __name__ == "__main__":
    main()