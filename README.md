# momentum-strategy-lab

Personal lab for testing the **"buy past winners, sell past losers"** momentum strategy (Jegadeesh & Titman, 1993) on a mixed European/US portfolio.

> **This repo tracks a live IBKR DEMO (paper trading) account.** All trades, positions, and history are real-time records of how the strategy performs on simulated capital. No real money is invested. The goal is to test the strategy with full transparency over multiple quarters before considering any real-money implementation.

**This is a personal experiment, not financial advice. Past performance does not guarantee future results.**

---

## What this is

A backtested implementation of the classic **momentum 12-1** strategy applied quarterly to a mixed portfolio of:
- **4 stocks from the S&P 500** (65% of capital)
- **2 stocks from the IBEX 35** (30% of capital)
- **5% of cash reserve** left for flexibility and commissions

Selection of stocks happens dynamically each quarter based on their 12-month price momentum (excluding the most recent month, a common technique to avoid short-term reversal noise). **Every quarter the script scans the entire universe** — all 35 IBEX components plus the top ~100 S&P 500 stocks by market cap — and picks the 6 stocks with the strongest momentum signal at that exact moment. No static "favorites list" is used.

## Strategy summary

| Parameter | Value |
|---|---|
| Strategy type | Long-only momentum |
| Lookback period | 12 months, skipping the last 1 (i.e. "12-1") |
| Rebalancing frequency | Quarterly (every 3 months) |
| Number of positions | 6 (4 US + 2 ES) |
| Position weights | Fixed 65% US / 30% ES (equal-weighted within each region) |
| Stock universe | IBEX 35 (35 stocks) + S&P 500 top ~100 by market cap |
| Selection | Dynamic each quarter, no static pre-selection |
| Initial capital | Configurable via `initial_capital_eur` in `data/portfolio.json` |
| Fractional shares | Enabled by default (essential for small capital with expensive stocks) |
| Commissions | Recorded manually per-trade in `data/history.json` (IBKR varies by tier/volume) |
| Tax framework | Spanish IRPF (Base del Ahorro), W-8BEN active for US dividends |
| Accounting currency | EUR |

## Historical backtest results (2019-2025)

These results assume the strategy was followed without intervention for 7 full years:

| Metric | Value |
|---|---|
| Capital initial | 2,000 € |
| Capital final | 20,112 € |
| Total return | +905.60% |
| CAGR (net of taxes) | **+39.06%** |
| Annualized volatility | 19.84% |
| Sharpe ratio (rf=0) | **1.78** |
| Max drawdown | **-17.24%** |
| Total taxes paid | 4,182 € |

**Note**: the backtest excludes commissions (they vary by IBKR tier/volume/account size and can't be modeled accurately upfront). In real execution you record actual commissions per trade in `data/history.json`. Expect commissions to subtract roughly 0.1-0.3% per year of CAGR.

For comparison, the S&P 500 buy-and-hold over the same period returned ~14% CAGR. The strategy outperforms thanks to the dynamic rotation, but with concentration risk.

See [docs/backtest-results.md](docs/backtest-results.md) for full year-by-year breakdown.

## Why this works (in theory)

Momentum is one of the most replicated anomalies in finance. Studies show that stocks with strong recent price performance tend to continue outperforming for 3-12 months. The reasons cited in the literature include:

- **Behavioral biases**: investors anchor to past prices and react slowly to news
- **Risk premium**: momentum captures a compensation for tail risk
- **Institutional inertia**: large funds rebalance slowly, creating persistent trends

The "skip the last month" detail removes the short-term reversal effect that dominates 1-month returns.

## Why this might NOT work going forward

- **Past data is just that**: 2019-2025 was a regime with strong tech tailwinds in the US
- **Momentum crashes**: when markets reverse sharply (e.g. early 2009, late 2020), momentum portfolios can lose 30-50% in months
- **Tax drag**: Spanish IRPF on each realized gain reduces compounding significantly
- **Survivorship bias**: the universe used here only includes stocks that survived to 2025

Read [docs/disclaimer.md](docs/disclaimer.md) before considering applying this with real money.

## Getting started

### Requirements

- Python 3.10+
- An IBKR account (for live execution) — optional, only needed if you actually want to trade
- Tax residency where capital gains rules are understood (this repo assumes Spanish IRPF)

### Installation

```bash
git clone https://github.com/<yourusername>/momentum-strategy-lab.git
cd momentum-strategy-lab
pip install -r requirements.txt
```

### Running the live rebalance script

The rebalance script tells you what to buy and sell each quarter:

```bash
python src/rebalance.py
```

The script will:
1. Download recent monthly prices for the IBEX 35 and S&P 500 universes
2. Calculate momentum 12-1 for each stock
3. Select top 4 from S&P 500 (with weight 65%) and top 2 from IBEX (with weight 30%)
4. Compare with the current portfolio state in `data/portfolio.json`
5. Print buy/sell orders to execute in IBKR
6. Save a record of the decision in `data/history.json`

After executing the trades in your IBKR DEMO account, manually update `data/portfolio.json` with the resulting positions and commit the change.

### Setting the initial capital

Before the very first run, open `data/portfolio.json` and edit the `initial_capital_eur` field to whatever amount you want to commit to the strategy. The default is 2,000 EUR.

```json
{
  "initial_capital_eur": 5000.0,
  "cash_eur": 0,
  "positions": {}
}
```

When `cash_eur` is 0 and `positions` is empty (i.e. on the first run), the script reads `initial_capital_eur` and uses it to initialize `cash_eur`. After that, the script tracks state via `cash_eur` and `positions`.

### Recording avg_price_eur for US (S&P 500) positions

For Spanish stocks, the trade is already in EUR, so `avg_price_eur` is just the fill price.

For US stocks, the fill price is in USD, and you need to convert it using the EUR/USD exchange rate **at the moment of the trade** (IBKR shows this rate on each trade confirmation).

**Example:** you bought 5 shares of NVDA at 100 USD each. On that day, 1 EUR = 1.1743 USD.

```
avg_price_eur = avg_price_usd / eur_usd_rate
              = 100 / 1.1743
              = 85.16 EUR per share
```

Total cost in EUR: 5 shares × 85.16 EUR = 425.79 EUR.

This `avg_price_eur` is the cost basis used to calculate P&L in EUR for tax purposes. Once recorded, it doesn't change — even if EUR/USD moves later, the cost basis stays fixed at what you actually paid.

### Adding extra capital later

If at some point you want to add more capital (e.g., 1,000 EUR after a year), the cleanest way is:

1. **Add the EUR to your IBKR account** as you normally would (wire transfer, etc.)
2. **Wait for the next quarterly rebalance date** (don't add mid-quarter — it breaks weight balance)
3. **Before running the script**, edit `data/portfolio.json` to add the extra cash:

```json
{
  "initial_capital_eur": 2000.0,        // leave as historical record
  "cash_eur": 1245.30,                  // increase by 1000 EUR -> 2245.30
  "positions": { ... unchanged ... },
  "last_rebalance": "2027-04-07"
}
```

4. **Run `python src/rebalance.py`**. The script will use the new total value (existing positions + increased cash) to compute target weights, and will rebalance positions to match.
5. **Optionally**, add a note to history.json documenting the capital injection for transparency.

The `initial_capital_eur` field is kept as a historical reference for total return calculations. To track CAGR correctly when adding capital over time, consider computing **time-weighted returns** externally — the simple `final_value / initial_capital - 1` formula no longer reflects strategy performance once you add money mid-stream.

### Forking for real money

If you want to fork this repo and connect it to a real (non-demo) IBKR account, add `data/portfolio.json` to `.gitignore` first to keep your positions private. See `.gitignore` for the line to uncomment.

### Running the historical backtest

```bash
python src/backtest.py
```

This reproduces the 2019-2025 simulation with synthetic price data calibrated to known historical annual returns.

## Repository structure

```
momentum-strategy-lab/
├── README.md                    # This file
├── LICENSE                      # MIT
├── .gitignore                   # See note: portfolio.json is public for DEMO account
├── requirements.txt             # Python dependencies
├── docs/
│   ├── methodology.md           # Detailed strategy explanation
│   ├── backtest-results.md      # Year-by-year historical performance
│   └── disclaimer.md            # Legal disclaimer
├── src/
│   ├── rebalance.py             # Quarterly rebalance script (production)
│   ├── backtest.py              # Historical backtest 2019-2025
│   └── universe.py              # Universe definitions (IBEX 35 + S&P 500)
├── data/
│   ├── portfolio.example.json   # Field documentation reference
│   ├── portfolio.json           # Live state of the DEMO account
│   └── history.json             # Append-only rebalance history
└── tests/
    └── test_momentum.py         # Unit tests
```

## Operational calendar

Rebalances should happen between the 5th and 10th of:
- January (Q1)
- April (Q2)
- July (Q3)
- October (Q4)

Tuesdays and Wednesdays are recommended for best liquidity.

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

This is a personal research project. **Nothing in this repository is investment advice.** The author is not a financial advisor. Past simulated performance does not guarantee future results. Trading involves risk of capital loss. See [docs/disclaimer.md](docs/disclaimer.md) for full disclaimer.

## References

- Jegadeesh, N., & Titman, S. (1993). *Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency.* Journal of Finance, 48(1), 65-91.
- Asness, C. S., Moskowitz, T. J., & Pedersen, L. H. (2013). *Value and Momentum Everywhere.* Journal of Finance, 68(3), 929-985.
- Fama, E. F., & French, K. R. (2012). *Size, value, and momentum in international stock returns.* Journal of Financial Economics, 105(3), 457-472.
