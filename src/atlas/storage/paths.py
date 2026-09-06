from datetime import date


class S3PathBuilder:
    """Build S3 keys for Atlas data."""

    def __init__(self, processing_date: date | None = None):
        self.processing_date = processing_date or date.today()

    def company_raw(self, ticker: str) -> str:
        return (
            f"raw/company_overview/"
            f"{self.processing_date:%Y-%m-%d}/"
            f"{ticker}.json"
        )

    def company_processed(self, ticker: str) -> str:
        return (
            f"processed/company_overview/"
            f"{self.processing_date:%Y-%m-%d}/"
            f"{ticker}.json"
        )

    def company_quarantine(self, ticker: str) -> str:
        return (
            f"quarantine/company_overview/"
            f"{self.processing_date:%Y-%m-%d}/"
            f"{ticker}.json"
        )

    def stock_price_raw(self, ticker: str) -> str:
        return (
            f"raw/stock_price/"
            f"{self.processing_date:%Y-%m-%d}/"
            f"{ticker}.json"
        )

    def stock_price_processed(self, ticker: str) -> str:
        return (
            f"processed/stock_price/"
            f"{self.processing_date:%Y-%m-%d}/"
            f"{ticker}.csv"
        )

    def stock_price_quarantine(self, ticker: str) -> str:
        return (
            f"quarantine/stock_price/"
            f"{self.processing_date:%Y-%m-%d}/"
            f"{ticker}.json"
        )