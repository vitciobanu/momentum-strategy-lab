# Backtest results (2019-2025)

Reproducible run of `src/backtest.py` against synthetic price data calibrated to
known historical annual returns.

## Strategy parameters

- **4 stocks from S&P 500** + **2 stocks from IBEX 35** = 6 positions total
- Weights: **65% USA / 30% Spain**, equal-weighted within each region
- Rebalancing: **quarterly** (Jan, Apr, Jul, Oct)
- Universe: full IBEX 35 + 49-stock S&P 500 representative sample
- Selection: **dynamic each quarter** (no static pre-selection)
- Fractional shares: enabled
- Initial capital: **2,000 EUR**
- Commissions: not modeled in the backtest (recorded manually in real execution)
- Tax framework: Spanish IRPF "base del ahorro"

## Global summary

| Metric | Value |
|---|---|
| Initial capital | 2,000 € |
| Final capital | **20,112 €** |
| Total return | +905.60% |
| **CAGR (net of taxes)** | **+39.06%** |
| Annualized volatility | 19.84% |
| **Sharpe ratio** | **1.78** |
| **Max drawdown** | **-17.24%** |
| Total taxes | 4,182 € |

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
