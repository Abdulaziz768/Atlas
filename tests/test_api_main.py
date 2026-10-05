from unittest.mock import patch

from fastapi.testclient import TestClient

from atlas.api.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_stocks():
    mock_data = [
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

    with patch(
        "atlas.api.main.get_stock_performance",
        return_value=mock_data,
    ):
        response = client.get("/stocks")

    assert response.status_code == 200
    assert response.json() == mock_data


def test_get_stock():
    mock_stock = {
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

    with patch(
        "atlas.api.main.get_stock_performance_by_ticker",
        return_value=mock_stock,
    ):
        response = client.get("/stocks/AAPL")

    assert response.status_code == 200
    assert response.json() == mock_stock


def test_get_stock_not_found():
    with patch(
        "atlas.api.main.get_stock_performance_by_ticker",
        return_value=None,
    ):
        response = client.get("/stocks/TSLA")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Stock 'TSLA' not found"
    }
