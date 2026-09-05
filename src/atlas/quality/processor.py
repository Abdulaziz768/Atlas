from atlas.quality.company import CompanyQualityChecker
from atlas.quality.models import QuarantineRecord

class QualityProcessor:

    def __init__(self, checker: CompanyQualityChecker):
        self.checker = checker

    def process(self, company):
        result = self.checker.check(company)

        if result.valid:
            return company, None

        quarantine_record = QuarantineRecord(
            ticker=company.ticker,
            errors=result.errors,
            record=company,
        )

        return None, quarantine_record