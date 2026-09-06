from datetime import date
from typing import Any

from atlas.transformation.models import StockPriceRecord

class StockPriceTransformer:
    """Transform raw stock price data into StockPriceRecord"""

    def _to_float(self, value: str | None) -> float | None:
        if not value:
            return None

        try:
            return float(value)
        except ValueError:
            return None

    def _to_int(self, value: str | None) -> int | None:
        if not value:
            return None

        try:
            return int(value)
        except ValueError:
            return None

    def _to_date(self, value: str | None) -> date | None:
        if not value:
            return None

        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

    def transform(self, data: dict[str, Any]) -> StockPriceRecord:
        return StockPriceRecord(
            ticker=data["symbol"],
            date=self._to_date(data.get("date")),
            open=self._to_float(data.get("open")),
            high=self._to_float(data.get("high")),
            low=self._to_float(data.get("low")),
            close=self._to_float(data.get("close")),
            volume=self._to_int(data.get("volume")),
        )
