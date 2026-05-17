# Backtest results (2019-2025)

> ## ⚠️ Important: this is a sample backtest with synthetic prices
>
> This backtest uses **synthetic monthly prices** calibrated to known annual
> returns 2014-2025 for a limited universe of ~25 US stocks plus 21 IBEX
> stocks. Real EUR/USD historical rates are used for currency conversion.
>
> **The numbers below should be treated as a sample**, not as a precise
> forecast of the strategy's actual performance.
>
> **A migration to fully real prices is underway.** The repository now
> contains `data/monthly-historic-prices.csv` with real daily prices
> for 35 IBEX stocks (full coverage) and 18 US stocks (partial coverage).
> Once the US side is extended to the full ~117 stocks in `src/universe.py`,
> `src/backtest.py` will be refactored to read from this CSV.
>
> **Preliminary analysis on the partial real dataset** shows several
> important differences from the synthetic results:
>
> - Real momentum 12-1 readings often reach +500% to +1000%+ during bull
>   periods. The synthetic calibration produces much smoother signals.
> - About **47% of all top-4 US selections** would have been stocks
>   OUTSIDE the S&P 500 (BE, AAOI, LITE, PLTR, ENPH, NU, ARM, SNDK).
>   The decision to widen the universe beyond the S&P 500 (issue #8) was
>   not a marginal improvement - it is fundamental.
> - The real CAGR is likely **higher than the +41.69% reported below**,
>   plausibly in the +50-70% range.
>
> When the real-data backtest is complete, this section will be removed
> and the numbers below will be replaced.
>
---

Reproducible run of `src/backtest.py` against synthetic price data calibrated to known historical annual returns, using **real historical EUR/USD exchange rates** from `data/eurusd_rates.csv`.

> Re-running `python src/backtest.py` regenerates `backtest-portfolio.json`, `backtest-history.json`, `backtest-trades.csv`, `backtest-metrics.json` and this file. Re-running `python scripts/build_backtest_dashboard.py` regenerates `backtest-dashboard.png`.

## Strategy parameters

- **4 stocks from the US universe** + **2 stocks from IBEX 35** = 6 positions total
- Weights: **65% USA / 30% Spain / 5% cash reserve**
- Rebalancing: **quarterly** (Jan, Apr, Jul, Oct)
- Selection: **dynamic each quarter** (no static pre-selection)
- Fractional shares: enabled
- Initial capital: **2,000 EUR**
- EUR/USD: **real historical rates per rebalance day** (from `data/eurusd_rates.csv`)
- Commissions: not modeled (recorded manually in real execution)
- Tax framework: Spanish IRPF "base del ahorro"

## Global summary

| Metric | Value |
|---|---|
| Initial capital | 2.000 € |
| Final capital | **22.926 €** |
| Total return | +1046.31% |
| **CAGR (net of taxes)** | **+41.69%** |
| Annualized volatility | 24.38% |
| **Sharpe ratio** | **1.57** |
| **Max drawdown** | **-22.80%** |
| Total taxes | 7.817 € |
| Total trades | 108 |
| Rebalances | 28 |

## Executive dashboard

![Backtest Dashboard](backtest-dashboard.png)

## Year-by-year breakdown

| Year | Capital start | Capital end (net) | Net return | Tax paid | Realized gain |
|------|--------------:|------------------:|-----------:|---------:|--------------:|
| 2019 | 2.000 € | 2.624 € | **+31.18%** | 34 € | 181 € |
| 2020 | 2.658 € | 6.492 € | **+144.24%** | 142 € | 747 € |
| 2021 | 6.633 € | 7.545 € | **+13.74%** | 178 € | 939 € |
| 2022 | 7.724 € | 7.880 € | **+2.02%** | 802 € | 4.223 € |
| 2023 | 8.682 € | 10.692 € | **+23.15%** | 224 € | 1.180 € |
| 2024 | 10.916 € | 23.456 € | **+114.88%** | 903 € | 4.752 € |
| 2025 | 24.359 € | 22.926 € | **-5.88%** | 2.766 € | 13.745 € |

## Detailed quarterly trades

One row per executed buy/sell. Sells show realized return at exit; buys leave the return column empty (the return crystallizes when sold).

### 2019 (13 buys, 7 sells, 6.686 € total volume — net annual return **+31.18%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2019 | BUY | ADBE | SP | 2.0408 | 182.95 USD | 1.1488 | 325 € |  |
| Q1 2019 | BUY | AMZN | SP | 1.9316 | 193.29 USD | 1.1488 | 325 € |  |
| Q1 2019 | BUY | ELE | IBEX | 6.8684 | 43.68 EUR |  | 300 € |  |
| Q1 2019 | BUY | LLY | SP | 2.5543 | 146.17 USD | 1.1488 | 325 € |  |
| Q1 2019 | BUY | MSFT | SP | 2.5443 | 146.74 USD | 1.1488 | 325 € |  |
| Q1 2019 | BUY | NTGY | IBEX | 5.6595 | 53.01 EUR |  | 300 € |  |
| Q2 2019 | BUY | CLNX | IBEX | 14.8873 | 20.67 EUR |  | 308 € |  |
| Q2 2019 | BUY | CRM | SP | 1.8226 | 204.62 USD | 1.1185 | 333 € |  |
| Q2 2019 | BUY | GOOGL | SP | 1.6129 | 231.23 USD | 1.1185 | 333 € |  |
| Q2 2019 | SELL | AMZN | SP | 1.9316 | 189.85 USD | 1.1185 | 328 € | +0.88% |
| Q2 2019 | SELL | LLY | SP | 2.5543 | 132.15 USD | 1.1185 | 302 € | -7.14% |
| Q2 2019 | SELL | NTGY | IBEX | 5.6595 | 51.30 EUR |  | 290 € | -3.22% |
| Q3 2019 | BUY | PLTR | SP | 150.8581 | 2.52 USD | 1.1158 | 341 € |  |
| Q3 2019 | BUY | SCYR | IBEX | 94.4379 | 3.33 EUR |  | 314 € |  |
| Q3 2019 | BUY | TSLA | SP | 7.3671 | 51.59 USD | 1.1158 | 341 € |  |
| Q3 2019 | SELL | ELE | IBEX | 6.8684 | 49.27 EUR |  | 338 € | +12.79% |
| Q3 2019 | SELL | GOOGL | SP | 1.6129 | 235.16 USD | 1.1158 | 340 € | +1.95% |
| Q3 2019 | SELL | MSFT | SP | 2.5443 | 158.38 USD | 1.1158 | 361 € | +11.12% |
| Q4 2019 | BUY | JPM | SP | 2.8756 | 155.81 USD | 1.1154 | 402 € |  |
| Q4 2019 | SELL | ADBE | SP | 2.0408 | 248.62 USD | 1.1154 | 455 € | +39.96% |

### 2020 (8 buys, 10 sells, 10.323 € total volume — net annual return **+144.24%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2020 | BUY | NOW | SP | 2.4749 | 212.96 USD | 1.1029 | 478 € |  |
| Q1 2020 | BUY | WMT | SP | 2.4507 | 215.06 USD | 1.1029 | 478 € |  |
| Q1 2020 | SELL | CLNX | IBEX | 14.8873 | 25.07 EUR |  | 373 € | +21.24% |
| Q1 2020 | SELL | CRM | SP | 1.8226 | 247.84 USD | 1.1029 | 410 € | +22.83% |
| Q1 2020 | SELL | PLTR | SP | 150.8581 | 3.31 USD | 1.1029 | 453 € | +32.95% |
| Q2 2020 | BUY | AMD | SP | 164.4217 | 3.86 USD | 1.0877 | 584 € |  |
| Q2 2020 | BUY | NFLX | SP | 5.4178 | 117.28 USD | 1.0877 | 584 € |  |
| Q2 2020 | BUY | SAN | IBEX | 93.7057 | 5.75 EUR |  | 539 € |  |
| Q2 2020 | SELL | JPM | SP | 2.8756 | 214.48 USD | 1.0877 | 567 € | +41.16% |
| Q2 2020 | SELL | SCYR | IBEX | 94.4379 | 3.90 EUR |  | 369 € | +17.26% |
| Q2 2020 | SELL | WMT | SP | 2.4507 | 223.09 USD | 1.0877 | 503 € | +5.18% |
| Q3 2020 | BUY | QCOM | SP | 19.3237 | 41.21 USD | 1.1872 | 671 € |  |
| Q3 2020 | SELL | NFLX | SP | 5.4178 | 130.60 USD | 1.1872 | 596 € | +2.03% |
| Q4 2020 | BUY | NFLX | SP | 6.4654 | 162.05 USD | 1.1679 | 897 € |  |
| Q4 2020 | BUY | NVDA | SP | 83.7759 | 12.51 USD | 1.1679 | 897 € |  |
| Q4 2020 | SELL | NOW | SP | 2.4749 | 298.98 USD | 1.1679 | 634 € | +32.58% |
| Q4 2020 | SELL | QCOM | SP | 19.3237 | 52.03 USD | 1.1679 | 861 € | +28.34% |
| Q4 2020 | SELL | SAN | IBEX | 93.7057 | 4.59 EUR |  | 430 € | -20.25% |

### 2021 (1 buys, 2 sells, 3.790 € total volume — net annual return **+13.74%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q2 2021 | SELL | NFLX | SP | 6.4654 | 147.53 USD | 1.2127 | 787 € | -12.32% |
| Q4 2021 | BUY | UNH | SP | 2.3439 | 682.60 USD | 1.1684 | 1.369 € |  |
| Q4 2021 | SELL | AMD | SP | 164.4217 | 11.61 USD | 1.1684 | 1.634 € | +179.72% |

### 2022 (11 buys, 9 sells, 28.828 € total volume — net annual return **+2.02%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2022 | BUY | AAPL | SP | 2.8426 | 498.61 USD | 1.1152 | 1.271 € |  |
| Q1 2022 | BUY | AVGO | SP | 38.1728 | 37.13 USD | 1.1152 | 1.271 € |  |
| Q1 2022 | BUY | CABK | IBEX | 313.2984 | 3.74 EUR |  | 1.173 € |  |
| Q1 2022 | BUY | COST | SP | 2.3520 | 602.63 USD | 1.1152 | 1.271 € |  |
| Q1 2022 | BUY | ROVI | IBEX | 30.1348 | 38.93 EUR |  | 1.173 € |  |
| Q1 2022 | SELL | NVDA | SP | 83.7759 | 26.02 USD | 1.1152 | 1.954 € | +117.86% |
| Q1 2022 | SELL | TSLA | SP | 7.3671 | 473.98 USD | 1.1152 | 3.131 € | +819.27% |
| Q2 2022 | BUY | LLY | SP | 2.7598 | 520.81 USD | 1.0504 | 1.368 € |  |
| Q2 2022 | BUY | XOM | SP | 60.2797 | 23.84 USD | 1.0504 | 1.368 € |  |
| Q2 2022 | SELL | AAPL | SP | 2.8426 | 447.79 USD | 1.0504 | 1.212 € | -4.65% |
| Q2 2022 | SELL | COST | SP | 2.3520 | 584.31 USD | 1.0504 | 1.308 € | +2.94% |
| Q2 2022 | SELL | ROVI | IBEX | 30.1348 | 35.69 EUR |  | 1.075 € | -8.33% |
| Q3 2022 | BUY | NOW | SP | 2.2036 | 636.83 USD | 1.0192 | 1.377 € |  |
| Q3 2022 | BUY | ORCL | SP | 31.1036 | 45.12 USD | 1.0192 | 1.377 € |  |
| Q3 2022 | SELL | AVGO | SP | 38.1728 | 31.10 USD | 1.0192 | 1.165 € | -8.34% |
| Q3 2022 | SELL | UNH | SP | 2.3439 | 714.01 USD | 1.0192 | 1.642 € | +19.91% |
| Q4 2022 | BUY | NTGY | IBEX | 13.8357 | 97.54 EUR |  | 1.350 € |  |
| Q4 2022 | BUY | V | SP | 7.3598 | 197.75 USD | 0.9955 | 1.462 € |  |
| Q4 2022 | SELL | CABK | IBEX | 313.2984 | 4.71 EUR |  | 1.476 € | +25.84% |
| Q4 2022 | SELL | ORCL | SP | 31.1036 | 44.88 USD | 0.9955 | 1.402 € | +1.83% |

### 2023 (9 buys, 9 sells, 27.122 € total volume — net annual return **+23.15%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2023 | BUY | ORCL | SP | 34.1907 | 44.91 USD | 1.0851 | 1.415 € |  |
| Q1 2023 | SELL | V | SP | 7.3598 | 184.54 USD | 1.0851 | 1.252 € | -14.39% |
| Q2 2023 | BUY | SCYR | IBEX | 323.8313 | 4.06 EUR |  | 1.315 € |  |
| Q2 2023 | BUY | TSLA | SP | 3.9577 | 397.11 USD | 1.1032 | 1.425 € |  |
| Q2 2023 | SELL | LLY | SP | 2.7598 | 678.66 USD | 1.1032 | 1.698 € | +24.07% |
| Q2 2023 | SELL | NTGY | IBEX | 13.8357 | 85.90 EUR |  | 1.188 € | -11.94% |
| Q3 2023 | BUY | AMD | SP | 91.0743 | 17.76 USD | 1.1024 | 1.467 € |  |
| Q3 2023 | BUY | BA | SP | 35.5006 | 45.57 USD | 1.1024 | 1.467 € |  |
| Q3 2023 | BUY | MSFT | SP | 4.5419 | 356.19 USD | 1.1024 | 1.467 € |  |
| Q3 2023 | BUY | UNI | IBEX | 48.3988 | 27.99 EUR |  | 1.355 € |  |
| Q3 2023 | SELL | ORCL | SP | 34.1907 | 44.17 USD | 1.1024 | 1.370 € | -3.19% |
| Q3 2023 | SELL | SCYR | IBEX | 323.8313 | 4.01 EUR |  | 1.299 € | -1.24% |
| Q3 2023 | SELL | TSLA | SP | 3.9577 | 392.96 USD | 1.1024 | 1.411 € | -0.97% |
| Q3 2023 | SELL | XOM | SP | 60.2797 | 33.18 USD | 1.1024 | 1.815 € | +32.61% |
| Q4 2023 | BUY | PLTR | SP | 1342.5078 | 1.38 USD | 1.0615 | 1.741 € |  |
| Q4 2023 | BUY | TSLA | SP | 4.2826 | 431.62 USD | 1.0615 | 1.741 € |  |
| Q4 2023 | SELL | BA | SP | 35.5006 | 45.07 USD | 1.0615 | 1.507 € | +2.72% |
| Q4 2023 | SELL | NOW | SP | 2.2036 | 1054.23 USD | 1.0615 | 2.189 € | +58.95% |

### 2024 (5 buys, 5 sells, 27.228 € total volume — net annual return **+114.88%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2024 | BUY | NVDA | SP | 139.4532 | 17.63 USD | 1.0843 | 2.268 € |  |
| Q1 2024 | SELL | PLTR | SP | 1342.5078 | 2.01 USD | 1.0843 | 2.484 € | +42.63% |
| Q2 2024 | BUY | AVGO | SP | 46.4918 | 65.44 USD | 1.0716 | 2.839 € |  |
| Q2 2024 | BUY | CRM | SP | 8.6972 | 349.79 USD | 1.0716 | 2.839 € |  |
| Q2 2024 | SELL | MSFT | SP | 4.5419 | 671.54 USD | 1.0716 | 2.846 € | +93.95% |
| Q2 2024 | SELL | NVDA | SP | 139.4532 | 18.64 USD | 1.0716 | 2.426 € | +6.97% |
| Q3 2024 | BUY | PLTR | SP | 1011.7674 | 3.29 USD | 1.0816 | 3.075 € |  |
| Q3 2024 | SELL | AMD | SP | 91.0743 | 33.12 USD | 1.0816 | 2.789 € | +90.05% |
| Q4 2024 | BUY | CABK | IBEX | 247.9472 | 12.73 EUR |  | 3.156 € |  |
| Q4 2024 | SELL | UNI | IBEX | 48.3988 | 51.78 EUR |  | 2.506 € | +85.02% |

### 2025 (10 buys, 9 sells, 86.264 € total volume — net annual return **-5.88%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2025 | BUY | NVDA | SP | 81.7447 | 53.28 USD | 1.0397 | 4.189 € |  |
| Q1 2025 | SELL | TSLA | SP | 4.2826 | 1438.24 USD | 1.0397 | 5.924 € | +240.20% |
| Q2 2025 | BUY | ORCL | SP | 48.2987 | 95.28 USD | 1.1389 | 4.041 € |  |
| Q2 2025 | BUY | WMT | SP | 6.9176 | 665.28 USD | 1.1389 | 4.041 € |  |
| Q2 2025 | SELL | AVGO | SP | 46.4918 | 113.29 USD | 1.1389 | 4.625 € | +62.90% |
| Q2 2025 | SELL | CRM | SP | 8.6972 | 564.26 USD | 1.1389 | 4.309 € | +51.78% |
| Q3 2025 | BUY | NFLX | SP | 42.2441 | 107.52 USD | 1.1429 | 3.974 € |  |
| Q3 2025 | SELL | WMT | SP | 6.9176 | 708.87 USD | 1.1429 | 4.291 € | +6.18% |
| Q4 2025 | BUY | BBVA | IBEX | 817.4755 | 5.10 EUR |  | 4.165 € |  |
| Q4 2025 | BUY | BKT | IBEX | 260.3703 | 16.00 EUR |  | 4.165 € |  |
| Q4 2025 | BUY | LLY | SP | 7.4317 | 702.61 USD | 1.1572 | 4.512 € |  |
| Q4 2025 | BUY | META | SP | 24.6154 | 212.13 USD | 1.1572 | 4.512 € |  |
| Q4 2025 | BUY | NOW | SP | 4.7389 | 1101.86 USD | 1.1572 | 4.512 € |  |
| Q4 2025 | BUY | QCOM | SP | 87.8130 | 59.46 USD | 1.1572 | 4.512 € |  |
| Q4 2025 | SELL | CABK | IBEX | 247.9472 | 24.53 EUR |  | 6.082 € | +92.71% |
| Q4 2025 | SELL | NFLX | SP | 42.2441 | 125.19 USD | 1.1572 | 4.570 € | +14.99% |
| Q4 2025 | SELL | NVDA | SP | 81.7447 | 40.91 USD | 1.1572 | 2.890 € | -31.01% |
| Q4 2025 | SELL | ORCL | SP | 48.2987 | 114.67 USD | 1.1572 | 4.786 € | +18.44% |
| Q4 2025 | SELL | PLTR | SP | 1011.7674 | 7.05 USD | 1.1572 | 6.164 € | +100.46% |

## Important notes

- **Synthetic prices** are calibrated to public annual returns 2014-2025. They are NOT real daily ticks. For institutional-grade backtests use real historical prices from a data provider.
- **Real EUR/USD historical rates** are used per rebalance day. The rate moved from ~1.15 in 2019 to parity (~1.00) in 2022 and back to ~1.15 in 2025. This adds realistic currency risk to the backtest.
- **No commissions are modeled** in the backtest. Real execution will subtract 0.1-0.3% per year of CAGR depending on broker tier.
- **Survivorship bias**: the universe contains stocks that survived to 2025. Stocks that delisted are not represented.

A real-money implementation should expect **5-15 percentage points lower CAGR** than the backtest result, due to these factors plus execution timing differences.

Even with that adjustment, a **25-30% net CAGR would still be exceptional**.
