from atlas.quality.models import QuarantineRecord


class QualityProcessor:

    def __init__(self, checker):
        self.checker = checker

    def process(self, record):

        result = self.checker.check(record)

        if result.valid:
            return record, None

        quarantine_record = QuarantineRecord(
            ticker=record.ticker,
            errors=result.errors,
            record=record,
        )

        return None, quarantine_record