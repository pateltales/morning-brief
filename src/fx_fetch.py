import requests

FRANKFURTER_URL = "https://api.frankfurter.app/latest"


def get_usd_inr() -> dict:
    try:
        resp = requests.get(FRANKFURTER_URL, params={"from": "USD", "to": "INR"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        rate = float(data["rates"]["INR"])
        if not (50 <= rate <= 200):
            return {"usd_to_inr": None, "as_of_date": None, "error": f"Rate {rate} outside expected range (50–200)"}
        return {"usd_to_inr": rate, "as_of_date": data["date"], "error": None}
    except requests.RequestException as e:
        return {"usd_to_inr": None, "as_of_date": None, "error": str(e)}
    except (KeyError, ValueError) as e:
        return {"usd_to_inr": None, "as_of_date": None, "error": f"Parse error: {e}"}
