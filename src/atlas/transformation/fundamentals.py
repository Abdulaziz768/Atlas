from datetime import date
from typing import Any

from atlas.transformation.models import FundamentalsRecord
from atlas.transformation.utils import to_float, to_int


class FundamentalsTransformer:
    """Transform raw company fundamental data into structured FundamentalsRecord."""

    def __init__(self, as_of_date: date):
        self.as_of_date = as_of_date

    def transform(self, data: dict[str, Any]) -> FundamentalsRecord:
        return FundamentalsRecord(
            ticker=data["Symbol"],
            as_of_date=self.as_of_date,
            currency=data["Currency"],

            # Valuation
            market_cap=to_int(data.get("MarketCapitalization")),
            pe_ratio=to_float(data.get("PERatio")),
            forward_pe=to_float(data.get("ForwardPE")),
            peg_ratio=to_float(data.get("PEGRatio")),
            price_to_sales=to_float(data.get("PriceToSalesRatioTTM")),
            price_to_book=to_float(data.get("PriceToBookRatio")),
            ev_to_revenue=to_float(data.get("EVToRevenue")),
            ev_to_ebitda=to_float(data.get("EVToEBITDA")),

            # Profitability
            eps=to_float(data.get("EPS")),
            diluted_eps_ttm=to_float(data.get("DilutedEPSTTM")),
            revenue_ttm=to_int(data.get("RevenueTTM")),
            revenue_per_share_ttm=to_float(data.get("RevenuePerShareTTM")),
            gross_profit_ttm=to_int(data.get("GrossProfitTTM")),
            ebitda=to_int(data.get("EBITDA")),
            profit_margin=to_float(data.get("ProfitMargin")),
            operating_margin=to_float(data.get("OperatingMarginTTM")),
            return_on_assets=to_float(data.get("ReturnOnAssetsTTM")),
            return_on_equity=to_float(data.get("ReturnOnEquityTTM")),

            # Growth
            quarterly_earnings_growth_yoy=to_float(
                data.get("QuarterlyEarningsGrowthYOY")
            ),
            quarterly_revenue_growth_yoy=to_float(
                data.get("QuarterlyRevenueGrowthYOY")
            ),

            # Dividends
            dividend_per_share=to_float(data.get("DividendPerShare")),
            dividend_yield=to_float(data.get("DividendYield")),

            # Market
            beta=to_float(data.get("Beta")),
            week_52_high=to_float(data.get("52WeekHigh")),
            week_52_low=to_float(data.get("52WeekLow")),
            moving_average_50_day=to_float(
                data.get("50DayMovingAverage")
            ),
            moving_average_200_day=to_float(
                data.get("200DayMovingAverage")
            ),

            # Ownership
            shares_outstanding=to_int(data.get("SharesOutstanding")),
            shares_float=to_int(data.get("SharesFloat")),
            percent_insiders=to_float(data.get("PercentInsiders")),
            percent_institutions=to_float(data.get("PercentInstitutions")),
        )