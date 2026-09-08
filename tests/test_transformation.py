from atlas.transformation.company import CompanyTransformer


def create_company_data():
    return {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
        "Exchange": "NASDAQ",
        "Sector": "TECHNOLOGY",
        "Industry": "CONSUMER ELECTRONICS",
        "Currency": "USD",
        "MarketCapitalization": "3000000000000",
        "EBITDA": "100000000000",
        "PERatio": "30.5",
        "EPS": "6.15",
        "RevenueTTM": "400000000000",
        "ProfitMargin": "0.25",
        "OperatingMarginTTM": "0.30",
        "ReturnOnEquityTTM": "1.50",
        "Beta": "1.20",
    }


def test_company_transformation():
    company = CompanyTransformer().transform(create_company_data())

    assert company.ticker == "AAPL"
    assert company.name == "Apple Inc."
    assert company.exchange == "NASDAQ"
    assert company.currency == "USD"
    assert company.sector == "TECHNOLOGY"
    assert company.industry == "CONSUMER ELECTRONICS"