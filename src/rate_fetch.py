import os
import requests

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"


def get_15yr_rate() -> dict:
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        return {"rate_pct": None, "as_of_date": None, "error": "FRED_API_KEY not set"}
    try:
        resp = requests.get(
            FRED_URL,
            params={
                "series_id": "MORTGAGE15US",
                "api_key": api_key,
                "sort_order": "desc",
                "limit": 1,
                "file_type": "json",
            },
            timeout=10,
        )
        resp.raise_for_status()
        obs = resp.json()["observations"][0]
        if obs["value"] == ".":
            return {"rate_pct": None, "as_of_date": obs["date"], "error": "FRED returned missing value"}
        rate = float(obs["value"])
        if not (2 <= rate <= 15):
            return {"rate_pct": None, "as_of_date": None, "error": f"Rate {rate} outside expected range (2–15)"}
        return {"rate_pct": rate, "as_of_date": obs["date"], "error": None}
    except requests.RequestException as e:
        return {"rate_pct": None, "as_of_date": None, "error": str(e)}
    except (KeyError, ValueError, IndexError) as e:
        return {"rate_pct": None, "as_of_date": None, "error": f"Parse error: {e}"}
