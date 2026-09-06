from datetime import date

from atlas.ingestion.company import CompanyService
from atlas.storage.s3 import S3Storage
from atlas.quality.processor import QualityProcessor
from atlas.transformation.company import CompanyTransformer
from atlas.transformation.stock_price import StockPriceTransformer
from atlas.ingestion.stock_price import StockPriceService

class AtlasPipeline:
    """Orchestrates data ingestion and storage"""

    def __init__(
        self,
        company_service: CompanyService,
        storage: S3Storage,
        transformer: CompanyTransformer,
        quality_processor: QualityProcessor,
        stock_price_transformer: StockPriceTransformer | None = None,
        stock_price_quality_processor: QualityProcessor | None = None,
        stock_price_service: StockPriceService | None = None,
    ):
        self.company_service = company_service
        self.storage = storage
        self.transformer = transformer
        self.quality_processor = quality_processor
        self.stock_price_transformer = stock_price_transformer
        self.stock_price_quality_processor = stock_price_quality_processor
        self.stock_price_service = stock_price_service

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

    def build_stock_price_s3_key(self, ticker: str) -> str:
        today = date.today()

        return (
            f"raw/stock_price/"
            f"{today:%Y-%m-%d}/"
            f"{ticker}.json"
        )


    def build_stock_price_quarantine_s3_key(self, ticker: str) -> str:
        today = date.today()

        return (
            f"quarantine/stock_price/"
            f"{today:%Y-%m-%d}/"
            f"{ticker}.json"
        )


    def build_stock_price_processed_s3_key(self, ticker: str) -> str:
        today = date.today()

        return (
            f"processed/stock_price/"
            f"{today:%Y-%m-%d}/"
            f"{ticker}.json"
        )
    
    def process_company(self, data: dict):
        company = self.transformer.transform(data)

        return self.quality_processor.process(company)

    def process_stock_price(self, data: list[dict]):
        valid_records = []
        quarantine_records = []

        for record in data:
            stock_price = self.stock_price_transformer.transform(record)
            valid, quarantine = self.stock_price_quality_processor.process(stock_price)

            if valid is not None:
                valid_records.append(valid)

            if quarantine is not None:
                quarantine_records.append(quarantine)

        return valid_records, quarantine_records

    def process_and_store_company(self, data: dict):
        company, quarantine = self.process_company(data)

        if quarantine is not None:
            self.store_quarantine(quarantine)
            return None

        self.store_processed(company)

        return company

    def process_and_store_stock_price(self, data: list[dict]):
        valid_records, quarantine_records = self.process_stock_price(data)

        if valid_records:
            self.store_stock_price_processed(valid_records)

        for quarantine in quarantine_records:
            self.store_stock_price_quarantine(quarantine)

        return valid_records

    def process_from_s3(self, s3_key: str):

        data = self.storage.read_json(s3_key)

        return self.process_company(data)

    def process_stock_price_from_s3(self, s3_key: str):

        data = self.storage.read_json(s3_key)

        return self.process_stock_price(data)

    def process_and_store_from_s3(self, s3_key: str):

        data = self.storage.read_json(s3_key)

        return self.process_and_store_company(data)

    def process_and_store_stock_price_from_s3(self, s3_key: str):

        data = self.storage.read_json(s3_key)

        return self.process_and_store_stock_price(data)

    def ingest_company(self, ticker: str):
        data = self.company_service.get_company_data(ticker)

        s3_key = self.build_s3_key(ticker)

        self.storage.upload_json(
            data=data,
            key=s3_key,
        )

        return self.process_and_store_from_s3(s3_key)

    def ingest_stock_price(self, ticker: str):
        data = self.stock_price_service.get_stock_price_data(ticker)

        s3_key = self.build_stock_price_s3_key(ticker)

        self.storage.upload_json(
            data=data,
            key=s3_key
        )

        return self.process_and_store_stock_price_from_s3(s3_key)

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

    def store_stock_price_quarantine(self, quarantine):
        record_data = quarantine.record.__dict__.copy()
        record_data["date"] = record_data["date"].isoformat()

        quarantine_data = {
            "ticker": quarantine.ticker,
            "errors": quarantine.errors,
            "record": record_data,
        }

        key = self.build_stock_price_quarantine_s3_key(quarantine.ticker)

        self.storage.upload_json(
            data=quarantine_data,
            key=key,
        )


    def store_stock_price_processed(self, stock_prices):
        processed_data = []

        for stock_price in stock_prices:                
            record = stock_price.__dict__.copy()
            record["date"] = record["date"].isoformat()
            processed_data.append(record)

        key = self.build_stock_price_processed_s3_key(stock_prices[0].ticker)

        self.storage.upload_csv(
            data=processed_data,
            key=key,
        )