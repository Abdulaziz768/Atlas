from atlas.ingestion.company import CompanyService
from atlas.quality.processor import QualityProcessor
from atlas.storage.paths import S3PathBuilder
from atlas.storage.s3 import S3Storage
from atlas.transformation.company import CompanyTransformer


class CompanyPipeline:
    """Orchestrate the company data pipeline."""

    def __init__(
        self,
        service: CompanyService,
        transformer: CompanyTransformer,
        quality_processor: QualityProcessor,
        storage: S3Storage,
        paths: S3PathBuilder,
    ):
        self.service = service
        self.transformer = transformer
        self.quality_processor = quality_processor
        self.storage = storage
        self.paths = paths

    def ingest(self, ticker: str):
        raw_data = self.service.get_company_data(ticker)

        raw_key = self.paths.company_raw(ticker)
        self.storage.upload_json(
            data=raw_data,
            key=raw_key,
        )

        return self.process_from_s3(raw_key)

    def process_from_s3(self, s3_key: str):
        raw_data = self.storage.read_json(s3_key)

        company = self.transformer.transform(raw_data)

        valid, quarantine = self.quality_processor.process(company)

        if quarantine is not None:
            self._store_quarantine(quarantine)
            return None

        self._store_processed(valid)
        return valid

    def _store_quarantine(self, quarantine):
        quarantine_data = {
            "ticker": quarantine.ticker,
            "errors": quarantine.errors,
            "record": quarantine.record.__dict__,
        }

        key = self.paths.company_quarantine(quarantine.ticker)

        self.storage.upload_json(
            data=quarantine_data,
            key=key,
        )

    def _store_processed(self, company):
        key = self.paths.company_processed(company.ticker)

        self.storage.upload_json(
            data=company.__dict__,
            key=key,
        )