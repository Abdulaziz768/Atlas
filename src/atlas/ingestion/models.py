from dataclasses import dataclass

@dataclass
class Company:
    ticker : str
    name : str
    exchange : str
    sector : str
    industry : str
    currency : str
    market_cap : float | None
    description : str | None
