from unittest.mock import Mock, patch

from atlas.api.snowflake import get_stock_performance


def test_get_stock_performance_returns_rows():
    connection = Mock()
    cursor = Mock()

    cursor.description = [
        ("TICKER",),
        ("FIRST_DATE",),
        ("LATEST_DATE",),
        ("FIRST_CLOSE",),
        ("LATEST_CLOSE",),
        ("TOTAL_RETURN_PCT",),
        ("AVERAGE_DAILY_RETURN_PCT",),
        ("BEST_DAY_RETURN_PCT",),
        ("WORST_DAY_RETURN_PCT",),
        ("TOTAL_VOLUME",),
        ("TRADING_DAYS",),
    ]

    cursor.fetchall.return_value = [
        (
            "AAPL",
            "2026-04-15",
            "2026-10-02",
            266.43,
            333.69,
            25.24,
            0.24,
            4.93,
            -4.26,
            6011682841,
            119,
        )
    ]

    connection.cursor.return_value = cursor

    with patch(
        "atlas.api.snowflake.get_connection",
        return_value=connection,
    ):
        result = get_stock_performance()

    assert result == [
        {
            "ticker": "AAPL",
            "first_date": "2026-04-15",
            "latest_date": "2026-10-02",
            "first_close": 266.43,
            "latest_close": 333.69,
            "total_return_pct": 25.24,
            "average_daily_return_pct": 0.24,
            "best_day_return_pct": 4.93,
            "worst_day_return_pct": -4.26,
            "total_volume": 6011682841,
            "trading_days": 119,
        }
    ]

    cursor.execute.assert_called_once()
    connection.close.assert_called_once()
