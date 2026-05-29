import io

import pandas as pd
import requests

ZHVI_URL = (
    "https://files.zillowstatic.com/research/public_csvs/zhvi/"
    "City_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
)

TARGET_CITIES = ["Seattle", "Lynnwood", "Shoreline", "Everett", "Kent", "Bellevue", "Redmond"]

_ERROR_BASE = {city: None for city in TARGET_CITIES}


def get_city_values() -> dict:
    try:
        resp = requests.get(ZHVI_URL, timeout=30)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text))

        wa = df[(df["StateName"] == "WA") & (df["RegionName"].isin(TARGET_CITIES))]
        if wa.empty:
            return _ERROR_BASE | {"as_of_month": None, "error": "No matching WA cities found in Zillow CSV"}

        latest_col = df.columns[-1]
        as_of_month = latest_col[:7]  # "YYYY-MM"

        result = {city: None for city in TARGET_CITIES}
        for _, row in wa.iterrows():
            city = row["RegionName"]
            val = row[latest_col]
            result[city] = int(val) if pd.notna(val) else None

        return result | {"as_of_month": as_of_month, "error": None}

    except requests.RequestException as e:
        return _ERROR_BASE | {"as_of_month": None, "error": str(e)}
    except Exception as e:
        return _ERROR_BASE | {"as_of_month": None, "error": f"Parse error: {e}"}
