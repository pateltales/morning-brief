# Morning Brief

Daily financial digest delivered to Discord every morning at 8:30 AM ET — one hour before the US stock market opens.

See [DESIGN.md](DESIGN.md) for the full system design, architecture, API choices, and implementation plan.

## What you get every morning

- Top 5 stock gainers and losers from the previous trading day
- Current 15-year fixed mortgage rate (national average, 800+ credit score benchmark)
- USD → INR exchange rate
- Median home values for Seattle, Lynnwood, Shoreline, Everett, Kent, Bellevue, and Redmond

## Stack

Python · GitHub Actions (free) · Discord Webhook · Alpha Vantage · FRED API · Frankfurter API · Zillow ZHVI

**Total infrastructure cost: $0/month**
