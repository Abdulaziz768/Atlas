import pytest

from atlas.quality.company import CompanyQualityChecker
from atlas.transformation.models import CompanyRecord


def create_company(**overrides):
    data = {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "exchange": "NASDAQ",
        "currency": "USD",
        "sector": "TECHNOLOGY",
        "industry": "CONSUMER ELECTRONICS",
    }

    data.update(overrides)
    return CompanyRecord(**data)


def test_valid_company_is_valid():
    company = create_company()

    checker = CompanyQualityChecker()
    result = checker.check(company)

    assert result.valid is True
    assert result.errors == []


@pytest.mark.parametrize(
    "field, error_message",
    [
        ("ticker", "ticker is missing"),
        ("name", "company name is missing"),
        ("exchange", "exchange is missing"),
        ("currency", "currency is missing"),
        ("sector", "sector is missing"),
        ("industry", "industry is missing"),
    ],
)
def test_company_required_field_is_invalid(field, error_message):
    company = create_company(**{field: ""})

    checker = CompanyQualityChecker()
    result = checker.check(company)

    assert result.valid is False
    assert error_message in result.errors