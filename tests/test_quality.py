from atlas.transformation.models import CompanyRecord
from atlas.quality.company import CompanyQualityChecker


def test_valid_company_record():
    company = CompanyRecord(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD",
        sector="TECHNOLOGY",
        industry="CONSUMER ELECTRONICS",
        market_cap=4742524699000,
        ebitda=167959003000,
        pe_ratio=37.31,
        eps=8.71,
        revenue_ttm=466822988000,
        profit_margin=0.276,
        operating_margin=0.326,
        return_on_equity=1.488,
        beta=1.086,
    )

    checker = CompanyQualityChecker()

    result = checker.check(company)

    assert result.valid is True
    assert result.errors == []

def test_company_with_missing_ticker_is_invalid():
    company = CompanyRecord(
        ticker="",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD",
        sector="TECHNOLOGY",
        industry="CONSUMER ELECTRONICS",
        market_cap=4742524699000,
        ebitda=167959003000,
        pe_ratio=37.31,
        eps=8.71,
        revenue_ttm=466822988000,
        profit_margin=0.276,
        operating_margin=0.326,
        return_on_equity=1.488,
        beta=1.086,
    )

    checker = CompanyQualityChecker()

    result = checker.check(company)

    assert result.valid is False
    assert "ticker is missing" in result.errors


def test_company_with_missing_name_is_invalid():
    company = CompanyRecord(
        ticker="AAPL",
        name="",
        exchange="NASDAQ",
        currency="USD",
        sector="TECHNOLOGY",
        industry="CONSUMER ELECTRONICS",
        market_cap=4742524699000,
        ebitda=167959003000,
        pe_ratio=37.31,
        eps=8.71,
        revenue_ttm=466822988000,
        profit_margin=0.276,
        operating_margin=0.326,
        return_on_equity=1.488,
        beta=1.086,
    )

    checker = CompanyQualityChecker()

    result = checker.check(company)

    assert result.valid is False
    assert "company name is missing" in result.errors


def test_company_with_missing_exchange_is_invalid():
    company = CompanyRecord(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="",
        currency="USD",
        sector="TECHNOLOGY",
        industry="CONSUMER ELECTRONICS",
        market_cap=4742524699000,
        ebitda=167959003000,
        pe_ratio=37.31,
        eps=8.71,
        revenue_ttm=466822988000,
        profit_margin=0.276,
        operating_margin=0.326,
        return_on_equity=1.488,
        beta=1.086,
    )

    checker = CompanyQualityChecker()

    result = checker.check(company)

    assert result.valid is False
    assert "exchange is missing" in result.errors


def test_company_with_missing_currency_is_invalid():
    company = CompanyRecord(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="",
        sector="TECHNOLOGY",
        industry="CONSUMER ELECTRONICS",
        market_cap=4742524699000,
        ebitda=167959003000,
        pe_ratio=37.31,
        eps=8.71,
        revenue_ttm=466822988000,
        profit_margin=0.276,
        operating_margin=0.326,
        return_on_equity=1.488,
        beta=1.086,
    )

    checker = CompanyQualityChecker()

    result = checker.check(company)

    assert result.valid is False
    assert "currency is missing" in result.errors

def test_company_with_missing_sector_is_invalid():
    company = CompanyRecord(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD",
        sector="",
        industry="CONSUMER ELECTRONICS",
        market_cap=4742524699000,
        ebitda=167959003000,
        pe_ratio=37.31,
        eps=8.71,
        revenue_ttm=466822988000,
        profit_margin=0.276,
        operating_margin=0.326,
        return_on_equity=1.488,
        beta=1.086,
    )

    checker = CompanyQualityChecker()

    result = checker.check(company)

    assert result.valid is False
    assert "sector is missing" in result.errors

def test_company_with_missing_industry_is_invalid():
    company = CompanyRecord(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD",
        sector="TECHNOLOGY",
        industry="",
        market_cap=4742524699000,
        ebitda=167959003000,
        pe_ratio=37.31,
        eps=8.71,
        revenue_ttm=466822988000,
        profit_margin=0.276,
        operating_margin=0.326,
        return_on_equity=1.488,
        beta=1.086,
    )

    checker = CompanyQualityChecker()

    result = checker.check(company)

    assert result.valid is False
    assert "industry is missing" in result.errors

def test_company_with_negative_market_cap_is_invalid():
    company = CompanyRecord(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD",
        sector="TECHNOLOGY",
        industry="CONSUMER ELECTRONICS",
        market_cap=-1000000,
        ebitda=167959003000,
        pe_ratio=37.31,
        eps=8.71,
        revenue_ttm=466822988000,
        profit_margin=0.276,
        operating_margin=0.326,
        return_on_equity=1.488,
        beta=1.086,
    )

    result = CompanyQualityChecker().check(company)

    assert result.valid is False
    assert "market cap cannot be negative" in result.errors

def test_company_with_invalid_beta_is_invalid():
    company = CompanyRecord(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD",
        sector="TECHNOLOGY",
        industry="CONSUMER ELECTRONICS",
        market_cap=4742524699000,
        ebitda=167959003000,
        pe_ratio=37.31,
        eps=8.71,
        revenue_ttm=466822988000,
        profit_margin=0.276,
        operating_margin=0.326,
        return_on_equity=1.488,
        beta=float("nan"),
    )

    result = CompanyQualityChecker().check(company)

    assert result.valid is False
    assert "beta must be a finite number" in result.errors

def test_company_with_invalid_profit_margin_is_invalid():
    company = CompanyRecord(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD",
        sector="TECHNOLOGY",
        industry="CONSUMER ELECTRONICS",
        market_cap=4742524699000,
        ebitda=167959003000,
        pe_ratio=37.31,
        eps=8.71,
        revenue_ttm=466822988000,
        profit_margin=1.5,
        operating_margin=0.326,
        return_on_equity=1.488,
        beta=1.086,
    )

    result = CompanyQualityChecker().check(company)

    assert result.valid is False
    assert "profit margin must be between -1 and 1" in result.errors

def test_company_with_invalid_operating_margin_is_invalid():
    company = CompanyRecord(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD",
        sector="TECHNOLOGY",
        industry="CONSUMER ELECTRONICS",
        market_cap=4742524699000,
        ebitda=167959003000,
        pe_ratio=37.31,
        eps=8.71,
        revenue_ttm=466822988000,
        profit_margin=0.786,
        operating_margin=-10.326,
        return_on_equity=1.488,
        beta=1.086,
    )

    result = CompanyQualityChecker().check(company)

    assert result.valid is False
    assert "operating margin must be between -1 and 1" in result.errors

def test_invalid_company_record_is_rejected():
    company = CompanyRecord(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD",
        sector="TECHNOLOGY",
        industry="CONSUMER ELECTRONICS",
        market_cap=-1000000,
        ebitda=167959003000,
        pe_ratio=37.31,
        eps=8.71,
        revenue_ttm=466822988000,
        profit_margin=0.276,
        operating_margin=0.326,
        return_on_equity=1.488,
        beta=1.086,
    )

    result = CompanyQualityChecker().check(company)

    assert result.valid is False
    assert result.errors == ["market cap cannot be negative"]

