from unittest.mock import Mock, patch

from atlas.ingestion.client import APIClient


def test_get_returns_response_data():
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
    }

    with patch("atlas.ingestion.client.requests.get", return_value=response):
        client = APIClient(
            base_url="https://example.com",
        )

        result = client.get("")

    assert result == {
        "Symbol": "AAPL",
        "Name": "Apple Inc.",
    }
    
def test_get_retries_on_provider_error():
    first_response = Mock()
    first_response.status_code = 200
    first_response.json.return_value = {
        "Information": "Rate limit exceeded"
    }

    second_response = Mock()
    second_response.status_code = 200
    second_response.json.return_value = {
        "Information": "Rate limit exceeded"
    }

    third_response = Mock()
    third_response.status_code = 200
    third_response.json.return_value = {
        "Information": "Rate limit exceeded"
    }

    final_response = Mock()
    final_response.status_code = 200
    final_response.json.return_value = {
        "Symbol": "NVDA"
    }

    with patch(
        "atlas.ingestion.client.requests.get",
        side_effect=[
            first_response,
            second_response,
            third_response,
            final_response,
        ],
    ), patch("atlas.ingestion.client.time.sleep"):

        client = APIClient(
            base_url="https://example.com",
            max_retries=3,
            retry_backoff=2,
        )

        result = client.get("")

    assert result == {"Symbol": "NVDA"}