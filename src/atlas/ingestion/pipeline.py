from datetime import date
from atlas.ingestion.company import CompanyService
from atlas.storage.s3 import S3Storage
from atlas.quality.processor import QualityProcessor
from atlas.transformation.company import CompanyTransformer

class AtlasPipeline:
    """Orchestrates data ingestion and storage"""

    def __init__(self, company_service: CompanyService, storage: S3Storage, transformer: CompanyTransformer, quality_processor: QualityProcessor):
        self.company_service = company_service
        self.storage = storage
        self.transformer = transformer
        self.quality_processor = quality_processor

    def build_s3_key(self, ticker: str) -> str:
        today = date.today()

        return (
            f"raw/company_overview/"
            f"{today:%Y-%m-%d}/"
            f"{ticker}.json"
        )

    def build_quarantine_s3_key(self, ticker: str) -> str:
        today = date.today()

        return (
            f"quarantine/company_overview/"
            f"{today:%Y-%m-%d}/"
            f"{ticker}.json"
        )

    def build_processed_s3_key(self, ticker: str) -> str:
        today = date.today()

        return (
            f"processed/company_overview/"
            f"{today:%Y-%m-%d}/"
            f"{ticker}.json"
        )

    def process_company(self, data: dict):
        company = self.transformer.transform(data)

        return self.quality_processor.process(company)

    def process_and_store_company(self, data: dict):
        company, quarantine = self.process_company(data)

        if quarantine is not None:
            self.store_quarantine(quarantine)
            return None

        self.store_processed(company)

        return company

    def process_from_s3(self, s3_key: str):

        data = self.storage.read_json(s3_key)

        return self.process_company(data)

    def process_and_store_from_s3(self, s3_key: str):

        data = self.storage.read_json(s3_key)

        return self.process_and_store_company(data)

    def ingest_company(self, ticker: str):
        data = self.company_service.get_company_data(ticker)

        s3_key = self.build_s3_key(ticker)

        self.storage.upload_json(
            data=data,
            key=s3_key,
        )

        return self.process_and_store_from_s3(s3_key)

    def store_quarantine(self, quarantine):
        quarantine_data = {
            "ticker" : quarantine.ticker,
            "errors" : quarantine.errors,
            "record" : quarantine.record.__dict__,
        }

        key = self.build_quarantine_s3_key(quarantine.ticker)

        self.storage.upload_json(
            data=quarantine_data,
            key=key,
        )

    def store_processed(self, company):
        processed_data = company.__dict__

        key = self.build_processed_s3_key(company.ticker)

        self.storage.upload_json(
            data=processed_data,
            key=key
        )
