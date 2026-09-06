import pytest

from atlas.transformation.company import CompanyTransformer


def create_company_data(**overrides):
    data = {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
        "Exchange": "NASDAQ",
        "Currency": "USD",
        "Sector": "TECHNOLOGY",
        "Industry": "CONSUMER ELECTRONICS",
        "MarketCapitalization": "4742524699000",
        "EBITDA": "167959003000",
        "PERatio": "37.31",
        "EPS": "8.71",
        "RevenueTTM": "466822988000",
        "ProfitMargin": "0.276",
        "OperatingMarginTTM": "0.326",
        "ReturnOnEquityTTM": "1.488",
        "Beta": "1.086",
    }

    data.update(overrides)
    return data


def test_company_transformation():
    company = CompanyTransformer().transform(create_company_data())

    assert company.ticker == "AAPL"
    assert company.name == "Apple Inc."
    assert company.market_cap == 4742524699000
    assert isinstance(company.market_cap, int)
    assert company.pe_ratio == 37.31
    assert isinstance(company.pe_ratio, float)


@pytest.mark.parametrize(
    "overrides",
    [
        {
            "MarketCapitalization": "",
            "EBITDA": "",
            "PERatio": "",
            "EPS": "",
            "RevenueTTM": "",
            "ProfitMargin": "",
            "OperatingMarginTTM": "",
            "ReturnOnEquityTTM": "",
            "Beta": "",
        },
        {
            "MarketCapitalization": "abcd",
            "EBITDA": "not-a-number",
            "PERatio": "N/A",
            "EPS": "invalid",
            "RevenueTTM": "unknown",
            "ProfitMargin": "N/A",
            "OperatingMarginTTM": "hello",
            "ReturnOnEquityTTM": "None",
            "Beta": "xyz",
        },
        {
            # Optional fields completely absent
        },
    ],
)
def test_company_transformation_handles_invalid_or_missing_optional_fields(
    overrides
):
    data = create_company_data(**overrides)

    if not overrides:
        for field in [
            "MarketCapitalization",
            "EBITDA",
            "PERatio",
            "EPS",
            "RevenueTTM",
            "ProfitMargin",
            "OperatingMarginTTM",
            "ReturnOnEquityTTM",
            "Beta",
        ]:
            data.pop(field)

    company = CompanyTransformer().transform(data)

    assert company.market_cap is None
    assert company.ebitda is None
    assert company.pe_ratio is None
    assert company.eps is None
    assert company.revenue_ttm is None
    assert company.profit_margin is None
    assert company.operating_margin is None
    assert company.return_on_equity is None
    assert company.beta is None