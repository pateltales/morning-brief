import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

from src import discord_notify, formatter, fx_fetch, housing_fetch, rate_fetch, stock_fetch


def run() -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] Morning Brief starting...")

    fx      = fx_fetch.get_usd_inr()
    rate    = rate_fetch.get_15yr_rate()
    stock   = stock_fetch.get_top_movers()
    housing = housing_fetch.get_city_values()

    for label, result in [("fx", fx), ("rate", rate), ("stock", stock), ("housing", housing)]:
        if result.get("error"):
            print(f"  [{label}] WARNING: {result['error']}")

    payload = formatter.build_message(stock, rate, fx, housing)
    discord_notify.send(payload)

    print(f"[{datetime.now(timezone.utc).isoformat()}] Morning Brief sent successfully.")


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"FATAL: {e}", file=sys.stderr)
        sys.exit(1)
