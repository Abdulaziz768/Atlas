from math import isfinite

from atlas.quality.models import QualityResult


class FundamentalsQualityChecker:
    """Validate fundamentals records."""

    def check(self, record):
        errors = []

        if not record.ticker:
            errors.append("ticker is missing")

        if record.as_of_date is None:
            errors.append("as of date is missing")

        if not record.currency:
            errors.append("currency is missing")

        numeric_fields = {
            "market_cap": record.market_cap,
            "pe_ratio": record.pe_ratio,
            "forward_pe": record.forward_pe,
            "peg_ratio": record.peg_ratio,
            "price_to_sales": record.price_to_sales,
            "price_to_book": record.price_to_book,
            "ev_to_revenue": record.ev_to_revenue,
            "ev_to_ebitda": record.ev_to_ebitda,
            "eps": record.eps,
            "diluted_eps_ttm": record.diluted_eps_ttm,
            "revenue_ttm": record.revenue_ttm,
            "revenue_per_share_ttm": record.revenue_per_share_ttm,
            "gross_profit_ttm": record.gross_profit_ttm,
            "ebitda": record.ebitda,
            "profit_margin": record.profit_margin,
            "operating_margin": record.operating_margin,
            "return_on_assets": record.return_on_assets,
            "return_on_equity": record.return_on_equity,
            "quarterly_earnings_growth_yoy": (
                record.quarterly_earnings_growth_yoy
            ),
            "quarterly_revenue_growth_yoy": (
                record.quarterly_revenue_growth_yoy
            ),
            "dividend_per_share": record.dividend_per_share,
            "dividend_yield": record.dividend_yield,
            "beta": record.beta,
            "week_52_high": record.week_52_high,
            "week_52_low": record.week_52_low,
            "moving_average_50_day": record.moving_average_50_day,
            "moving_average_200_day": record.moving_average_200_day,
            "shares_outstanding": record.shares_outstanding,
            "shares_float": record.shares_float,
            "percent_insiders": record.percent_insiders,
            "percent_institutions": record.percent_institutions,
        }

        for field_name, value in numeric_fields.items():
            if value is not None and not isfinite(value):
                errors.append(f"{field_name} must be finite")

        non_negative_fields = {
            "market_cap": record.market_cap,
            "revenue_ttm": record.revenue_ttm,
            "gross_profit_ttm": record.gross_profit_ttm,
            "shares_outstanding": record.shares_outstanding,
            "shares_float": record.shares_float,
        }

        for field_name, value in non_negative_fields.items():
            if value is not None and value < 0:
                errors.append(f"{field_name} cannot be negative")

        return QualityResult(
            valid=len(errors) == 0,
            errors=errors,
        )