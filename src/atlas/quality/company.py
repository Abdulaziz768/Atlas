import math

from atlas.quality.models import QualityResult


class CompanyQualityChecker:
    def check(self, company):
        errors = []

        if not company.ticker:
            errors.append("ticker is missing")

        if not company.name:
            errors.append("company name is missing")

        if not company.exchange:
            errors.append("exchange is missing")

        if not company.currency:
            errors.append("currency is missing")

        if not company.sector:
            errors.append("sector is missing")

        if not company.industry:
            errors.append("industry is missing")

        if company.market_cap is not None and company.market_cap < 0:
            errors.append("market cap cannot be negative")

        if company.beta is not None and not math.isfinite(company.beta):
            errors.append("beta must be a finite number")

        if (
            company.profit_margin is not None
            and not -1 <= company.profit_margin <= 1
        ):
            errors.append("profit margin must be between -1 and 1")

        if (
            company.operating_margin is not None
            and not -1 <= company.operating_margin <= 1
        ):
            errors.append("operating margin must be between -1 and 1")

        return QualityResult(
            valid=len(errors) == 0,
            errors=errors,
        )