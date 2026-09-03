from datetime import date
from atlas.ingestion.company import CompanyService
from atlas.storage.s3 import S3Storage

class AtlasPipeline:
    """Orchestrates data ingestion and storage"""

    def __init__(self, company_service: CompanyService, storage: S3Storage):
        self.company_service = company_service
        self.storage = storage

    def build_s3_key(self, ticker: str) -> str:
        today = date.today()

        return (
            f"raw/company_overview/"
            f"{today:%Y-%m-%d}/"
            f"{ticker}.json"
        )

    def ingest_company(self, ticker: str) -> None:
        data = self.company_service.get_company_data(ticker)

        s3_key = self.build_s3_key(ticker)

        self.storage.upload_json(
            data=data,
            key=s3_key,
        )
