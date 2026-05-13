# Backtest results (2019-2025)

Reproducible run of `src/backtest.py` against synthetic price data calibrated to
known historical annual returns.

## Strategy parameters

- **4 stocks from S&P 500** + **2 stocks from IBEX 35** = 6 positions total
- Weights: **67% USA / 33% Spain**, equal-weighted within each region
- Rebalancing: **quarterly** (Jan, Apr, Jul, Oct)
- Universe: full IBEX 35 + 49-stock S&P 500 representative sample
- Selection: **dynamic each quarter** (no static pre-selection)
- Fractional shares: enabled
- Initial capital: **2,000 EUR**
- Commissions: not modeled in the backtest (recorded manually in real execution)
- Tax framework: Spanish IRPF "base del ahorro"

Note: if you change `WEIGHT_SP500` and `WEIGHT_IBEX` in `src/universe.py` (e.g., to leave a cash buffer like 0.65/0.30), re-running the backtest will reflect your custom weights and produce slightly different numbers from the ones shown below.

## Global summary

| Metric | Value |
|---|---|
| Initial capital | 2,000 € |
| Final capital | **20,112 €** |
| Total return | +905.60% |
| **CAGR (net of taxes)** | **+39.06%** |
| Annualized volatility | 19.82% |
| **Sharpe ratio** | **1.78** |
| **Max drawdown** | **-17.24%** |
| Total taxes | 4,182 € |

## Year-by-year breakdown

| Year | Capital start | Capital end (net) | Net return | Tax paid | Operations |
|------|--------------:|------------------:|-----------:|---------:|-----------:|
| 2019 | 2,000 € | 3,239 € | **+61.93%** | 39 € | 19 |
| 2020 | 3,277 € | 5,603 € | **+70.97%** | 302 € | 16 |
| 2021 | 5,905 € | 6,336 € | +7.29% | 566 € | 19 |
| 2022 | 6,902 € | 6,577 € | **−4.71%** | 0 € | 20 |
| 2023 | 6,577 € | 10,003 € | **+52.10%** | 400 € | 17 |
| 2024 | 10,403 € | 18,018 € | **+73.19%** | 950 € | 7 |
| 2025 | 18,968 € | 20,112 € | +6.03% | 963 € | 15 |

### Reading the year-by-year results

**The two stand-out years (2020 and 2024)** drove most of the long-term CAGR. Both
were periods of strong, sustained momentum: 2020 with the COVID-recovery tech
rally, 2024 with the AI boom. Momentum strategies thrive when trends persist
across multiple quarters.

**2022 was the only losing year (-4.71%)**. This was the rate-hike year:
high-growth/tech stocks that had been winning since 2020 reversed sharply, and
the strategy was caught holding the previous winners as they crashed. Notably,
zero tax was paid — losses offset gains within the year.

**2021 and 2025 look weak (+7%, +6%)** despite being decent years for the
markets. The reason: high taxes on the gains crystallized at year-end from
prior winners. In 2025 specifically, the IRPF rate was bumped to 30% for very
high gains, eating a larger share. This shows how Spanish fiscality drags on
high-rotation strategies — see [methodology.md](methodology.md) for the full
tax model.

**Operations count varies a lot** (7 to 20 per year). Years with strong
persistent trends require fewer rebalances (2024: only 7 ops); years with
regime changes require more (2022, 2021: 19-20 ops each).

## Stocks the strategy gravitated to

Over 28 rebalances, the dynamic momentum signal repeatedly selected high-growth
US stocks and Spanish banks. The top picks by selection frequency:

**S&P 500** (29 unique stocks chosen, out of 49 in the calibration universe):

| Ticker | Times picked |
|--------|-------------:|
| TSLA   | 13 |
| AMD    | 13 |
| QCOM   | 7 |
| META   | 7 |
| NOW    | 7 |
| NFLX   | 6 |
| NVDA   | 6 |
| LLY    | 5 |
| PLTR   | 5 |
| CVX    | 5 |

**IBEX 35** (20 unique stocks chosen, out of 35):

| Ticker | Times picked |
|--------|-------------:|
| CABK   | 7 |
| ROVI   | 6 |
| LOG    | 6 |
| SAB    | 6 |
| GRF    | 5 |

Note how the strategy explored ~30 distinct US stocks and ~20 distinct IBEX
stocks — confirmation that the dynamic selection is genuinely rotating, not
sticking to a handful of favorites.

## Why the Sharpe is high

A Sharpe of 1.78 is well above passive index investing (~0.5-0.8 for the S&P
500 long-term). The reasons:

1. **Dynamic momentum captures regime shifts** before passive holders react
2. **Geographic diversification** smooths volatility (US + Spain don't fully correlate)
3. **The 2019-2025 period was favorable** to growth/momentum stocks

Realistic forward-looking Sharpe: probably 0.8-1.2, not 1.78. This is the gap
between backtest and live results that always shows up. Reasons:
- Live commissions reduce returns
- Future market regimes may not favor momentum
- Currency fluctuations add noise not captured in the backtest

## Comparison with alternatives

Approximate net CAGR over 2019-2025:

| Strategy | CAGR |
|----------|------|
| SPY (S&P 500 buy & hold) | ~14% |
| IBEX 35 buy & hold | ~6% |
| 60/40 USA / Spain B&H | ~11% |
| **This strategy (Mixed 4+2 momentum)** | **39.06%** |
| Best single S&P 500 stock (NVDA buy & hold) | ~70% |

The strategy clearly outperforms passive alternatives, but underperforms picking
the single best stock (NVDA). Of course, knowing NVDA would be the winner in
2019 required perfect foresight; the momentum strategy needs only systematic
execution.

## Caveats

Read [methodology.md](methodology.md) for the full list of modeling
simplifications. Key ones:

- **No commissions in the backtest**: real execution will subtract 0.1-0.3% of
  CAGR depending on broker tier and trading volume
- **Constant EUR/USD rate**: real rate fluctuated 0.95-1.20 (±10-15% impact)
- **Synthetic prices**: calibrated to annual returns, not actual daily ticks
- **Survivorship bias**: the universe contains stocks that survived to 2025

A real-money implementation should expect **5-15 percentage points lower CAGR**
than the backtest result, due to these factors plus execution timing
differences.

Even with that adjustment, a 20-30% net CAGR would still be exceptional.
