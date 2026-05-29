# Morning Brief — Daily Financial Digest Bot

## Overview

**Morning Brief** is a scheduled Python bot that aggregates financial and real estate data from free public APIs and delivers a formatted daily digest to a Discord channel every morning, one hour before the US stock market opens (8:30 AM ET / 5:30 AM PT).

### What it delivers

| # | Data Point | Source |
|---|-----------|--------|
| 1 | Top 10 stock market movers (gainers & losers) from previous trading day | Alpha Vantage (free) |
| 2 | Current 15-year fixed mortgage rate (800+ credit score benchmark) | FRED API (free) |
| 3 | USD → INR exchange rate for the day | Frankfurter API (free, no key) |
| 4 | Median home values for 7 Seattle-area cities | Zillow ZHVI CSV (free) |

**Delivery channel:** Discord (via webhook — no app approval, no workspace, no cost)  
**Schedule:** 8:30 AM ET daily (Mon–Fri), via GitHub Actions (free tier)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      GitHub Actions (cron)                      │
│              Schedule: 12:30 UTC Mon–Fri (8:30 AM ET)           │
└────────────────────────────┬────────────────────────────────────┘
                             │ triggers
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        main.py (orchestrator)                   │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ stock_fetch  │  │  rate_fetch  │  │  fx_fetch    │          │
│  │  .py         │  │  .py         │  │  .py         │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│  ┌──────▼─────────────────▼─────────────────▼───────┐          │
│  │               housing_fetch.py                    │          │
│  └──────────────────────┬────────────────────────────┘          │
│                         │                                       │
│  ┌──────────────────────▼────────────────────────────┐          │
│  │               formatter.py                        │          │
│  │  (builds Discord embed / message string)          │          │
│  └──────────────────────┬────────────────────────────┘          │
│                         │                                       │
│  ┌──────────────────────▼────────────────────────────┐          │
│  │               discord_notify.py                   │          │
│  │  (HTTP POST to Discord webhook URL)               │          │
│  └───────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Sources & APIs (All Free)

### 1. Stock Market — Top Movers
**Source:** Alpha Vantage — `TOP_GAINERS_LOSERS` endpoint  
**API Key:** Required — free registration at alphavantage.co (25 calls/day free tier, we use 1/day)  
**Endpoint:**
```
GET https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={KEY}
```
**Returns:** Top 20 gainers, top 20 losers, most actively traded — we surface top 5 each  
**Notes:**
- Data reflects the most recent completed trading day
- No cost, no credit card required
- Free tier: 25 requests/day, 500/month — well within limits

---

### 2. 15-Year Mortgage Rate
**Source:** FRED (Federal Reserve Economic Data) — St. Louis Fed  
**API Key:** Required — free registration at fred.stlouisfed.org  
**Series ID:** `MORTGAGE15US` — 15-Year Fixed Rate Mortgage Average  
**Endpoint:**
```
GET https://api.stlouisfed.org/fred/series/observations
    ?series_id=MORTGAGE15US
    &api_key={KEY}
    &sort_order=desc
    &limit=1
    &file_type=json
```
**Returns:** Most recent weekly average rate (%)  
**Notes:**
- FRED data is weekly (Thursday release); we display the latest available value
- The rate shown is the national average — appropriate for 800+ credit score benchmark
- The 800+ credit score borrower typically gets the best available rate, which tracks closely with or slightly below this published average
- We will note this context in the message

---

### 3. USD → INR Exchange Rate
**Source:** Frankfurter API (European Central Bank data)  
**API Key:** None required  
**Endpoint:**
```
GET https://api.frankfurter.app/latest?from=USD&to=INR
```
**Returns:** Live (ECB business day) USD/INR rate  
**Notes:**
- ECB rates update ~16:00 CET each business day
- Completely free, no registration, no rate limits for personal use
- Fallback: ExchangeRate-API free tier (1,500 requests/month)

---

### 4. Median Home Values — Seattle Metro Cities
**Source:** Zillow Home Value Index (ZHVI) — All Homes, Middle Tier  
**API Key:** None required — publicly downloadable CSV  
**URL:**
```
https://files.zillowstatic.com/research/public_v2/zhvi/City_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv
```
**Target cities:**
- Seattle, WA
- Lynnwood, WA
- Shoreline, WA
- Everett, WA
- Kent, WA
- Bellevue, WA
- Redmond, WA

**Notes:**
- ZHVI is updated monthly (released ~mid-month for the prior month)
- CSV is ~5MB; we download, filter to WA cities, and extract latest value
- Values represent the typical middle-tier home value (33rd–67th percentile)
- This is the most reliable free source for city-level home values in the US
- Fallback: Redfin Data Center CSV (`https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_covid19/weekly_housing_market_data.tsv000`)

---

## Technical Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Language | Python 3.11 | Simple, excellent library ecosystem for HTTP/data |
| HTTP client | `requests` | Standard, no async needed for sequential fetches |
| Data processing | `pandas` | Needed for Zillow CSV filtering |
| Scheduling | GitHub Actions (cron) | Free, no server required, version-controlled |
| Delivery | Discord Webhook | No app approval, free, instant setup |
| Secrets management | GitHub Actions Secrets | Free, encrypted, works natively with Actions |
| Config | `.env` (local) / GitHub Secrets (prod) | `python-dotenv` for local dev |

**Python dependencies (`requirements.txt`):**
```
requests==2.31.0
pandas==2.1.4
python-dotenv==1.0.0
```

No heavyweight libraries. No databases. No servers.

---

## Project File Structure

```
morning-brief/
├── .github/
│   └── workflows/
│       └── daily_brief.yml       # GitHub Actions schedule
├── src/
│   ├── __init__.py
│   ├── main.py                   # Orchestrator — calls all fetchers, triggers send
│   ├── stock_fetch.py            # Alpha Vantage top movers
│   ├── rate_fetch.py             # FRED 15-year mortgage rate
│   ├── fx_fetch.py               # Frankfurter USD/INR
│   ├── housing_fetch.py          # Zillow ZHVI CSV for WA cities
│   ├── formatter.py              # Builds Discord message payload
│   └── discord_notify.py        # HTTP POST to Discord webhook
├── tests/
│   ├── test_stock_fetch.py
│   ├── test_rate_fetch.py
│   ├── test_fx_fetch.py
│   └── test_housing_fetch.py
├── .env.example                  # Template for local development
├── requirements.txt
├── DESIGN.md                     # This document
└── README.md                     # Setup and run instructions
```

---

## Module Specifications

### `main.py` — Orchestrator
```python
# Pseudocode
def run():
    stock_data   = stock_fetch.get_top_movers()       # returns dict
    mortgage_rate = rate_fetch.get_15yr_rate()         # returns float
    fx_rate      = fx_fetch.get_usd_inr()             # returns float
    housing_data = housing_fetch.get_city_values()    # returns dict[city -> value]

    message = formatter.build_message(
        stock_data, mortgage_rate, fx_rate, housing_data
    )
    discord_notify.send(message)
```
- Sequential execution (no async needed — total runtime ~5–10s)
- Each fetcher returns a typed dict or raises a descriptive exception
- If any fetcher fails, it returns a fallback value with an error flag; the message still sends but notes the failed section

---

### `stock_fetch.py`
```python
# Returns:
{
    "top_gainers": [
        {"ticker": "XYZ", "price": "123.45", "change_pct": "+8.21%"},
        ...  # top 5
    ],
    "top_losers": [
        {"ticker": "ABC", "price": "45.12", "change_pct": "-6.44%"},
        ...  # top 5
    ],
    "as_of_date": "2026-05-27"
}
```

---

### `rate_fetch.py`
```python
# Returns:
{
    "rate_pct": 6.78,
    "as_of_date": "2026-05-22",   # FRED weekly release date
    "note": "National avg, 800+ score borrowers typically at or below this rate"
}
```

---

### `fx_fetch.py`
```python
# Returns:
{
    "usd_to_inr": 83.47,
    "as_of_date": "2026-05-27"
}
```

---

### `housing_fetch.py`
```python
# Returns:
{
    "Seattle":   985000,
    "Lynnwood":  612000,
    "Shoreline": 789000,
    "Everett":   521000,
    "Kent":      587000,
    "Bellevue":  1325000,
    "Redmond":   1102000,
    "as_of_month": "2026-04"   # ZHVI is monthly
}
```

---

### `formatter.py` — Discord Message Shape

The message is sent as a **Discord Embed** (rich card format):

```
┌─────────────────────────────────────────────┐
│  📊  Morning Brief — May 28, 2026           │
│  Delivered at 8:30 AM ET · 1hr before open  │
├─────────────────────────────────────────────┤
│  📈 TOP GAINERS (prev. day)                 │
│  NVDA  +8.21%  $892.10                      │
│  META  +5.33%  $521.40                      │
│  TSLA  +4.88%  $178.55                      │
│  AMD   +4.12%  $145.22                      │
│  PLTR  +3.90%  $22.44                       │
├─────────────────────────────────────────────┤
│  📉 TOP LOSERS (prev. day)                  │
│  INTC  -6.44%  $21.10                       │
│  PFE   -4.22%  $26.88                       │
│  ...                                        │
├─────────────────────────────────────────────┤
│  🏠 15-YR MORTGAGE RATE                     │
│  6.78%  (as of May 22 · 800+ score tier)    │
├─────────────────────────────────────────────┤
│  💱 USD → INR                               │
│  1 USD = ₹83.47  (ECB rate, May 28)         │
├─────────────────────────────────────────────┤
│  🏡 SEATTLE METRO MEDIAN HOME VALUES        │
│  Bellevue    $1,325,000                     │
│  Redmond     $1,102,000                     │
│  Seattle       $985,000                     │
│  Shoreline     $789,000                     │
│  Kent          $587,000                     │
│  Lynnwood      $612,000                     │
│  Everett       $521,000                     │
│  (Zillow ZHVI · April 2026)                 │
└─────────────────────────────────────────────┘
```

---

### `discord_notify.py`
```python
# Sends HTTP POST to DISCORD_WEBHOOK_URL with JSON payload
# Uses requests.post() — no Discord SDK needed
# Payload uses Discord Embeds API for formatted cards
# Raises on non-2xx response so GitHub Actions marks the run as failed
```

---

## GitHub Actions Workflow

**File:** `.github/workflows/daily_brief.yml`

```yaml
name: Morning Brief

on:
  schedule:
    # 12:30 UTC = 8:30 AM ET (EDT, UTC-4) = 5:30 AM PT
    # During EST (winter, UTC-5): runs at 7:30 AM ET — adjust to 13:30 UTC Nov–Mar
    - cron: '30 12 * * 1-5'   # Mon–Fri only (no weekend market)
  workflow_dispatch:            # allow manual trigger for testing

jobs:
  send-brief:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run Morning Brief
        env:
          ALPHA_VANTAGE_KEY:  ${{ secrets.ALPHA_VANTAGE_KEY }}
          FRED_API_KEY:       ${{ secrets.FRED_API_KEY }}
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
        run: python src/main.py
```

**GitHub Secrets to configure (repo Settings → Secrets → Actions):**

| Secret Name | Where to get it |
|-------------|----------------|
| `ALPHA_VANTAGE_KEY` | alphavantage.co → free registration |
| `FRED_API_KEY` | fred.stlouisfed.org → free registration |
| `DISCORD_WEBHOOK_URL` | Discord channel → Edit → Integrations → Webhooks |

---

## Local Development Setup

```bash
git clone https://github.com/pateltales/morning-brief
cd morning-brief
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy and fill in your keys
cp .env.example .env
# Edit .env with your API keys

# Run manually
python src/main.py
```

`.env.example`:
```
ALPHA_VANTAGE_KEY=your_key_here
FRED_API_KEY=your_key_here
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

---

## Error Handling Strategy

| Failure | Behavior |
|---------|----------|
| Alpha Vantage API down / rate limited | Send message with "⚠️ Stock data unavailable" in that section |
| FRED API down | Show last known rate with staleness note |
| Frankfurter API down | Retry once with ExchangeRate-API fallback |
| Zillow CSV fetch fails | Show last cached value (housing data is monthly anyway) |
| Discord webhook fails | Raise exception → GitHub Actions marks run as ❌ failed → email notification |

Each fetcher wraps its logic in try/except and returns a standardized result dict with an `"error"` key when something goes wrong. The formatter checks for errors and degrades gracefully instead of crashing the whole run.

---

## Timing Notes

| Time Zone | Send time |
|-----------|-----------|
| ET (EDT, summer) | 8:30 AM |
| ET (EST, winter) | 8:30 AM |
| PT (PDT, summer) | 5:30 AM |
| PT (PST, winter) | 5:30 AM |

The GitHub Actions cron is set in UTC. Because ET switches between UTC-4 (EDT) and UTC-5 (EST), two cron entries handle the DST shift:

```yaml
- cron: '30 12 * * 1-5'   # EDT (Mar–Nov): 12:30 UTC = 8:30 AM ET
- cron: '30 13 * * 1-5'   # EST (Nov–Mar): 13:30 UTC = 8:30 AM ET
```

GitHub Actions scheduler does not auto-adjust for DST — this dual-entry approach keeps delivery consistent year-round. Alternatively, a single `30 12 * * 1-5` entry (off by 1 hour in winter) is acceptable if exact timing is not critical.

---

## Free API Limits Summary

| API | Free Limit | Our Usage | Headroom |
|-----|-----------|-----------|---------|
| Alpha Vantage | 25 req/day, 500/month | 1 req/day, ~22/month | Ample |
| FRED | Unlimited (fair use) | 1 req/day | No concern |
| Frankfurter | Unlimited | 1 req/day | No concern |
| Zillow ZHVI CSV | Public download, no auth | 1 download/day | No concern |
| Discord Webhook | 50 req/sec per webhook | 1 req/day | No concern |
| GitHub Actions | 2,000 min/month (free) | ~2 min/run × 22 days = 44 min | Ample |

**Total cost: $0.00/month**

---

## Implementation Phases

### Phase 1 — Core Data (Week 1)
- [ ] Set up repo structure and GitHub Actions skeleton
- [ ] Implement `fx_fetch.py` (simplest — no auth, instant test)
- [ ] Implement `rate_fetch.py` (FRED API)
- [ ] Implement `discord_notify.py` with a test message
- [ ] Wire up `main.py` and `.env` loading

### Phase 2 — Stock & Formatter (Week 2)
- [ ] Implement `stock_fetch.py` (Alpha Vantage)
- [ ] Implement `formatter.py` (Discord embed builder)
- [ ] End-to-end test with manual `workflow_dispatch`

### Phase 3 — Housing & Polish (Week 3)
- [ ] Implement `housing_fetch.py` (Zillow CSV)
- [ ] Add error handling and fallbacks to all fetchers
- [ ] Add DST-aware dual cron schedule
- [ ] Write tests for each module
- [ ] Final end-to-end test

### Phase 4 — Hardening (Ongoing)
- [ ] Monitor first 2 weeks of live runs via GitHub Actions logs
- [ ] Add GitHub Actions failure → email alert (built-in via repo notification settings)
- [ ] Tune Discord embed formatting based on readability

---

## Limitations & Caveats

1. **Zillow ZHVI is monthly, not daily** — house values update once per month. The message will clearly show the data month (e.g., "April 2026 data"). This is the best granularity available for free.

2. **FRED mortgage rate is weekly** — released each Thursday. On other days the message shows the most recent Thursday's rate, labeled with its date.

3. **Stock data is previous-day close** — Alpha Vantage's free `TOP_GAINERS_LOSERS` reflects the most recently completed trading day. The message is clearly labeled "previous close."

4. **Frankfurter uses ECB rates** — these are mid-market rates, not bank transfer rates. Actual transfer rates will vary by provider.

5. **GitHub Actions cron is not guaranteed** — GitHub's documentation notes that scheduled workflows may be delayed by up to a few minutes under heavy load. This is acceptable for a morning digest.

6. **No weekend runs** — cron is set for Mon–Fri only. Markets are closed on weekends; housing and FX data would be stale.
