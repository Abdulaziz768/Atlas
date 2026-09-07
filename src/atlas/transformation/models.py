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