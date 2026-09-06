from atlas.quality.company import CompanyQualityChecker
from atlas.quality.models import QuarantineRecord
from atlas.quality.processor import QualityProcessor
from atlas.transformation.models import CompanyRecord


def create_company(market_cap=4742524699000):
    return CompanyRecord(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD",
        sector="TECHNOLOGY",
        industry="CONSUMER ELECTRONICS",
        market_cap=market_cap,
        ebitda=167959003000,
        pe_ratio=37.31,
        eps=8.71,
        revenue_ttm=466822988000,
        profit_margin=0.276,
        operating_margin=0.326,
        return_on_equity=1.488,
        beta=1.086,
    )


def test_valid_company_is_returned():
    company = create_company()

    processor = QualityProcessor(CompanyQualityChecker())

    valid_company, quarantine = processor.process(company)

    assert valid_company == company
    assert quarantine is None


def test_invalid_company_is_quarantined():
    company = create_company(market_cap=-1000000)

    processor = QualityProcessor(CompanyQualityChecker())

    valid_company, quarantine = processor.process(company)

    assert valid_company is None
    assert isinstance(quarantine, QuarantineRecord)
    assert quarantine.ticker == "AAPL"
    assert quarantine.errors == ["market cap cannot be negative"]
    assert quarantine.record == company