from dataclasses import dataclass
from datetime import date

@dataclass
class CompanyRecord:
    ticker: str
    name: str
    exchange: str
    currency: str
    sector: str
    industry: str

    market_cap: int | None
    ebitda: int | None
    pe_ratio: float | None
    eps: float | None
    revenue_ttm: int | None
    profit_margin: float | None
    operating_margin: float | None
    return_on_equity: float | None

    beta: float | None    

@dataclass
class StockPriceRecord:
    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int | None

@dataclass
class FinancialStatementRecord:
    ticker: str
    fiscal_date: date
    report_type: str
    currency: str

    revenue: int | None
    gross_profit: int | None
    operating_income: int | None
    net_income: int | None
    ebitda: int | None

    total_assets: int | None
    total_liabilities: int | None
    total_equity: int | None
    cash: int | None
    inventory: int | None
    total_debt: int | None

    operating_cash_flow: int | None
    capital_expenditure: int | None
    investing_cash_flow: int | None
    financing_cash_flow: int | None
    free_cash_flow: int | None

@dataclass
class FundamentalsRecord:
    ticker: str
    as_of_date: date | None
    currency: str

    # Valuation
    market_cap: int | None
    pe_ratio: float | None
    forward_pe: float | None
    peg_ratio: float | None
    price_to_sales: float | None
    price_to_book: float | None
    ev_to_revenue: float | None
    ev_to_ebitda: float | None

    # Profitability
    eps: float | None
    diluted_eps_ttm: float | None
    revenue_ttm: int | None
    revenue_per_share_ttm: float | None
    gross_profit_ttm: int | None
    ebitda: int | None
    profit_margin: float | None
    operating_margin: float | None
    return_on_assets: float | None
    return_on_equity: float | None

    # Growth
    quarterly_earnings_growth_yoy: float | None
    quarterly_revenue_growth_yoy: float | None

    # Dividends
    dividend_per_share: float | None
    dividend_yield: float | None

    # Market
    beta: float | None
    week_52_high: float | None
    week_52_low: float | None
    moving_average_50_day: float | None
    moving_average_200_day: float | None

    # Ownership
    shares_outstanding: int | None
    shares_float: int | None
    percent_insiders: float | None
    percent_institutions: float | None