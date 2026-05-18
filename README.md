# momentum-strategy-lab

Personal lab for testing the **"buy past winners, sell past losers"** momentum strategy (Jegadeesh & Titman, 1993) on a mixed European/US portfolio.

> **This repo tracks a live IBKR DEMO (paper trading) account.** All trades, positions, and history are real-time records of how the strategy performs on simulated capital. No real money is invested. The goal is to test the strategy with full transparency over multiple quarters before considering any real-money implementation.

**This is a personal experiment, not financial advice. Past performance does not guarantee future results.**

---

## What this is

A backtested implementation of the classic **momentum 12-1** strategy applied quarterly to a mixed portfolio of:
- **4 stocks from the US universe** (65% of capital)
- **2 stocks from the IBEX 35** (30% of capital)
- **5% of cash reserve** left for flexibility and commissions

Selection of stocks happens dynamically each quarter based on their 12-month price momentum (excluding the most recent month, a common technique to avoid short-term reversal noise). **Every quarter the script scans the entire universe** — all 35 IBEX components plus 157 US stocks across NYSE and NASDAQ — and picks the 6 stocks with the strongest momentum signal at that exact moment. No static "favorites list" is used.

## Strategy summary

| Parameter | Value |
|---|---|
| Strategy type | Long-only momentum |
| Lookback period | 12 months, skipping the last 1 (i.e. "12-1") |
| Rebalancing frequency | Quarterly (every 3 months) |
| Number of positions | 6 (4 US + 2 ES) |
| Position weights | Fixed 65% US / 30% ES (equal-weighted within each region) |
| Cash reserve | 5% (for commissions and flexibility) |
| Stock universe | IBEX 35 (35 stocks) + 157 US stocks across NYSE and NASDAQ |
| Selection | Dynamic each quarter, no static pre-selection |
| Fractional shares | Enabled (essential at small capital sizes) |

### US Universe

The US universe (~157 stocks) includes S&P 500 large caps plus:

- **Large non-S&P 500 listings** (foreign-domiciled ADRs, recent IPOs, etc.) such as Sandisk, Bloom Energy, Lumentum, Applied Optoelectronics, Cerebras, ARM, ASML, TSM, MercadoLibre, PDD, Alibaba, Novo Nordisk, AstraZeneca, NU, HOOD, Enphase.
- **Momentum mid-caps** that have shown explosive recent performance: Astera Labs, Argan, Vertiv, MP Materials, Rocket Lab, IES Holdings, Sterling Construction, Powell Industries, Modine, Marvell, Coherent, MACOM, Ciena, Western Digital, and others. One way to identify these stocks is by using https://stockanalysis.com/stocks/screener/ and adding "Change 1Y" column and then sort by it in descending order to see the stocks with the highest change in the last 12 months.

Why widen beyond the S&P 500? Many high-momentum stocks live OUTSIDE the index, especially in their early-growth phase. The S&P 500's inclusion committee imposes strict rules (profitability, market cap, US domicile) that exclude exactly the kind of stocks that often top the momentum ranking. Capturing them requires a wider net. See `src/universe.py` for the full list and rationale.

## Historical backtest results (2019-2025)

Run on **real historical daily prices** for all 192 universe stocks (157 US + 35 IBEX) from `data/monthly-historic-prices.csv`, with **real historical EUR/USD rates** from `data/eurusd.rates.csv` applied per rebalance day.

| Metric | Value |
|---|---|
| Initial capital | 2.000 € |
| Final capital | **46.916 €** |
| Total return | +2.245,78% |
| **CAGR (net of taxes)** | **+56,95%** |
| Annualized volatility | 44,41% |
| **Sharpe ratio** | **1,24** |
| **Max drawdown** | **-44,26%** |
| Total taxes (Spanish IRPF) | 10.390 € |
| Total trades | 158 |
| Rebalances | 28 |

These numbers reflect real prices — not synthetic calibrations. They are very strong but also more volatile than naive simulations suggest. The −44% max drawdown in 2022 is real and important: the strategy hurts hard during regime changes (rate-hike shocks, momentum crashes).

See [backtests/backtest-results.md](backtests/backtest-results.md) for the full year-by-year breakdown and per-trade detail, and [backtests/backtest-dashboard.png](backtests/backtest-dashboard.png) for the executive summary image.

## Why this works (in theory)

1. **Behavioral bias.** Investors react slowly to good news, so prices drift upward over weeks-months rather than jumping in one day.
2. **Institutional inertia.** Large funds need weeks-months to change positions due to regulatory and operational constraints, creating persistent trends that nimble investors can ride.
3. **Risk premium.** Momentum strategies suffer occasionally in major regime changes ("momentum crashes"), and the market pays a premium for assuming that tail risk.

See [docs/methodology.md](docs/methodology.md) for a deeper discussion.

## Why this might NOT work going forward

- **Period 2019-2025 was extraordinarily favorable** for momentum (post-COVID tech boom + AI boom). The next 7 years are unlikely to resemble it.
- **Currency risk is real.** EUR/USD moved from 1,15 in 2019 to parity in 2022 and back up. Future moves will continue to add noise both ways.
- **Survivorship bias.** The universe contains stocks that exist today; companies that delisted are absent, inflating backtest returns.
- **Commissions are not modeled** in the backtest. Real execution will subtract 0,1-0,3% annually depending on IBKR tier.
- **Crowded factor.** Momentum is well-known. The more capital chasing the same signal, the smaller the premium.

A realistic expectation for live performance is **5-15 percentage points lower CAGR** than the backtest. Even with that adjustment a CAGR of 30-40% would be exceptional. Don't bet the farm on it.

---

## Getting started

### Requirements

- Python 3.10+
- Packages in `requirements.txt`: pandas, numpy, yfinance, matplotlib
- An IBKR account (DEMO or live)

### Installation

```bash
git clone https://github.com/<your-username>/momentum-strategy-lab.git
cd momentum-strategy-lab
pip install -r requirements.txt
```

### Setting the initial capital

Before the first run, edit `data/portfolio.json` as follows:

```json
{
  "initial_capital_eur": 2000.0,
  "net_capital_contributed_eur": 2000.0,
  "inception_date": "2026-05-18",
  "cash_eur": 2000.0,
  "positions": {},
  "last_rebalance": null
}
```

- `initial_capital_eur`: historical reference, never changes
- `net_capital_contributed_eur`: starts equal to initial; later updated if you add or withdraw capital
- `inception_date`: the day you actually deposit money in IBKR (used by `src/cagr.py` to compute annualized returns)
- `cash_eur`: starts equal to initial capital. Updated automatically by `scripts/append-rebalance.py` after each rebalance.

---

## Quarterly rebalance flow

Every quarter (Jan/Apr/Jul/Oct, days 5-10) execute the following four steps. The whole thing takes about 15-30 minutes.

### Step 1 — Generate the plan

In the morning of the rebalance day:

```bash
python src/rebalance.py
```

This:
- Downloads current prices from Yahoo Finance for the full universe
- Computes the 12-1 momentum of every stock
- Selects the top 4 US + top 2 IBEX as new targets
- Compares against your current portfolio and proposes BUYs / SELLs
- **Appends a PLAN entry to `data/history.json`** with the momentum values and the proposed orders

The script does NOT execute anything in your broker. It only writes a plan that says "these are the trades I would do if I were executing now".

### Step 2 — Execute the orders in IBKR manually

Open the IBKR Web/TWS interface and manually place each order from the plan (BUY for new picks, SELL for positions that fell out of the top). Use MARKET orders during market hours for simplicity.

IBKR will give you the actual execution price, the actual EUR/USD rate it applied (visible in the "EUR.USD SLD" lines of the trade log for US orders), and the commission charged.

### Step 3 — Record the executed trades

Once all orders are filled:

```bash
python scripts/append-rebalance.py
```

This is an interactive script that asks for the native IBKR numbers of each trade (shares, price, commission, and for US trades the EUR/USD rate IBKR applied). It then:

- Computes all EUR-equivalent values automatically (no manual math)
- Backs up the JSON files (`.bak`) before overwriting
- **Appends an EXECUTION entry to `data/history.json`** with the real execution data
- Updates `data/portfolio.json` with the new positions and remaining cash
- Validates that the cash math balances (refuses to save if `cash_after != cash_before + sells − buys` within 0,50 EUR)

For testing without writing files, add `--dry-run`:

```bash
python scripts/append-rebalance.py --dry-run
```

### Step 4 — Commit and push

```powershell
.\scripts\commit-rebalance.ps1 -Quarter "2026 Q2" `
    -Sold "" `
    -Bought "SNDK,BE,LITE,AAOI,SLR,ACS" `
    -ValueBefore 2000.00 -ValueAfter 1990.56 `
    -CashRemaining 102.19 -EurUsd 1.1641
```

The `append-rebalance.py` output prints this exact command for copy-paste.

---

## history.json: two entries per rebalance

`data/history.json` records two entries per rebalance, distinguished by a top-level `type` field:

- **`"type": "PLAN"`** — written by `src/rebalance.py` in the morning. Records what the algorithm decided: selected tickers, momentum 12-1 values (as percentages under `momentum_us_top_pct` and `momentum_ibex_top_pct`), reference prices, proposed orders. The reference EUR/USD rate in this entry is what the script saw when it ran.
- **`"type": "EXECUTION"`** — written by `scripts/append-rebalance.py` after orders are filled. Records what actually happened in the market: fill prices, actual EUR/USD rates IBKR applied to each order, real commissions, realized P&L on sells.

Both entries share the same `date`. PLAN tells you "why" the strategy chose what it chose. EXECUTION tells you "what really happened" when you placed the orders. Useful months later when you want to audit a past decision.

Quick example after two quarters:

```json
[
  { "type": "PLAN",      "date": "2026-05-18", "momentum_us_top_pct": { ... }, ... },
  { "type": "EXECUTION", "date": "2026-05-18", "orders_to_buy": [ ... ],       ... },
  { "type": "PLAN",      "date": "2026-07-06", ... },
  { "type": "EXECUTION", "date": "2026-07-06", ... }
]
```

Over 10 years that's 80 entries (40 PLAN + 40 EXECUTION). Plenty of audit trail, no scaling issue.

---

## Adding or withdrawing capital later

If at some point you want to add (or withdraw) capital — for example a 1.000 EUR top-up a year after you started — follow these steps:

1. **Wait for the next rebalance day.** Don't add money mid-quarter; the strategy is designed for clean quarterly cuts.
2. **Transfer the money to IBKR before that day** (wires take 1-2 business days to clear).
3. **Before running `src/rebalance.py` that morning**, edit `data/portfolio.json`:
   - Add the new amount to `cash_eur`
   - Add the new amount to `net_capital_contributed_eur`
4. **Append a capital-flow event to `data/history.json`**:
   ```json
   {
     "type": "CAPITAL_INJECTION",
     "date": "2027-04-06",
     "amount_eur": 1000.0,
     "new_total_contributed_eur": 3000.0,
     "reason": "Yearly top-up from savings"
   }
   ```
   For withdrawals, use `"type": "CAPITAL_WITHDRAWAL"` with `amount_eur` as a positive number
(the amount withdrawn), and DECREASE `new_total_contributed_eur` by that amount.
Also decrease `cash_eur` in portfolio.json by the same amount.
5. **Run `python src/rebalance.py`** as usual. The script will see the new cash and rebalance with the updated total.

### Why this matters: real annualized return with capital flows

Once you have added or withdrawn capital, the naive formula `(current − contributed) / contributed` is no longer your real annualized return — it mixes investments held for different periods.

`src/cagr.py` computes the proper metrics:

```bash
python src/cagr.py                # uses last known portfolio value
python src/cagr.py 5800.00        # override with a specific current value, as a test
```

You get two numbers:
- **Money-weighted CAGR (XIRR)**: the annualized return your money actually experienced, accounting for when each deposit happened. Same metric professional fund managers report.
- **Time-weighted CAGR (TWR)**: pure strategy performance, independent of when you added or withdrew money. Use this to compare against benchmarks like the S&P 500.

Both numbers also appear in `rebalance.py`'s output after each quarterly rebalance.

---

## How to expand the universe

The universe is data-driven. To add a new stock:

1. **Add its daily prices** to `data/monthly-historic-prices.csv` in the existing format: `Date,Ticker,Close,Company` with dates in English month-name format (e.g. `"January 2, 2014"`).
2. **Add the ticker to `src/universe.py`** in the appropriate sector section of `US_LARGE_CAP` (or `IBEX_35` for Spanish stocks).

Both `backtest.py` and `rebalance.py` will pick it up automatically. That´s it, there is no other place to update.

The same applies for removing a stock: delete it from `universe.py`. Its prices can stay in the CSV — they will simply be ignored.

---

## Running the historical backtest

```bash
python src/backtest.py                            # runs the simulation
python scripts/build_backtest_report.py           # generates backtest-results.md
python scripts/build_backtest_dashboard.py        # generates backtest-dashboard.png
```

Outputs go to `backtests/`. Re-running these scripts at any time regenerates everything from the source data.

---

## Forking for real money

If you want to use this as a starting point for a real-money implementation, **read [docs/disclaimer.md](docs/disclaimer.md) first** and consider:

- The backtest is on past data; the future may differ substantially
- IBKR commissions and bid-ask spreads will reduce returns
- The strategy can lose 40-50% in bad years (and recover, but you need the stomach for it)
- Spanish IRPF rules change; verify yours
- Test with a DEMO account for at least 2-4 quarters before risking real capital

---

## Repository structure

```
momentum-strategy-lab/
├── README.md                    # This file
├── LICENSE                      # MIT
├── CHANGELOG.md                 # Release notes
├── .gitignore                   # See note: portfolio.json is public for DEMO account
├── requirements.txt             # Python dependencies
├── docs/
│   ├── methodology.md           # Detailed strategy explanation
│   └── disclaimer.md            # Legal disclaimer
├── src/
│   ├── rebalance.py             # Quarterly rebalance: writes PLAN entries
│   ├── backtest.py              # Historical backtest on real data 2019-2025
│   ├── universe.py              # Universe definitions (IBEX 35 + US Large Cap)
│   └── cagr.py                  # Money-weighted (XIRR) and time-weighted (TWR) returns
├── scripts/
│   ├── append-rebalance.py            # Records executed trades into JSONs
│   ├── build_backtest_dashboard.py    # Generates the executive dashboard image
│   ├── build_backtest_report.py       # Generates backtest-results.md
│   └── commit-rebalance.ps1           # PowerShell helper for quarterly commits
├── data/
│   ├── portfolio.example.json         # Field documentation reference
│   ├── portfolio.json                 # Live state of the DEMO account
│   ├── history.json                   # Append-only history (PLAN + EXECUTION entries)
│   ├── eurusd.rates.csv               # Daily EUR/USD rates 2000-today
│   └── monthly-historic-prices.csv    # Daily prices for all 192 universe stocks
├── backtests/                   # All backtest outputs (re-generable)
│   ├── backtest-portfolio.json
│   ├── backtest-history.json
│   ├── backtest-trades.csv
│   ├── backtest-metrics.json
│   ├── backtest-results.md      # Human-readable report (auto-generated)
│   └── backtest-dashboard.png   # Executive dashboard (auto-generated)
└── tests/
    ├── test_momentum.py         # Unit tests for the strategy core
    └── test_cagr.py             # Unit tests for the XIRR/TWR module
```

## Operational calendar

Rebalances should happen between the 5th and 10th of:
- January (Q1)
- April (Q2)
- July (Q3)
- October (Q4)

Tuesdays and Wednesdays are recommended for best liquidity.
Also avoid first and last trading hours due to high volatility.

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

This is a personal research project. **Nothing in this repository is investment advice.** The author is not a financial advisor. Past simulated performance does not guarantee future results. Trading involves risk of capital loss. See [docs/disclaimer.md](docs/disclaimer.md) for full disclaimer.

## References

- Jegadeesh, N., & Titman, S. (1993). *Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency.* Journal of Finance, 48(1), 65-91.
- Asness, C. S., Moskowitz, T. J., & Pedersen, L. H. (2013). *Value and Momentum Everywhere.* Journal of Finance, 68(3), 929-985.
- Fama, E. F., & French, K. R. (2012). *Size, value, and momentum in international stock returns.* Journal of Financial Economics, 105(3), 457-472.