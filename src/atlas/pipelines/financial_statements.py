from atlas.ingestion.financial_statements import FinancialStatementService
from atlas.quality.processor import QualityProcessor
from atlas.storage.paths import S3PathBuilder
from atlas.storage.s3 import S3Storage
from atlas.transformation.financial_statements import FinancialStatementTransformer


class FinancialStatementPipeline:
    """Orchestrate the financial statement data pipeline."""

    def __init__(
        self,
        service: FinancialStatementService,
        transformer: FinancialStatementTransformer,
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
        raw_data = self.service.get_financial_statements(ticker)

        raw_key = self.paths.financial_statements_raw(ticker)
        self.storage.upload_json(data=raw_data, key=raw_key)

        return self.process_from_s3(raw_key)

    def process_from_s3(self, s3_key: str):
        raw_data = self.storage.read_json(s3_key)

        records = self.transformer.transform(raw_data)

        valid_records = []
        quarantine_records = []

        for record in records:
            valid, quarantine = self.quality_processor.process(record)

            if valid is not None:
                valid_records.append(valid)

            if quarantine is not None:
                quarantine_records.append(quarantine)

        if valid_records:
            self._store_processed(valid_records)

        for quarantine in quarantine_records:
            self._store_quarantine(quarantine)

        return valid_records

    def _store_processed(self, records):
        processed_data = [record.__dict__ for record in records]

        key = self.paths.financial_statements_processed(
            records[0].ticker
        )

        self.storage.upload_csv(
            data=processed_data,
            key=key,
        )

    def _store_quarantine(self, quarantine):
        quarantine_data = {
            "ticker": quarantine.ticker,
            "errors": quarantine.errors,
            "record": quarantine.record.__dict__,
        }

        key = self.paths.financial_statements_quarantine(
            quarantine.ticker
        )

        self.storage.upload_json(
            data=quarantine_data,
            key=key,
        )