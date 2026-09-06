from atlas.ingestion.stock_price import StockPriceService
from atlas.quality.processor import QualityProcessor
from atlas.storage.paths import S3PathBuilder
from atlas.storage.s3 import S3Storage
from atlas.transformation.stock_price import StockPriceTransformer


class StockPricePipeline:
    """Orchestrate the stock price data pipeline."""

    def __init__(
        self,
        service: StockPriceService,
        transformer: StockPriceTransformer,
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
        raw_data = self.service.get_stock_price_data(ticker)

        raw_key = self.paths.stock_price_raw(ticker)

        self.storage.upload_json(
            data=raw_data,
            key=raw_key,
        )

        return self.process_from_s3(raw_key)

    def process_from_s3(self, s3_key: str):
        raw_data = self.storage.read_json(s3_key)

        valid_records = []
        quarantine_records = []

        for record in raw_data:
            stock_price = self.transformer.transform(record)

            valid, quarantine = self.quality_processor.process(
                stock_price
            )

            if valid is not None:
                valid_records.append(valid)

            if quarantine is not None:
                quarantine_records.append(quarantine)

        if valid_records:
            self._store_processed(valid_records)

        for quarantine in quarantine_records:
            self._store_quarantine(quarantine)

        return valid_records

    def _store_quarantine(self, quarantine):
        record_data = quarantine.record.__dict__.copy()

        if record_data["date"] is not None:
            record_data["date"] = record_data["date"].isoformat()

        quarantine_data = {
            "ticker": quarantine.ticker,
            "errors": quarantine.errors,
            "record": record_data,
        }

        key = self.paths.stock_price_quarantine(
            quarantine.ticker
        )

        self.storage.upload_json(
            data=quarantine_data,
            key=key,
        )

    def _store_processed(self, stock_prices):
        processed_data = []

        for stock_price in stock_prices:
            record = stock_price.__dict__.copy()

            if record["date"] is not None:
                record["date"] = record["date"].isoformat()

            processed_data.append(record)

        key = self.paths.stock_price_processed(
            stock_prices[0].ticker
        )

        self.storage.upload_csv(
            data=processed_data,
            key=key,
        )