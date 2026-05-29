from datetime import date


EMBED_COLOR = 3447003  # Discord blue


def _gainers_losers_field(label: str, entries: list) -> str:
    if not entries:
        return "⚠️ Data unavailable"
    lines = []
    for e in entries:
        lines.append(f"`{e['ticker']:<6}` {e['change_pct']:>8}   ${e['price']}")
    return "\n".join(lines)


def _housing_field(housing: dict) -> str:
    cities = ["Bellevue", "Redmond", "Seattle", "Shoreline", "Lynnwood", "Kent", "Everett"]
    lines = []
    for city in cities:
        val = housing.get(city)
        if val:
            lines.append(f"`{city:<10}` ${val:,.0f}")
        else:
            lines.append(f"`{city:<10}` —")
    month = housing.get("as_of_month")
    if month:
        lines.append(f"\n*Zillow ZHVI · {month}*")
    return "\n".join(lines)


def build_message(stock: dict, rate: dict, fx: dict, housing: dict) -> dict:
    today = date.today().strftime("%B %-d, %Y")
    fields = []

    # Stock movers
    if stock.get("error"):
        fields.append({"name": "📈 Top Gainers (prev. close)", "value": "⚠️ Data unavailable", "inline": False})
        fields.append({"name": "📉 Top Losers (prev. close)",  "value": "⚠️ Data unavailable", "inline": False})
    else:
        as_of = stock.get("as_of_date") or "prev. close"
        fields.append({
            "name": f"📈 Top Gainers ({as_of})",
            "value": _gainers_losers_field("gainers", stock.get("top_gainers", [])),
            "inline": False,
        })
        fields.append({
            "name": f"📉 Top Losers ({as_of})",
            "value": _gainers_losers_field("losers", stock.get("top_losers", [])),
            "inline": False,
        })

    # Mortgage rate
    if rate.get("error") or rate.get("rate_pct") is None:
        rate_value = "⚠️ Data unavailable"
    else:
        rate_value = f"**{rate['rate_pct']}%**  *(as of {rate['as_of_date']} · 800+ score benchmark)*"
    fields.append({"name": "🏠 15-Year Mortgage Rate", "value": rate_value, "inline": True})

    # USD → INR
    if fx.get("error") or fx.get("usd_to_inr") is None:
        fx_value = "⚠️ Data unavailable"
    else:
        fx_value = f"**1 USD = ₹{fx['usd_to_inr']:,.2f}**  *(ECB · {fx['as_of_date']})*"
    fields.append({"name": "💱 USD → INR", "value": fx_value, "inline": True})

    # Housing
    fields.append({
        "name": "🏡 Seattle Metro Median Home Values",
        "value": _housing_field(housing),
        "inline": False,
    })

    return {
        "embeds": [{
            "title": f"📊 Morning Brief — {today}",
            "description": "Delivered 1 hour before market open  •  All data from free public sources",
            "color": EMBED_COLOR,
            "fields": fields,
            "footer": {"text": "Alpha Vantage · FRED (St. Louis Fed) · Frankfurter (ECB) · Zillow ZHVI"},
        }]
    }
