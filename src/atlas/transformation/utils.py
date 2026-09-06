from datetime import date

def to_int(value: str | None) -> int | None:
    if not value:
        return None

    try:
        return int(value)
    except ValueError:
        return None


def to_float(value: str | None) -> float | None:
    if not value:
        return None

    try:
        return float(value)
    except ValueError:
        return None


def to_date(value: str | None) -> date | None:
    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None
