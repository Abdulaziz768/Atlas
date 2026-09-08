from atlas.quality.company import CompanyQualityChecker
from atlas.quality.processor import QualityProcessor
from atlas.transformation.models import CompanyRecord


def create_company():
    return CompanyRecord(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD",
        sector="TECHNOLOGY",
        industry="CONSUMER ELECTRONICS",
    )


def test_valid_company_is_not_quarantined():
    company = create_company()

    checker = CompanyQualityChecker()
    processor = QualityProcessor(checker)

    valid, quarantine = processor.process(company)

    assert valid is not None
    assert quarantine is None
    assert valid == company


def test_invalid_company_is_quarantined():
    company = create_company()
    company.ticker = ""

    checker = CompanyQualityChecker()
    processor = QualityProcessor(checker)

    valid, quarantine = processor.process(company)

    assert valid is None
    assert quarantine is not None
    assert quarantine.ticker == ""
    assert "ticker is missing" in quarantine.errors
    assert quarantine.record == company