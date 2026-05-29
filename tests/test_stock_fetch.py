from unittest.mock import patch, MagicMock

import pytest
import requests as req

from src.stock_fetch import get_top_movers, _last_trading_day


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    monkeypatch.setenv("ALPHA_VANTAGE_KEY", "test_key")


def _mock_resp(data):
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = data
    return mock


_SAMPLE = {
    "top_gainers": [
        {"ticker": "AAA", "price": "10.00", "change_percentage": "+9.0%"},
        {"ticker": "BBB", "price": "20.00", "change_percentage": "+8.0%"},
        {"ticker": "CCC", "price": "30.00", "change_percentage": "+7.0%"},
        {"ticker": "DDD", "price": "40.00", "change_percentage": "+6.0%"},
        {"ticker": "EEE", "price": "50.00", "change_percentage": "+5.0%"},
        {"ticker": "FFF", "price": "60.00", "change_percentage": "+4.0%"},
    ],
    "top_losers": [
        {"ticker": "ZZZ", "price": "5.00", "change_percentage": "-9.0%"},
        {"ticker": "YYY", "price": "6.00", "change_percentage": "-8.0%"},
        {"ticker": "XXX", "price": "7.00", "change_percentage": "-7.0%"},
        {"ticker": "WWW", "price": "8.00", "change_percentage": "-6.0%"},
        {"ticker": "VVV", "price": "9.00", "change_percentage": "-5.0%"},
    ],
}


def test_success():
    with patch("src.stock_fetch.requests.get", return_value=_mock_resp(_SAMPLE)):
        result = get_top_movers()
    assert result["error"] is None
    assert len(result["top_gainers"]) == 5   # sliced to 5
    assert len(result["top_losers"]) == 5
    assert result["top_gainers"][0]["ticker"] == "AAA"
    assert result["top_losers"][0]["ticker"] == "ZZZ"


def test_slices_to_five():
    with patch("src.stock_fetch.requests.get", return_value=_mock_resp(_SAMPLE)):
        result = get_top_movers()
    assert len(result["top_gainers"]) == 5  # 6 in sample, capped at 5


def test_rate_limited_note():
    data = {"Note": "Thank you for using Alpha Vantage! Our standard API call frequency is ..."}
    with patch("src.stock_fetch.requests.get", return_value=_mock_resp(data)):
        result = get_top_movers()
    assert result["error"] is not None
    assert "Rate limited" in result["error"]


def test_rate_limited_information():
    data = {"Information": "The **standard** API rate limit is 25 requests per day"}
    with patch("src.stock_fetch.requests.get", return_value=_mock_resp(data)):
        result = get_top_movers()
    assert result["error"] is not None


def test_network_error():
    with patch("src.stock_fetch.requests.get", side_effect=req.RequestException("timeout")):
        result = get_top_movers()
    assert result["error"] is not None
    assert result["top_gainers"] == []


def test_missing_key(monkeypatch):
    monkeypatch.delenv("ALPHA_VANTAGE_KEY", raising=False)
    result = get_top_movers()
    assert result["error"] is not None


def test_last_trading_day_not_weekend():
    from datetime import date
    d = _last_trading_day()
    weekday = date.fromisoformat(d).weekday()
    assert weekday < 5  # 0=Mon … 4=Fri
