# Backtest results (2019-2025)

Reproducible run of `src/backtest.py` against synthetic price data calibrated to
known historical annual returns.

## Strategy parameters

- **4 stocks from S&P 500** + **2 stocks from IBEX 35** = 6 positions total
- Weights: **65% USA / 30% Spain**, equal-weighted within each region
- Rebalancing: **quarterly** (Jan, Apr, Jul, Oct)
- Pre-selected universe: top 20 of each market by momentum 2015-2018
- Initial capital: **2,000 EUR**
- Commissions: 3 EUR/trade (IBEX), 1 USD/trade (S&P 500)
- Tax framework: Spanish IRPF "base del ahorro"

## Year-by-year breakdown

| Year | Capital start | Capital end (net) | Net return | Tax paid | Operations |
|------|--------------:|------------------:|-----------:|---------:|-----------:|
| 2019 | 2,000 € | 2,880 € | +43.99% | 53 € | 25 |
| 2020 | 2,933 € | 5,589 € | **+90.54%** | 181 € | 12 |
| 2021 | 5,769 € | 6,073 € | +5.27% | 732 € | 15 |
| 2022 | 6,805 € | 6,699 € | -1.56% | 0 € | 15 |
| 2023 | 6,699 € | 8,380 € | +25.10% | 156 € | 22 |
| 2024 | 8,536 € | 17,067 € | **+99.94%** | 54 € | 7 |
| 2025 | 17,121 € | 17,934 € | +4.75% | 732 € | 12 |

## Global summary

| Metric | Value |
|---|---|
| Initial capital | 2,000 € |
| Final capital | **17,934 €** |
| Total return | +796.71% |
| **CAGR (net)** | **+36.80%** |
| Annualized volatility | 17.09% |
| **Sharpe ratio** | **1.94** |
| **Max drawdown** | **-12.23%** |
| Total commissions | 131 € |
| Total taxes | 2,639 € |

## Discussion

### Where the strategy worked

- **2020 (+90.54%)**: COVID-recovery was a momentum-friendly regime. After the
  March crash, tech stocks (NVDA, AVGO, MSFT) led the recovery, exactly what
  momentum picks up.
- **2024 (+99.94%)**: The AI rally and Fed pivot expectations created strong
  persistent trends, which momentum captures well.

### Where the strategy struggled

- **2022 (-1.56%)**: Year of major regime change. Rate hikes destroyed
  growth/tech momentum (which had dominated 2020-2021 selection), and rotation to
  value/energy happened faster than the 12-1 lookback could detect. The strategy
  was "caught" holding the previous winners as they crashed.
- **2025 (+4.75%)**: Underperformance because of high taxes paid (€732) on prior
  gains realized through the year.

### Why the Sharpe is high

A Sharpe of 1.94 is well above what you see in passive index investing (~0.5-0.8
for the S&P 500 long-term). The reasons:

1. **Concentration in momentum-screened universe** = higher expected return
2. **Geographic diversification** smooths volatility
3. **The 2019-2025 period was favorable** to growth/momentum stocks

Realistic forward-looking Sharpe: probably 0.8-1.2, not 1.94. This is the gap
between backtest and live results that always shows up.

### Comparison with alternatives

Approximate net CAGR over 2019-2025:

| Strategy | CAGR |
|----------|------|
| SPY (S&P 500 buy & hold) | ~14% |
| IBEX 35 buy & hold | ~6% |
| 60/40 USA stocks / Spanish stocks (B&H) | ~11% |
| **This strategy (Mixed 4+2 momentum)** | **36.80%** |
| Best single S&P 500 stock (NVDA buy & hold) | ~70% |

The strategy clearly outperforms passive alternatives, but underperforms picking
the single best stock (NVDA). Of course, knowing NVDA would be the winner in 2019
required perfect foresight; the momentum strategy needs only systematic execution.

## Caveats

Read [methodology.md](methodology.md) for the full list of modeling
simplifications. Key ones:

- Constant EUR/USD exchange rate (real rate fluctuated 0.95-1.20)
- No slippage modeling
- Synthetic prices (not actual daily ticks)
- Survivorship bias in the universe

A real-money implementation should expect **5-15 percentage points lower CAGR**
than the backtest result, due to these factors plus execution timing differences.

Even with that adjustment, a 20-25% net CAGR would still be exceptional.
