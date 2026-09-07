import pytest

from atlas.quality.company import CompanyQualityChecker
from atlas.transformation.models import CompanyRecord
from atlas.quality.financial_statements import FinancialStatementQualityChecker
from atlas.transformation.models import FinancialStatementRecord

def create_company(**overrides):
    data = {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "exchange": "NASDAQ",
        "currency": "USD",
        "sector": "TECHNOLOGY",
        "industry": "CONSUMER ELECTRONICS",
        "market_cap": 4742524699000,
        "ebitda": 167959003000,
        "pe_ratio": 37.31,
        "eps": 8.71,
        "revenue_ttm": 466822988000,
        "profit_margin": 0.276,
        "operating_margin": 0.326,
        "return_on_equity": 1.488,
        "beta": 1.086,
    }

    data.update(overrides)
    return CompanyRecord(**data)


def test_valid_company_record():
    company = create_company()

    result = CompanyQualityChecker().check(company)

    assert result.valid is True
    assert result.errors == []


@pytest.mark.parametrize(
    "field, error",
    [
        ("ticker", "ticker is missing"),
        ("name", "company name is missing"),
        ("exchange", "exchange is missing"),
        ("currency", "currency is missing"),
        ("sector", "sector is missing"),
        ("industry", "industry is missing"),
    ],
)
def test_company_with_missing_required_field_is_invalid(field, error):
    company = create_company(**{field: ""})

    result = CompanyQualityChecker().check(company)

    assert result.valid is False
    assert error in result.errors


def test_company_with_negative_market_cap_is_invalid():
    company = create_company(market_cap=-1000000)

    result = CompanyQualityChecker().check(company)

    assert result.valid is False
    assert result.errors == ["market cap cannot be negative"]


def test_company_with_invalid_beta_is_invalid():
    company = create_company(beta=float("nan"))

    result = CompanyQualityChecker().check(company)

    assert result.valid is False
    assert result.errors == ["beta must be a finite number"]


def test_company_with_invalid_profit_margin_is_invalid():
    company = create_company(profit_margin=1.5)

    result = CompanyQualityChecker().check(company)

    assert result.valid is False
    assert result.errors == [
        "profit margin must be between -1 and 1"
    ]


def test_company_with_invalid_operating_margin_is_invalid():
    company = create_company(operating_margin=-10.326)

    result = CompanyQualityChecker().check(company)

    assert result.valid is False
    assert result.errors == [
        "operating margin must be between -1 and 1"
    ]

def create_financial_statement(**overrides):
    data = {
        "ticker": "AAPL",
        "fiscal_date": "2025-09-30",
        "report_type": "annual",
        "currency": "USD",
        "revenue": 416161000000,
        "gross_profit": 195201000000,
        "operating_income": 133050000000,
        "net_income": 112010000000,
        "ebitda": 144427000000,
        "total_assets": 359241000000,
        "total_liabilities": 285508000000,
        "total_equity": 73733000000,
        "cash": 35934000000,
        "inventory": 5718000000,
        "total_debt": 112377000000,
        "operating_cash_flow": 111482000000,
        "capital_expenditure": 12715000000,
        "investing_cash_flow": 15195000000,
        "financing_cash_flow": -120686000000,
        "free_cash_flow": 98767000000,
    }

    data.update(overrides)

    from datetime import date

    if isinstance(data["fiscal_date"], str):
        data["fiscal_date"] = date.fromisoformat(data["fiscal_date"])

    return FinancialStatementRecord(**data)


def test_valid_financial_statement_record():
    record = create_financial_statement()

    result = FinancialStatementQualityChecker().check(record)

    assert result.valid is True
    assert result.errors == []


def test_financial_statement_with_negative_balance_sheet_value_is_invalid():
    record = create_financial_statement(total_assets=-100)

    result = FinancialStatementQualityChecker().check(record)

    assert result.valid is False
    assert result.errors == ["total_assets cannot be negative"]