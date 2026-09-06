from atlas.quality.company import QualityResult


class StockPriceQualityChecker:

    def check(self, record):
        errors = []

        if not record.ticker:
            errors.append("ticker is missing")

        if record.date is None:
            errors.append("date is missing")

        if record.open is None:
            errors.append("open price is missing")

        if record.high is None:
            errors.append("high price is missing")

        if record.low is None:
            errors.append("low price is missing")

        if record.close is None:
            errors.append("close price is missing")

        if record.open is not None and record.open < 0:
            errors.append("open price cannot be negative")

        if record.high is not None and record.high < 0:
            errors.append("high price cannot be negative")

        if record.low is not None and record.low < 0:
            errors.append("low price cannot be negative")

        if record.close is not None and record.close < 0:
            errors.append("close price cannot be negative")

        if record.volume is not None and record.volume < 0:
            errors.append("volume cannot be negative")

        if (
            record.high is not None
            and record.open is not None
            and record.high < record.open
        ):
            errors.append("high price cannot be lower than open price")

        if (
            record.high is not None
            and record.close is not None
            and record.high < record.close
        ):
            errors.append("high price cannot be lower than close price")

        if (
            record.low is not None
            and record.open is not None
            and record.low > record.open
        ):
            errors.append("low price cannot be higher than open price")

        if (
            record.low is not None
            and record.close is not None
            and record.low > record.close
        ):
            errors.append("low price cannot be higher than close price")

        return QualityResult(
            valid=len(errors) == 0,
            errors=errors,
        )