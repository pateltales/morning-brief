from unittest.mock import patch, MagicMock
from src.fx_fetch import get_usd_inr


def test_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"rates": {"INR": 83.47}, "date": "2026-05-27"}
    mock_resp.raise_for_status = MagicMock()
    with patch("src.fx_fetch.requests.get", return_value=mock_resp):
        result = get_usd_inr()
    assert result["usd_to_inr"] == 83.47
    assert result["as_of_date"] == "2026-05-27"
    assert result["error"] is None


def test_network_error():
    import requests as req
    with patch("src.fx_fetch.requests.get", side_effect=req.RequestException("timeout")):
        result = get_usd_inr()
    assert result["usd_to_inr"] is None
    assert result["error"] is not None


def test_out_of_range_rate():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"rates": {"INR": 5.0}, "date": "2026-05-27"}
    mock_resp.raise_for_status = MagicMock()
    with patch("src.fx_fetch.requests.get", return_value=mock_resp):
        result = get_usd_inr()
    assert result["usd_to_inr"] is None
    assert "range" in result["error"]
