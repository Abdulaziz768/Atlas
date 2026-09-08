from atlas.quality.models import QualityResult


class CompanyQualityChecker:
    """Validate company records."""

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

        return QualityResult(
            valid=len(errors) == 0,
            errors=errors,
        )