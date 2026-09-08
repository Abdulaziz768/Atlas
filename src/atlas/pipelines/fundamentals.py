from atlas.quality.processor import QualityProcessor
from atlas.storage.paths import S3PathBuilder
from atlas.storage.s3 import S3Storage
from atlas.transformation.fundamentals import FundamentalsTransformer


class FundamentalsPipeline:
    """Process company overview data into fundamentals data."""

    def __init__(
        self,
        transformer: FundamentalsTransformer,
        quality_processor: QualityProcessor,
        storage: S3Storage,
        paths: S3PathBuilder,
    ):
        self.transformer = transformer
        self.quality_processor = quality_processor
        self.storage = storage
        self.paths = paths

    def process_from_s3(self, s3_key: str):
        raw_data = self.storage.read_json(s3_key)

        fundamentals = self.transformer.transform(raw_data)

        valid, quarantine = self.quality_processor.process(fundamentals)

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

        key = self.paths.fundamentals_quarantine(
            quarantine.ticker
        )

        self.storage.upload_json(
            data=quarantine_data,
            key=key,
        )

    def _store_processed(self, fundamentals):
        key = self.paths.fundamentals_processed(
            fundamentals.ticker
        )

        self.storage.upload_csv(
            data=[fundamentals.__dict__],
            key=key,
        )