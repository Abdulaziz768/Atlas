from typing import Any

from atlas.transformation.models import CompanyRecord

class CompanyTransformer:
    """Transform raw company data into structured CompanyRecord"""

    def _to_int(self, value: str | None) -> int | None:
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def _to_float(self, value: str | None) -> float | None:
        if not value: 
            return None

        try:
            return float(value)
        except ValueError:
            return None

    def transform(self, data: dict[str, Any]) -> CompanyRecord:
            
        return CompanyRecord(
            ticker=data["Symbol"],
            name=data["Name"],
            exchange=data["Exchange"],
            currency=data["Currency"],
            sector=data["Sector"],
            industry=data["Industry"],
            market_cap=self._to_int(data.get("MarketCapitalization")),
            ebitda=self._to_int(data.get("EBITDA")),
            pe_ratio=self._to_float(data.get("PERatio")),
            eps=self._to_float(data.get("EPS")),
            revenue_ttm=self._to_int(data.get("RevenueTTM")),
            profit_margin=self._to_float(data.get("ProfitMargin")),
            operating_margin=self._to_float(data.get("OperatingMarginTTM")),
            return_on_equity=self._to_float(data.get("ReturnOnEquityTTM")),
            beta=self._to_float(data.get("Beta")),            
        )