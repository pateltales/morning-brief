import io
from unittest.mock import patch, MagicMock

import pandas as pd
import requests as req

from src.housing_fetch import get_city_values, TARGET_CITIES

_CSV_HEADER = "RegionID,SizeRank,RegionName,RegionType,StateName,State,Metro,CountyName,2026-03-31,2026-04-30\n"
_CSV_ROWS = (
    "1,1,Seattle,City,WA,WA,Seattle-Tacoma,King County,860000,871598\n"
    "2,2,Bellevue,City,WA,WA,Seattle-Tacoma,King County,1500000,1527243\n"
    "3,3,Redmond,City,WA,WA,Seattle-Tacoma,King County,1380000,1408840\n"
    "4,4,Everett,City,WA,WA,Seattle-Tacoma,Snohomish County,650000,665405\n"
    "5,5,Kent,City,WA,WA,Seattle-Tacoma,King County,640000,657910\n"
    "6,6,Lynnwood,City,WA,WA,Seattle-Tacoma,Snohomish County,770000,786226\n"
    "7,7,Shoreline,City,WA,WA,Seattle-Tacoma,King County,820000,832251\n"
    "8,8,Los Angeles,City,CA,CA,Los Angeles,LA County,900000,910000\n"
)
_SAMPLE_CSV = _CSV_HEADER + _CSV_ROWS


def _mock_resp(text=_SAMPLE_CSV, status=200):
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.text = text
    mock.status_code = status
    return mock


def test_success():
    with patch("src.housing_fetch.requests.get", return_value=_mock_resp()):
        result = get_city_values()
    assert result["error"] is None
    assert result["as_of_month"] == "2026-04"
    assert result["Seattle"] == 871598
    assert result["Bellevue"] == 1527243


def test_all_target_cities_present():
    with patch("src.housing_fetch.requests.get", return_value=_mock_resp()):
        result = get_city_values()
    for city in TARGET_CITIES:
        assert city in result
        assert result[city] is not None


def test_non_wa_cities_excluded():
    with patch("src.housing_fetch.requests.get", return_value=_mock_resp()):
        result = get_city_values()
    assert "Los Angeles" not in result


def test_missing_city_returns_none():
    csv = _CSV_HEADER + "1,1,Seattle,City,WA,WA,Metro,County,860000,871598\n"
    with patch("src.housing_fetch.requests.get", return_value=_mock_resp(text=csv)):
        result = get_city_values()
    assert result["Bellevue"] is None  # not in the CSV


def test_network_error():
    with patch("src.housing_fetch.requests.get", side_effect=req.RequestException("timeout")):
        result = get_city_values()
    assert result["error"] is not None
    assert result["Seattle"] is None


def test_empty_wa_rows():
    csv = _CSV_HEADER + "1,1,Portland,City,OR,OR,Portland,Multnomah,400000,410000\n"
    with patch("src.housing_fetch.requests.get", return_value=_mock_resp(text=csv)):
        result = get_city_values()
    assert result["error"] is not None
