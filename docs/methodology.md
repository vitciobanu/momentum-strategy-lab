# Methodology

## Overview

This strategy applies the classic momentum factor (Jegadeesh & Titman, 1993) to a
mixed portfolio of US and Spanish equities. The core hypothesis is that stocks
with strong recent price performance tend to continue outperforming for the next
3-12 months — a well-documented market anomaly.

## The momentum signal

For each stock, at each rebalance date, we compute:

```
momentum_12_1(t) = (Price(t-1) / Price(t-12)) - 1
```

Where:
- `Price(t-1)` is the price 1 month before the rebalance date (last closed month)
- `Price(t-12)` is the price 12 months before the rebalance date

The reason to **skip the most recent month** is well-established in the literature:
1-month returns exhibit short-term reversal (the opposite of momentum), so including
them adds noise.

## Universe pre-selection (one-time)

Rather than using all S&P 500 / IBEX 35 stocks, we pre-select the **top 20 of each
market based on their average momentum during 2015-2018** (4-year pre-selection
period).

Why pre-select?
- Reduces computational cost
- Concentrates on stocks with persistent momentum behavior
- Avoids stocks with random, unstable returns

Why use a pre-period (2015-2018)?
- Avoids **look-ahead bias**: we don't use 2019+ data to select the universe we'll
  test on 2019+
- The 4-year window is long enough to filter out luck
- It mimics what a real investor in early 2019 could have done

The top 20 lists are fixed in `src/universe.py`.

## Portfolio construction

Each quarter (Jan, Apr, Jul, Oct, days 5-10):

1. Compute 12-1 momentum for the 20 IBEX top stocks and the 20 SP500 top stocks
2. Select the **4 best** from S&P 500 and **2 best** from IBEX (by momentum rank)
3. Allocate capital with **fixed regional weights**:
   - 67% to the 4 US stocks (16.75% each)
   - 33% to the 2 Spanish stocks (16.5% each)
4. Sell positions no longer in the top 6
5. Buy new positions to fill the gaps
6. Hold positions that are still in the top 6 (no rebalancing of weights within a
   quarter — only at quarter boundaries)

## Why 4+2 and not 6 free positions?

We could let momentum freely pick the top 6 across both markets. We don't, because:

1. **Geographic diversification** is structural protection against country-specific
   shocks (Spanish banking crisis, US tech crash)
2. **Currency diversification** smooths returns: when the EUR/USD moves, one part
   of the portfolio is naturally hedged
3. **Tax / commission considerations**: Spanish stocks are cheaper to trade for an
   IBKR account based in Spain
4. **The free-selection version tends to over-allocate to US** (which historically
   has dominated momentum rankings), defeating the diversification purpose

## Position sizing

Within each region, positions are **equal-weighted**:
- S&P 500: 67% / 4 = 16.75% per position
- IBEX: 33% / 2 = 16.5% per position

At each rebalance, weights are reset to target. This means a position that grew a
lot may be partially trimmed even if it stays in the top 6 (though in practice the
script only rebalances new vs. closed positions, not within held ones, to minimize
unnecessary trades).

## Tax modeling

The backtest applies Spanish IRPF "base del ahorro" brackets per year:

| Year | 0-6k | 6k-50k | 50k-200k | 200k-300k | >300k |
|------|------|--------|----------|-----------|-------|
| 2019-2020 | 19% | 21% | 23% | 23% | 23% |
| 2021 | 19% | 21% | 23% | 26% | 26% |
| 2022-2024 | 19% | 21% | 23% | 27% | 28% |
| 2025 | 19% | 21% | 23% | 27% | 30% |

Taxes are calculated on **realized gains** (gains from positions sold during the
year). Losses can offset gains within the same year (and carry forward 4 years).
The backtest simplifies this to within-year offsetting only.

## Commission model

- **IBEX (BME) stocks**: 3 EUR per trade (IBKR tier rate for Madrid)
- **S&P 500 stocks**: 1 USD per trade (IBKR Tiered rate)

A round-trip (buy + sell) costs 6 EUR for an IBEX stock or 2 USD for a US stock.

## Currency handling

In the live script (`rebalance.py`), the EUR/USD rate is fetched dynamically. All
positions are valued in EUR (USD values are converted at the live rate). 

The backtest uses a **constant reference rate** (1 EUR = 1.1758 USD as of 12 May 2026)
for simplicity. In reality, the EUR/USD moved between 0.95 and 1.20 during 2019-2025,
which would add ±15% to the final result depending on exact entry/exit timing. This
is a known simplification of the backtest.

## What the strategy does NOT model

To be transparent about the limitations:

1. **Currency risk**: real EUR/USD fluctuations during 2019-2025 are not in the
   backtest (constant rate used). This could change results by ±10-15%.
2. **Slippage**: orders execute at the close price, not at a real market price.
3. **Dividend reinvestment**: dividends are not modeled (yfinance auto_adjust=True
   helps, but isn't perfect).
4. **Survivorship bias**: the universe contains stocks that survived to 2025. Stocks
   that delisted or went bankrupt during the period are not represented.
5. **Look-ahead bias in universe selection**: although we use 2015-2018 for
   pre-selection, the choice of "top 20 by momentum" was itself informed by
   knowing momentum works. A truly bias-free study would use a random universe.
6. **Stress periods**: COVID-2020 and rate-hike-2022 were rare events. The
   strategy worked well during recovery (2020-2021 and 2023-2024). Future regimes
   may differ.

## References

- Jegadeesh, N., & Titman, S. (1993). *Returns to Buying Winners and Selling Losers:
  Implications for Stock Market Efficiency.* Journal of Finance, 48(1), 65-91.
- Asness, C. S., Moskowitz, T. J., & Pedersen, L. H. (2013). *Value and Momentum
  Everywhere.* Journal of Finance, 68(3), 929-985.
- Fama, E. F., & French, K. R. (2012). *Size, value, and momentum in international
  stock returns.* Journal of Financial Economics, 105(3), 457-472.
