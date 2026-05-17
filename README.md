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
| CAGR (net of taxes) | **+41.69%** |
| Annualized volatility | 24.38% |
| Sharpe ratio (rf=0) | **1.57** |
| Max drawdown | **-22.80%** |
| Total taxes paid | 4,182 € |

**Note**: the backtest excludes commissions (they vary by IBKR tier/volume/account size and can't be modeled accurately upfront). In real execution you record actual commissions per trade in `data/history.json`. Expect commissions to subtract roughly 0.1-0.3% per year of CAGR.

For comparison, the S&P 500 buy-and-hold over the same period returned ~14% CAGR. The strategy outperforms thanks to the dynamic rotation, but with concentration risk.

See [backtests/backtest-results.md](backtests/backtest-results.md) for full year-by-year breakdown and per-quarter trade detail. See [backtests/backtest-dashboard.png](backtests/backtest-dashboard.png)
for the executive summary image.

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
- **Currency risk is now in the backtest** (issue #6). EUR/USD moved from 1.15 in 2019 to parity in 2022 and back to 1.15 in 2025. The backtest uses the real historical rate of each rebalance day. Going forward, EUR/USD movements will continue to add noise to results — both positively and negatively.

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

### Adding or withdrawing capital later

Once the strategy is running, you may want to add new capital (e.g., yearly top-ups from savings) or withdraw some (e.g., to cover an expense). The strategy uses a `net_capital_contributed_eur` field in `portfolio.json` to track the cumulative net amount you've put in — this is essential for calculating real return on capital.

**Golden rule for both operations**: always wait for the next quarterly rebalance window (day 5-10 of Jan/Apr/Jul/Oct). Don't add or withdraw mid-quarter — it breaks the weight balance and triggers unnecessary rebalancing complexity.

#### Adding capital (example: +1,000 EUR after one year)

Imagine your portfolio file looks like this right before the new injection:

```json
{
  "initial_capital_eur": 2000.0,
  "net_capital_contributed_eur": 2000.0,
  "cash_eur": 45.20,
  "positions": { ... your 6 positions ... },
  "last_rebalance": "2027-01-08"
}
```

**Step 1:** Transfer 1,000 EUR to your IBKR account (wire/SEPA). Plan ahead — transfers take 1-2 business days.

**Step 2:** On the next rebalance day, BEFORE running the script, edit `data/portfolio.json`:

```json
{
  "initial_capital_eur": 2000.0,
  "net_capital_contributed_eur": 3000.0,
  "cash_eur": 1045.20,
  "positions": { ... same positions, unchanged ... },
  "last_rebalance": "2027-01-08"
}
```

Changes made:
- `cash_eur`: added 1,000 EUR (45.20 → 1,045.20)
- `net_capital_contributed_eur`: increased by 1,000 EUR (2,000 → 3,000)
- `initial_capital_eur`: unchanged (historical reference)

**Step 3:** Run `python src/rebalance.py`. The script sees a larger total portfolio and will issue BUY orders to bring positions up to the new equal-weight targets, using the extra cash.

**Step 4:** Append an entry to `data/history.json` documenting the injection:

```json
{
  "date": "2027-04-06",
  "event": "CAPITAL_INJECTION",
  "amount_eur": 1000.0,
  "new_net_contributed_eur": 3000.0,
  "reason": "Yearly top-up from savings"
}
```

#### Withdrawing capital (example: -500 EUR after two years)

Withdrawals are slightly trickier because you need to free up cash before transferring out. The cleanest approach:

**Step 1:** Wait for the rebalance day.

**Step 2:** Run `python src/rebalance.py` FIRST (don't withdraw yet). The script tells you which positions to sell (the ones no longer in the top 6 by momentum).

**Step 3:** Execute the sells in IBKR. After the sells, your `cash_eur` will be higher than usual because of the sale proceeds.

**Step 4:** Check if you have enough cash to cover the 500 EUR withdrawal AFTER the script's planned buys:

- **If YES (typical case):** Reduce the script's BUYS proportionally to keep 500 EUR aside. For example, if the script wants you to buy 800 EUR of NVDA and 800 EUR of MSFT, buy 550 EUR and 550 EUR instead — keeping 500 EUR for the withdrawal. The strategy is now slightly underinvested for that quarter, but it self-corrects next time.

- **If NO (rare):** You need to sell more than the script suggested. Sell extra shares of the position with the LOWEST current momentum 12-1 (the script's ranking output shows this). This is the position closest to being dropped anyway.

**Step 5:** Once the 500 EUR is in cash, transfer it out of IBKR.

**Step 6:** Update `portfolio.json`:

```json
{
  "initial_capital_eur": 2000.0,
  "net_capital_contributed_eur": 2500.0,
  "cash_eur": 32.15,
  "positions": { ... updated post-rebalance positions ... },
  "last_rebalance": "2028-01-07"
}
```

Changes:
- `cash_eur`: reflects real balance after sells, buys, and withdrawal
- `net_capital_contributed_eur`: decreased by 500 EUR (3,000 → 2,500)
- `positions`: reflects whatever you actually hold after the rebalance

**Step 7:** Append to `data/history.json`:

```json
{
  "date": "2028-01-07",
  "event": "CAPITAL_WITHDRAWAL",
  "amount_eur": -500.0,
  "new_net_contributed_eur": 2500.0,
  "reason": "Personal expense"
}
```

#### Calculating real return after capital changes

Once you've added or withdrawn capital, the simple formula `final_value / initial_capital_eur - 1` is meaningless — it mixes investment returns with new money flows.

**Use this instead:**

```
Return on net contributions = (current_portfolio_value - net_capital_contributed_eur)
                              / net_capital_contributed_eur
```

**Example:** if your portfolio is worth 5,800 EUR after injecting and later withdrawing for a net of 2,500 EUR contributed, your real return is (5,800 - 2,500) / 2,500 = **132%**, NOT (5,800 - 2,000) / 2,000 = 190%.

For a fully accurate CAGR with multiple cash flows (the technically correct metric is "money-weighted return"), use Excel's `XIRR` function or Python's `pyxirr` library. Feed it the list of all cash flows (initial 2,000, +1,000 after 1 year, -500 after 2 years, current value as final positive flow) with their respective dates.

### Forking for real money

If you want to fork this repo and connect it to a real (non-demo) IBKR account, add `data/portfolio.json` to `.gitignore` first to keep your positions private. See `.gitignore` for the line to uncomment.

### Running the historical backtest

```bash
# Run the simulation (writes JSON/CSV outputs to backtests/)
python src/backtest.py

# Generate the human-readable .md report
python scripts/build_backtest_report.py

# Generate the executive dashboard image (.png)
python scripts/build_backtest_dashboard.py
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
│   └── disclaimer.md            # Legal disclaimer
├── src/
│   ├── rebalance.py             # Quarterly rebalance script (production)
│   ├── backtest.py              # Historical backtest 2019-2025
│   └── universe.py              # Universe definitions (IBEX 35 + US Large Cap)
├── scripts/
│   ├── build_backtest_dashboard.py   # Generates the executive dashboard image
│   ├── build_backtest_report.py      # Generates backtest-results.md
│   └── commit-rebalance.ps1          # PowerShell script for quarterly commits
├── data/
│   ├── portfolio.example.json   # Field documentation reference
│   ├── portfolio.json           # Live state of the DEMO account
│   ├── history.json             # Append-only rebalance history
│   └── eurusd_rates.csv         # Historical EUR/USD daily rates
├── backtests/                   # All backtest outputs (re-generable)
│   ├── backtest-portfolio.json  # Final portfolio state (same schema as data/portfolio.json)
│   ├── backtest-history.json    # Rebalance log (same schema as data/history.json)
│   ├── backtest-trades.csv      # One row per buy/sell trade
│   ├── backtest-metrics.json    # Numeric summary
│   ├── backtest-results.md      # Human-readable report (auto-generated)
│   └── backtest-dashboard.png   # Executive dashboard image (auto-generated)
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
