from typing import Any

from atlas.transformation.models import CompanyRecord
from atlas.transformation.utils import to_float, to_int


class CompanyTransformer:
    """Transform raw company data into structured CompanyRecord."""

    def transform(self, data: dict[str, Any]) -> CompanyRecord:
        return CompanyRecord(
            ticker=data["Symbol"],
            name=data["Name"],
            exchange=data["Exchange"],
            currency=data["Currency"],
            sector=data["Sector"],
            industry=data["Industry"],
            market_cap=to_int(data.get("MarketCapitalization")),
            ebitda=to_int(data.get("EBITDA")),
            pe_ratio=to_float(data.get("PERatio")),
            eps=to_float(data.get("EPS")),
            revenue_ttm=to_int(data.get("RevenueTTM")),
            profit_margin=to_float(data.get("ProfitMargin")),
            operating_margin=to_float(data.get("OperatingMarginTTM")),
            return_on_equity=to_float(data.get("ReturnOnEquityTTM")),
            beta=to_float(data.get("Beta")),
        )