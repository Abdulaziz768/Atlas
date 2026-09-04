from atlas.transformation.company import CompanyTransformer

def test_company_transformation():
    raw_data = {
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

    transformer = CompanyTransformer()

    company = transformer.transform(raw_data)

    assert company.market_cap == 4742524699000
    assert isinstance(company.market_cap, int)

    assert company.pe_ratio == 37.31
    assert isinstance(company.pe_ratio, float)


def test_company_transformation_handles_empty_values():
    raw_data = {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
        "Exchange": "NASDAQ",
        "Currency": "USD",
        "Sector": "TECHNOLOGY",
        "Industry": "CONSUMER ELECTRONICS",
        "MarketCapitalization": "",
        "EBITDA": "",
        "PERatio": "",
        "EPS": "",
        "RevenueTTM": "",
        "ProfitMargin": "",
        "OperatingMarginTTM": "",
        "ReturnOnEquityTTM": "",
        "Beta": "",
    }

    transformer = CompanyTransformer()

    company = transformer.transform(raw_data)

    assert company.market_cap is None
    assert company.ebitda is None
    assert company.pe_ratio is None
    assert company.eps is None
    assert company.revenue_ttm is None
    assert company.profit_margin is None
    assert company.operating_margin is None
    assert company.return_on_equity is None
    assert company.beta is None

def test_company_transformation_handles_invalid_values():
    raw_data = {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
        "Exchange": "NASDAQ",
        "Currency": "USD",
        "Sector": "TECHNOLOGY",
        "Industry": "CONSUMER ELECTRONICS",
        "MarketCapitalization": "abcd",
        "EBITDA": "not-a-number",
        "PERatio": "N/A",
        "EPS": "invalid",
        "RevenueTTM": "unknown",
        "ProfitMargin": "N/A",
        "OperatingMarginTTM": "hello",
        "ReturnOnEquityTTM": "None",
        "Beta": "xyz",
    }

    transformer = CompanyTransformer()

    company = transformer.transform(raw_data)

    assert company.market_cap is None
    assert company.ebitda is None
    assert company.pe_ratio is None
    assert company.eps is None
    assert company.revenue_ttm is None
    assert company.profit_margin is None
    assert company.operating_margin is None
    assert company.return_on_equity is None
    assert company.beta is None

def test_company_transformation_handles_missing_fields():
    raw_data = {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
        "Exchange": "NASDAQ",
        "Currency": "USD",
        "Sector": "TECHNOLOGY",
        "Industry": "CONSUMER ELECTRONICS",
    }

    transformer = CompanyTransformer()

    company = transformer.transform(raw_data)

    assert company.market_cap is None
    assert company.ebitda is None
    assert company.pe_ratio is None
    assert company.eps is None
    assert company.revenue_ttm is None
    assert company.profit_margin is None
    assert company.operating_margin is None
    assert company.return_on_equity is None
    assert company.beta is None