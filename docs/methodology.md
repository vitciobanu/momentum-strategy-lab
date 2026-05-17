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

## Universe definition (dynamic, not pre-selected)

The strategy scans **two complete universes** every quarter:
- The **IBEX 35**: all 35 components of the Spanish benchmark index
- The **S&P 500 large-cap subset**: the ~100 largest US stocks by market cap, representing approximately 80% of the total S&P 500 index weight

There is **no static pre-selection** of "best stocks". Every quarter, the script:
1. Downloads recent prices for every stock in both universes
2. Computes 12-1 momentum for each
3. Picks the 4 strongest from the S&P universe and the 2 strongest from the IBEX universe

Why not use the full S&P 500 (all 503 stocks)?
- The top 100 represent ~80% of total index weight
- These stocks have deep liquidity (important for execution)
- Smaller S&P components have noisier momentum signals
- It keeps each quarterly data download fast (~135 vs. ~500 tickers)

Why not pre-select "good momentum stocks" once and stick with them?
- The whole point of momentum is that **the winners change over time**
- A static list would miss new entrants (recent IPOs, sector rotations)
- A static list of 20 stocks would have only ~6% of the dynamic universe's breadth
- Bad picks made years ago would still be tested every quarter

**Universe maintenance**: the lists in `src/universe.py` should be reviewed periodically as index compositions change:
- **IBEX 35**: composition is reviewed twice a year (June and December) by BME's Technical Advisory Committee. Update the file after each review.
- **S&P 500 large-cap subset**: review yearly. The top 100 by market cap shifts gradually, but new IPOs (e.g., a future Palantir-like) can be missed if the list goes stale.

## Portfolio construction

Each quarter (Jan, Apr, Jul, Oct, days 5-10):

1. Compute 12-1 momentum for the 20 IBEX top stocks and the 20 SP500 top stocks
2. Select the **4 best** from S&P 500 and **2 best** from IBEX (by momentum rank)
3. Allocate capital with **fixed regional weights**:
   - 65% to the 4 US stocks (16.25% each)
   - 30% to the 2 Spanish stocks (15% each)
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
- S&P 500: 65% / 4 = 16.25% per position
- IBEX: 30% / 2 = 15% per position

At each rebalance, weights are reset to target. This means a position that grew a
lot may be partially trimmed even if it stays in the top 6 (though in practice the
script only rebalances new vs. closed positions, not within held ones, to minimize
unnecessary trades).

### Fractional shares

By default the strategy uses **fractional shares** (`ALLOW_FRACTIONAL_SHARES = True`
in `src/universe.py`). This is essential for small capital sizes: with 2,000 EUR
split into 6 positions, each target is ~333 EUR — too small to afford one whole
share of expensive stocks like BKNG (~5,000 USD), AVGO (~2,000 USD), or COST
(~900 USD).

IBKR supports fractional shares on most US stocks and many European ones. If your
broker doesn't or you prefer whole shares, set the flag to `False` and the script
will fall back to integer-share orders (with a warning if a target stock is
unaffordable at one full share).

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

## Commissions

The backtest **does not model commissions**. The reason is that IBKR commissions
vary significantly by:

- Account tier (Tiered vs Fixed pricing)
- Monthly trading volume (volume discounts kick in at certain thresholds)
- Account size (some markets charge more for small accounts)
- Market venue (BME, NYSE, NASDAQ have different rate cards)
- Currency conversion fees (if you operate a single-currency account)

A single hardcoded number (e.g., "3 EUR per trade") would either underestimate or
overestimate actual costs depending on your specific situation. Instead, the
real-execution workflow records **actual commissions per trade** in
`data/history.json` after each rebalance.

For a rough estimate, expect commissions to subtract roughly 0.1-0.3% per year of
CAGR for a small-to-medium portfolio. For 2,000 EUR with ~25 trades per year at
1-3 EUR each, that's 25-75 EUR per year, or ~1.5-3.5% of starting capital.

## Currency handling

In the live script (`rebalance.py`), the EUR/USD rate is fetched dynamically from
Yahoo Finance at each rebalance. All positions are valued in EUR.

When you record a US position in `portfolio.json`, the `avg_price_eur` field
captures the cost basis in EUR using the exchange rate **at the moment of
purchase**. This is the rate IBKR shows on each trade confirmation. Once
recorded, this value doesn't change — even if EUR/USD moves later, the cost
basis stays fixed at what you actually paid.

The backtest uses a **constant reference rate** (1 EUR = 1.1758 USD as of 12 May
2026) for simplicity. In reality, the EUR/USD moved between 0.95 and 1.20 during
2019-2025, which would add ±10-15% to the final result depending on exact entry
and exit timing. This is a known simplification of the backtest.

## Operational realities and known biases

This section documents behaviors that emerge in real execution and that are
NOT obvious from the strategy description. Read this before getting surprised
by them in practice.

### The "giveback" on exit

Momentum is a trend-following strategy: positions are sold only at the
quarterly rebalance, never at intra-quarter peaks. The consequence is that
when a winner finally drops out of the top 4, you typically sell it
significantly below its peak — often 15-30% below.

Example: a stock you bought at 100 USD rises to 200 USD over two quarters,
then drops to 140 USD in the third quarter (when its momentum 12-1 falls
below the top 4 threshold). The script will sell at 140, not at 200. You
still made +40% from your entry, but you "gave back" 60 USD of unrealized
gain.

This is inherent to systematic momentum. The alternative — selling at peaks
— requires daily monitoring, emotional decisions, and continuous trading.
Studies consistently show that adding stop-losses or peak-detection rules to
momentum strategies **worsens long-term returns**, because most of those
"peaks" are temporary dips that recover. Accept the giveback as the cost of
systematization.

### Winners are held, not topped up

When a position remains in the top 4 over multiple quarters, the script does
NOT add capital to it. It is simply held. The position grows organically as
the price rises, which means it can drift well above the target weight
(e.g., from 16.75% at entry to 30% after a strong run).

This is intentional. The momentum philosophy is "let winners run". Forcing
the position back to equal weight each quarter would mean partially selling
the winner — incurring taxes, commissions, and reducing exposure to the
trend that is working.

The trade-off: concentration risk grows over time. If a single position
reaches 35-40% of the portfolio, a sharp drop in that one stock will hurt
disproportionately. Currently the script does not enforce any concentration
cap. A future enhancement could add a max-position rule (e.g., trim back to
25% if any position exceeds 30%), but this would only matter for positions
that have already produced large gains — a problem worth having.

### Extreme momentum signals are normal

In the real data 2019-2025, the strategy sometimes selected stocks with
momentum 12-1 readings of +500%, +700%, even +1000% or more (e.g., TSLA in
Q4 2020, AAOI in Q1 2024, SNDK in Q2 2026). These extreme readings are not
errors and they do not signal an imminent crash. Statistically:

- High-momentum stocks DO have higher volatility (both up and down)
- They DO have larger maximum drawdowns
- But on average their forward returns over the next 3-12 months are
  POSITIVE, not negative
- Filtering them out (e.g., "don't buy if momentum > 500%") would have
  reduced backtest returns substantially

The instinct to avoid stocks "that already went up too much" is a
behavioral bias documented as "anchoring to past prices". It works in
everyday shopping but fails in trend-following finance. The strategy is
designed to override that instinct.

### Real-data backtest is work in progress

The current `src/backtest.py` uses synthetic prices calibrated to known
annual returns. **This is a known limitation.** The repository now includes
`data/monthly-historic-prices.csv` with real daily prices for 53
tickers (all 35 IBEX + 18 selected US). The plan is to:

1. Expand this dataset to cover all ~117 US universe stocks over the next
   updates.
2. Refactor `src/backtest.py` to read from the CSV instead of generating
   synthetic prices.
3. Re-generate `backtests/backtest-results.md` and `backtest-dashboard.png`
   with real data.

The synthetic backtest gave CAGR +41.69%. Preliminary analysis on the
partial real dataset suggests the real CAGR is likely higher (+50-70%),
because real data shows much more extreme momentum signals than the
synthetic calibration captured, AND because the strategy heavily favors
stocks outside the S&P 500 (Bloom Energy, Applied Optoelectronics,
Sandisk, etc.) which the synthetic calibration did not include.

The real number will only be known after the full migration. **The synthetic
backtest should be treated as a sample, not as a forecast.**

## What the strategy does NOT model

To be transparent about the limitations:

1. **Currency risk**: real EUR/USD fluctuations during 2019-2025 are not in the
   backtest (constant rate used). This could change results by ±10-15%.
2. **Commissions**: not modeled in the backtest; recorded manually in
   `history.json` for the live strategy.
3. **Slippage**: orders execute at the close price, not at a real market price.
4. **Dividend reinvestment**: dividends are not modeled (yfinance
   `auto_adjust=True` helps, but isn't perfect).
5. **Survivorship bias**: the universe contains stocks that survived to 2025.
   Stocks that delisted or went bankrupt during the period are not represented.
6. **Stress periods**: COVID-2020 and rate-hike-2022 were rare events. The
   strategy worked well during recovery (2020-2021 and 2023-2024). Future
   regimes may differ.

## References

- Jegadeesh, N., & Titman, S. (1993). *Returns to Buying Winners and Selling Losers:
  Implications for Stock Market Efficiency.* Journal of Finance, 48(1), 65-91.
- Asness, C. S., Moskowitz, T. J., & Pedersen, L. H. (2013). *Value and Momentum
  Everywhere.* Journal of Finance, 68(3), 929-985.
- Fama, E. F., & French, K. R. (2012). *Size, value, and momentum in international
  stock returns.* Journal of Financial Economics, 105(3), 457-472.

