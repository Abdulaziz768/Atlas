from typing import Any

from atlas.transformation.models import StockPriceRecord
from atlas.transformation.utils import to_float, to_int, to_date


class StockPriceTransformer:
    """Transform raw stock price data into StockPriceRecord."""

    def transform(self, data: dict[str, Any]) -> StockPriceRecord:
        return StockPriceRecord(
            ticker=data["symbol"],
            date=to_date(data.get("date")),
            open=to_float(data.get("open")),
            high=to_float(data.get("high")),
            low=to_float(data.get("low")),
            close=to_float(data.get("close")),
            volume=to_int(data.get("volume")),
            ingestion_time=data["ingestion_time"],
        )