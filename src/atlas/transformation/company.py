from typing import Any

from atlas.transformation.models import CompanyRecord


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
        )