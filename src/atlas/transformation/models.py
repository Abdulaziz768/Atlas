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
    open : float
    high: float
    low: float
    close: float
    volume: int | None
