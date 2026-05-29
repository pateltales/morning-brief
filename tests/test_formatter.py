from src.formatter import build_message

_STOCK = {
    "top_gainers": [{"ticker": "AAA", "price": "10.00", "change_pct": "+9.0%"}],
    "top_losers":  [{"ticker": "ZZZ", "price": "5.00",  "change_pct": "-9.0%"}],
    "as_of_date": "2026-05-28",
    "error": None,
}
_RATE    = {"rate_pct": 6.78, "as_of_date": "2026-05-22", "error": None}
_FX      = {"usd_to_inr": 83.47, "as_of_date": "2026-05-28", "error": None}
_HOUSING = {
    "Seattle": 871598, "Lynnwood": 786226, "Shoreline": 832251,
    "Everett": 665405, "Kent": 657910, "Bellevue": 1527243, "Redmond": 1408840,
    "as_of_month": "2026-04", "error": None,
}


def test_returns_discord_embed_shape():
    payload = build_message(_STOCK, _RATE, _FX, _HOUSING)
    assert "embeds" in payload
    assert len(payload["embeds"]) == 1
    embed = payload["embeds"][0]
    assert "title" in embed
    assert "fields" in embed
    assert "footer" in embed


def test_field_count():
    payload = build_message(_STOCK, _RATE, _FX, _HOUSING)
    fields = payload["embeds"][0]["fields"]
    assert len(fields) == 5  # gainers, losers, rate, fx, housing


def test_mortgage_rate_in_output():
    payload = build_message(_STOCK, _RATE, _FX, _HOUSING)
    rate_field = next(f for f in payload["embeds"][0]["fields"] if "Mortgage" in f["name"])
    assert "6.78" in rate_field["value"]


def test_fx_rate_in_output():
    payload = build_message(_STOCK, _RATE, _FX, _HOUSING)
    fx_field = next(f for f in payload["embeds"][0]["fields"] if "INR" in f["name"])
    assert "83.47" in fx_field["value"]


def test_housing_values_formatted_with_commas():
    payload = build_message(_STOCK, _RATE, _FX, _HOUSING)
    housing_field = next(f for f in payload["embeds"][0]["fields"] if "Home Values" in f["name"])
    assert "1,527,243" in housing_field["value"]


def test_stock_error_shows_warning():
    stock_err = {**_STOCK, "error": "Rate limited", "top_gainers": [], "top_losers": []}
    payload = build_message(stock_err, _RATE, _FX, _HOUSING)
    gainers = next(f for f in payload["embeds"][0]["fields"] if "Gainers" in f["name"])
    assert "unavailable" in gainers["value"]


def test_fx_error_shows_warning():
    fx_err = {**_FX, "error": "timeout", "usd_to_inr": None}
    payload = build_message(_STOCK, _RATE, fx_err, _HOUSING)
    fx_field = next(f for f in payload["embeds"][0]["fields"] if "INR" in f["name"])
    assert "unavailable" in fx_field["value"]


def test_housing_none_values_show_dash():
    housing_partial = {**_HOUSING, "Bellevue": None}
    payload = build_message(_STOCK, _RATE, _FX, housing_partial)
    housing_field = next(f for f in payload["embeds"][0]["fields"] if "Home Values" in f["name"])
    assert "—" in housing_field["value"]
