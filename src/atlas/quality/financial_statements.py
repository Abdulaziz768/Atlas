from math import isfinite

from atlas.quality.models import QualityResult


class FinancialStatementQualityChecker:
    """Validate financial statement records."""

    def check(self, record):
        errors = []

        if not record.ticker:
            errors.append("ticker is missing")

        if record.fiscal_date is None:
            errors.append("fiscal date is missing")

        if record.report_type not in ("annual", "quarterly"):
            errors.append("report type must be annual or quarterly")

        if not record.currency:
            errors.append("currency is missing")

        non_negative_fields = {
            "total_assets": record.total_assets,
            "inventory": record.inventory,
            "cash": record.cash,
            "total_debt": record.total_debt,
        }

        for field_name, value in non_negative_fields.items():
            if value is not None and value < 0:
                errors.append(f"{field_name} cannot be negative")

        numeric_fields = {
            "revenue": record.revenue,
            "gross_profit": record.gross_profit,
            "operating_income": record.operating_income,
            "net_income": record.net_income,
            "ebitda": record.ebitda,
            "total_assets": record.total_assets,
            "total_liabilities": record.total_liabilities,
            "total_equity": record.total_equity,
            "cash": record.cash,
            "inventory": record.inventory,
            "total_debt": record.total_debt,
            "operating_cash_flow": record.operating_cash_flow,
            "capital_expenditure": record.capital_expenditure,
            "investing_cash_flow": record.investing_cash_flow,
            "financing_cash_flow": record.financing_cash_flow,
            "free_cash_flow": record.free_cash_flow,
        }

        for field_name, value in numeric_fields.items():
            if value is not None and not isfinite(value):
                errors.append(f"{field_name} must be finite")

        return QualityResult(
            valid=len(errors) == 0,
            errors=errors,
        )