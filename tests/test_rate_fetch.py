import os
from unittest.mock import patch, MagicMock

import pytest
import requests as req

from src.rate_fetch import get_15yr_rate


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    monkeypatch.setenv("FRED_API_KEY", "test_key")


def _mock_resp(value="6.78", date="2026-05-22"):
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = {"observations": [{"date": date, "value": value}]}
    return mock


def test_success():
    with patch("src.rate_fetch.requests.get", return_value=_mock_resp()):
        result = get_15yr_rate()
    assert result["rate_pct"] == 6.78
    assert result["as_of_date"] == "2026-05-22"
    assert result["error"] is None


def test_missing_value_dot():
    with patch("src.rate_fetch.requests.get", return_value=_mock_resp(value=".")):
        result = get_15yr_rate()
    assert result["rate_pct"] is None
    assert result["error"] is not None


def test_out_of_range():
    with patch("src.rate_fetch.requests.get", return_value=_mock_resp(value="0.5")):
        result = get_15yr_rate()
    assert result["rate_pct"] is None
    assert "range" in result["error"]


def test_network_error():
    with patch("src.rate_fetch.requests.get", side_effect=req.RequestException("timeout")):
        result = get_15yr_rate()
    assert result["rate_pct"] is None
    assert result["error"] is not None


def test_missing_key(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    result = get_15yr_rate()
    assert result["error"] is not None
