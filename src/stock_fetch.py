import os
from datetime import date, timedelta

import requests

ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"


def _last_trading_day() -> str:
    d = date.today() - timedelta(days=1)
    while d.weekday() >= 5:  # skip Saturday=5, Sunday=6
        d -= timedelta(days=1)
    return d.isoformat()


def _parse_entries(entries: list) -> list:
    return [
        {
            "ticker": e["ticker"],
            "price": e["price"],
            "change_pct": e["change_percentage"],
        }
        for e in entries[:5]
    ]


def get_top_movers() -> dict:
    api_key = os.getenv("ALPHA_VANTAGE_KEY")
    if not api_key:
        return {"top_gainers": [], "top_losers": [], "as_of_date": None, "error": "ALPHA_VANTAGE_KEY not set"}
    try:
        resp = requests.get(
            ALPHA_VANTAGE_URL,
            params={"function": "TOP_GAINERS_LOSERS", "apikey": api_key},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        if "Note" in data or "Information" in data:
            msg = data.get("Note") or data.get("Information")
            return {"top_gainers": [], "top_losers": [], "as_of_date": None, "error": f"Rate limited: {msg}"}

        return {
            "top_gainers": _parse_entries(data.get("top_gainers", [])),
            "top_losers": _parse_entries(data.get("top_losers", [])),
            "as_of_date": _last_trading_day(),
            "error": None,
        }
    except requests.RequestException as e:
        return {"top_gainers": [], "top_losers": [], "as_of_date": None, "error": str(e)}
    except (KeyError, ValueError) as e:
        return {"top_gainers": [], "top_losers": [], "as_of_date": None, "error": f"Parse error: {e}"}
