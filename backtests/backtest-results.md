# Backtest results (2019-2025)

Reproducible run of `src/backtest.py` against **REAL historical price data** from `data/monthly-historic-prices.csv` and **REAL historical EUR/USD rates** from `data/eurusd.rates.csv`.

> Re-running `python src/backtest.py` regenerates the JSON/CSV outputs. Then run `python scripts/build_backtest_dashboard.py` and `python scripts/build_backtest_report.py` to regenerate the dashboard image and this markdown report.

## Strategy parameters

- **4 stocks from the US universe** + **2 stocks from IBEX 35** = 6 positions total
- Weights: **65% USA / 30% Spain / 5% cash reserve**
- Rebalancing: **quarterly** (Jan, Apr, Jul, Oct)
- Selection: **dynamic each quarter** (no static pre-selection)
- Fractional shares: enabled
- Initial capital: **2,000 EUR**
- US universe: **157** stocks (NYSE + NASDAQ, includes S&P 500 large caps + non-S&P 500 + recent momentum mid-caps)
- IBEX universe: **35** stocks (complete IBEX 35)
- Price data: **real historical daily prices** from `data/monthly-historic-prices.csv`, resampled to month-end closes
- EUR/USD: **real historical rates per rebalance day** (from `data/eurusd.rates.csv`)
- Commissions: not modeled (recorded manually in real execution)
- Tax framework: Spanish IRPF "base del ahorro"

## Global summary

| Metric | Value |
|---|---|
| Initial capital | 2.000 € |
| Final capital | **48.588 €** |
| Total return | +2329.42% |
| **CAGR (net of taxes)** | **+57.74%** |
| Annualized volatility | 44.20% |
| **Sharpe ratio** | **1.26** |
| **Max drawdown** | **-45.31%** |
| Total taxes | 10.661 € |
| Total trades | 164 |
| Rebalances | 28 |

## Executive dashboard

![Backtest Dashboard](backtest-dashboard.png)

## The 2021-2022 drawdown: what really happened

The strategy reached a peak in **October 2021** at **13.264,33 €**, then suffered a sustained decline reaching its lowest point in **June 2022** at **7.254,67 €** — a drawdown of **-45.31%** from the previous peak.

From peak to trough took **8 months**. The portfolio then took another **14 months** to reach the previous peak again, finally crossing it in **August 2023**. Total time underwater: **~22 months**.

This is the most important number to internalize before trusting the strategy. The +56.95% headline CAGR is real, but reaching it required holding through almost two years of seeing the portfolio worth less than its previous best. Anyone who panicked and exited near the trough crystallized a -45% loss; those who held saw the portfolio continue to **48.588 €** by the end of the backtest.

## Year-by-year breakdown

| Year | Capital start | Capital end (net) | Net return | Tax paid | Realized gain |
|------|--------------:|------------------:|-----------:|---------:|--------------:|
| 2019 | 2.000 € | 4.063 € | **+103.17%** | 0 € | -38 € |
| 2020 | 4.063 € | 10.228 € | **+151.72%** | 635 € | 3.343 € |
| 2021 | 10.228 € | 10.250 € | **+0.22%** | 1.050 € | 5.526 € |
| 2022 | 10.250 € | 8.534 € | **-16.75%** | 0 € | -927 € |
| 2023 | 8.534 € | 17.148 € | **+100.95%** | 509 € | 2.678 € |
| 2024 | 17.148 € | 25.283 € | **+47.44%** | 2.603 € | 12.964 € |
| 2025 | 25.283 € | 48.588 € | **+92.18%** | 2.932 € | 14.535 € |

## Monthly trajectory

Portfolio value at the end of each month, net of yearly tax. The drawdown column shows how far below the running peak the portfolio was at that point.

| Date | Value (€) | Monthly return | Drawdown from peak |
|------|----------:|---------------:|-------------------:|
| 2019-01 | 2.000,00 € | — | 0,00% |
| 2019-02 | 2.181,38 € | +9.07% | 0,00% |
| 2019-03 | 2.110,79 € | -3.24% | -3.24% |
| 2019-04 | 2.233,16 € | +5.80% | 0,00% |
| 2019-05 | 2.551,85 € | +14.27% | 0,00% |
| 2019-06 | 2.758,72 € | +8.11% | 0,00% |
| 2019-07 | 3.358,45 € | +21.74% | 0,00% |
| 2019-08 | 3.594,87 € | +7.04% | 0,00% |
| 2019-09 | 3.071,35 € | -14.56% | -14.56% |
| 2019-10 | 3.244,04 € | +5.62% | -9.76% |
| 2019-11 | 4.108,15 € | +26.64% | 0,00% |
| 2019-12 | 4.063,39 € | -1.09% | -1.09% |
| 2020-01 | 3.862,83 € | -4.94% | -5.97% |
| 2020-02 | 4.451,69 € | +15.24% | 0,00% |
| 2020-03 | 3.439,78 € | -22.73% | -22.73% |
| 2020-04 | 4.470,35 € | +29.96% | 0,00% |
| 2020-05 | 5.326,62 € | +19.15% | 0,00% |
| 2020-06 | 5.319,07 € | -0.14% | -0.14% |
| 2020-07 | 6.186,09 € | +16.30% | 0,00% |
| 2020-08 | 7.631,35 € | +23.36% | 0,00% |
| 2020-09 | 7.038,10 € | -7.77% | -7.77% |
| 2020-10 | 7.101,94 € | +0.91% | -6.94% |
| 2020-11 | 9.483,94 € | +33.54% | 0,00% |
| 2020-12 | 10.228,18 € | +7.85% | 0,00% |
| 2021-01 | 11.080,63 € | +8.33% | 0,00% |
| 2021-02 | 10.189,36 € | -8.04% | -8.04% |
| 2021-03 | 9.900,07 € | -2.84% | -10.65% |
| 2021-04 | 9.728,14 € | -1.74% | -12.21% |
| 2021-05 | 9.679,19 € | -0.50% | -12.65% |
| 2021-06 | 10.927,05 € | +12.89% | -1.39% |
| 2021-07 | 10.828,08 € | -0.91% | -2.28% |
| 2021-08 | 11.982,86 € | +10.66% | 0,00% |
| 2021-09 | 11.596,86 € | -3.22% | -3.22% |
| 2021-10 | 13.264,33 € | +14.38% | 0,00% |
| 2021-11 | 12.900,15 € | -2.75% | -2.75% |
| 2021-12 | 10.250,31 € | -20.54% | -22.72% |
| 2022-01 | 9.157,61 € | -10.66% | -30.96% |
| 2022-02 | 9.176,85 € | +0.21% | -30.82% |
| 2022-03 | 9.602,44 € | +4.64% | -27.61% |
| 2022-04 | 8.013,22 € | -16.55% | -39.59% |
| 2022-05 | 8.754,12 € | +9.25% | -34.00% |
| 2022-06 | 7.254,67 € | -17.13% | -45.31% |
| 2022-07 | 7.599,63 € | +4.76% | -42.71% |
| 2022-08 | 8.031,35 € | +5.68% | -39.45% |
| 2022-09 | 7.453,10 € | -7.20% | -43.81% |
| 2022-10 | 9.136,31 € | +22.58% | -31.12% |
| 2022-11 | 9.077,70 € | -0.64% | -31.56% |
| 2022-12 | 8.533,67 € | -5.99% | -35.66% |
| 2023-01 | 8.991,21 € | +5.36% | -32.22% |
| 2023-02 | 8.900,33 € | -1.01% | -32.90% |
| 2023-03 | 8.687,76 € | -2.39% | -34.50% |
| 2023-04 | 7.862,65 € | -9.50% | -40.72% |
| 2023-05 | 9.446,65 € | +20.15% | -28.78% |
| 2023-06 | 10.515,68 € | +11.32% | -20.72% |
| 2023-07 | 11.318,24 € | +7.63% | -14.67% |
| 2023-08 | 15.377,72 € | +35.87% | 0,00% |
| 2023-09 | 14.523,09 € | -5.56% | -5.56% |
| 2023-10 | 12.547,28 € | -13.60% | -18.41% |
| 2023-11 | 15.322,85 € | +22.12% | -0.36% |
| 2023-12 | 17.148,38 € | +11.91% | 0,00% |
| 2024-01 | 18.725,30 € | +9.20% | 0,00% |
| 2024-02 | 21.935,05 € | +17.14% | 0,00% |
| 2024-03 | 23.320,71 € | +6.32% | 0,00% |
| 2024-04 | 22.690,16 € | -2.70% | -2.70% |
| 2024-05 | 24.440,27 € | +7.71% | 0,00% |
| 2024-06 | 22.004,15 € | -9.97% | -9.97% |
| 2024-07 | 23.916,70 € | +8.69% | -2.14% |
| 2024-08 | 25.266,49 € | +5.64% | 0,00% |
| 2024-09 | 25.665,19 € | +1.58% | 0,00% |
| 2024-10 | 26.098,76 € | +1.69% | 0,00% |
| 2024-11 | 31.667,48 € | +21.34% | 0,00% |
| 2024-12 | 25.282,92 € | -20.16% | -20.16% |
| 2025-01 | 26.154,93 € | +3.45% | -17.41% |
| 2025-02 | 26.875,49 € | +2.75% | -15.13% |
| 2025-03 | 22.519,89 € | -16.21% | -28.89% |
| 2025-04 | 24.965,78 € | +10.86% | -21.16% |
| 2025-05 | 30.186,01 € | +20.91% | -4.68% |
| 2025-06 | 38.002,64 € | +25.89% | 0,00% |
| 2025-07 | 44.254,89 € | +16.45% | 0,00% |
| 2025-08 | 43.079,32 € | -2.66% | -2.66% |
| 2025-09 | 49.497,78 € | +14.90% | 0,00% |
| 2025-10 | 56.911,11 € | +14.98% | 0,00% |
| 2025-11 | 48.843,88 € | -14.18% | -14.18% |
| 2025-12 | 48.588,33 € | -0.52% | -14.62% |

## Most-selected stocks

### US universe (top 15)

| Ticker | Times selected |
|---|---:|
| PDD | 4 |
| NVDA | 4 |
| ENPH | 3 |
| MOD | 3 |
| VICR | 2 |
| AMD | 2 |
| LLY | 2 |
| BE | 2 |
| SITM | 2 |
| MP | 2 |
| CYTK | 2 |
| POWL | 2 |
| ARWR | 1 |
| CIEN | 1 |
| MELI | 1 |

### IBEX 35 (top 10)

| Ticker | Times selected |
|---|---:|
| SAB | 4 |
| BBVA | 3 |
| ITX | 3 |
| SLR | 2 |
| ANA | 2 |
| FDR | 2 |
| ROVI | 2 |
| REP | 2 |
| IDR | 2 |
| NTGY | 1 |

## Detailed quarterly trades

One row per executed buy/sell. Sells show realized return at exit; buys leave the return column empty (the return crystallizes when sold).

### 2019 (13 buys, 8 sells, 7.637 € total volume — net annual return **+103.17%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2019 | BUY | ARWR | US | 26.3407 | 14.12 USD | 1.1444 | 325 € |  |
| Q1 2019 | BUY | CIEN | US | 9.7645 | 38.09 USD | 1.1444 | 325 € |  |
| Q1 2019 | BUY | ENPH | US | 51.4426 | 7.23 USD | 1.1444 | 325 € |  |
| Q1 2019 | BUY | NTGY | IBEX | 12.3203 | 24.35 EUR |  | 300 € |  |
| Q1 2019 | BUY | SLR | IBEX | 55.6586 | 5.39 EUR |  | 300 € |  |
| Q1 2019 | BUY | VICR | US | 9.4422 | 39.39 USD | 1.1444 | 325 € |  |
| Q2 2019 | BUY | AMD | US | 14.7296 | 27.63 USD | 1.1215 | 363 € |  |
| Q2 2019 | BUY | ANA | IBEX | 3.2427 | 103.30 EUR |  | 335 € |  |
| Q2 2019 | BUY | LLY | US | 3.4773 | 117.04 USD | 1.1215 | 363 € |  |
| Q2 2019 | SELL | CIEN | US | 9.7645 | 38.36 USD | 1.1215 | 334 € | +2.77% |
| Q2 2019 | SELL | NTGY | IBEX | 12.3203 | 25.32 EUR |  | 312 € | +3.98% |
| Q2 2019 | SELL | VICR | US | 9.4422 | 37.51 USD | 1.1215 | 316 € | -2.83% |
| Q3 2019 | BUY | CLNX | IBEX | 14.9249 | 27.39 EUR |  | 409 € |  |
| Q3 2019 | BUY | MELI | US | 0.9725 | 621.42 USD | 1.1074 | 546 € |  |
| Q3 2019 | SELL | ANA | IBEX | 3.2427 | 96.30 EUR |  | 312 € | -6.78% |
| Q3 2019 | SELL | LLY | US | 3.4773 | 108.95 USD | 1.1074 | 342 € | -5.73% |
| Q3 2019 | SELL | SLR | IBEX | 55.6586 | 5.38 EUR |  | 299 € | -0.28% |
| Q4 2019 | BUY | KLAC | US | 2.4799 | 169.04 USD | 1.1150 | 376 € |  |
| Q4 2019 | BUY | PDD | US | 14.3782 | 40.88 USD | 1.1150 | 527 € |  |
| Q4 2019 | SELL | AMD | US | 14.7296 | 33.93 USD | 1.1150 | 448 € | +23.52% |
| Q4 2019 | SELL | MELI | US | 0.9725 | 521.52 USD | 1.1150 | 455 € | -16.65% |

### 2020 (9 buys, 8 sells, 14.865 € total volume — net annual return **+151.72%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2020 | BUY | AMD | US | 4.7042 | 47.00 USD | 1.1093 | 199 € |  |
| Q1 2020 | BUY | TER | US | 10.5519 | 65.99 USD | 1.1093 | 628 € |  |
| Q1 2020 | SELL | KLAC | US | 2.4799 | 165.74 USD | 1.1093 | 371 € | -1.45% |
| Q1 2020 | SELL | PDD | US | 14.3782 | 35.22 USD | 1.1093 | 456 € | -13.40% |
| Q2 2020 | BUY | PDD | US | 16.2525 | 47.44 USD | 1.0955 | 704 € |  |
| Q2 2020 | BUY | TSLA | US | 15.2658 | 52.13 USD | 1.0955 | 726 € |  |
| Q2 2020 | SELL | ARWR | US | 26.3407 | 34.43 USD | 1.0955 | 828 € | +154.72% |
| Q2 2020 | SELL | TER | US | 10.5519 | 62.54 USD | 1.0955 | 602 € | -4.03% |
| Q3 2020 | BUY | NVDA | US | 111.5522 | 10.61 USD | 1.1774 | 1.005 € |  |
| Q3 2020 | BUY | SLR | IBEX | 72.3237 | 12.83 EUR |  | 928 € |  |
| Q3 2020 | BUY | VICR | US | 14.5277 | 81.47 USD | 1.1774 | 1.005 € |  |
| Q3 2020 | SELL | AMD | US | 4.7042 | 77.43 USD | 1.1774 | 309 € | +55.22% |
| Q3 2020 | SELL | ENPH | US | 51.4426 | 60.36 USD | 1.1774 | 2.637 € | +711.46% |
| Q4 2020 | BUY | BE | US | 106.3401 | 12.64 USD | 1.1647 | 1.154 € |  |
| Q4 2020 | BUY | ENPH | US | 12.8552 | 98.09 USD | 1.1647 | 1.083 € |  |
| Q4 2020 | SELL | PDD | US | 16.2525 | 89.98 USD | 1.1647 | 1.256 € | +78.40% |
| Q4 2020 | SELL | VICR | US | 14.5277 | 78.00 USD | 1.1647 | 973 € | -3.22% |

### 2021 (11 buys, 11 sells, 37.046 € total volume — net annual return **+0.22%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2021 | BUY | FDR | IBEX | 56.2226 | 19.80 EUR |  | 1.113 € |  |
| Q1 2021 | BUY | PDD | US | 13.9429 | 165.71 USD | 1.2136 | 1.904 € |  |
| Q1 2021 | BUY | SITM | US | 18.9306 | 122.05 USD | 1.2136 | 1.904 € |  |
| Q1 2021 | SELL | BE | US | 106.3401 | 34.91 USD | 1.2136 | 3.059 € | +165.06% |
| Q1 2021 | SELL | CLNX | IBEX | 14.9249 | 44.75 EUR |  | 668 € | +63.38% |
| Q1 2021 | SELL | NVDA | US | 111.5522 | 12.99 USD | 1.2136 | 1.194 € | +18.78% |
| Q2 2021 | BUY | GSAT | US | 106.2406 | 19.05 USD | 1.2018 | 1.684 € |  |
| Q2 2021 | BUY | HUT | US | 74.2710 | 27.25 USD | 1.2018 | 1.684 € |  |
| Q2 2021 | BUY | MTS | IBEX | 37.5115 | 24.23 EUR |  | 909 € |  |
| Q2 2021 | SELL | ENPH | US | 12.8552 | 139.25 USD | 1.2018 | 1.490 € | +37.58% |
| Q2 2021 | SELL | PDD | US | 13.9429 | 133.93 USD | 1.2018 | 1.554 € | -18.38% |
| Q2 2021 | SELL | SLR | IBEX | 72.3237 | 17.05 EUR |  | 1.233 € | +32.93% |
| Q3 2021 | BUY | MOD | US | 132.1653 | 16.73 USD | 1.1870 | 1.863 € |  |
| Q3 2021 | BUY | MP | US | 58.7753 | 37.62 USD | 1.1870 | 1.863 € |  |
| Q3 2021 | SELL | SITM | US | 18.9306 | 135.64 USD | 1.1870 | 2.163 € | +13.63% |
| Q3 2021 | SELL | TSLA | US | 15.2658 | 229.07 USD | 1.1870 | 2.946 € | +305.55% |
| Q4 2021 | BUY | BBVA | IBEX | 207.2488 | 6.06 EUR |  | 1.256 € |  |
| Q4 2021 | BUY | SAB | IBEX | 2993.8686 | 0.70 EUR |  | 2.085 € |  |
| Q4 2021 | BUY | SITM | US | 9.8579 | 264.89 USD | 1.1561 | 2.259 € |  |
| Q4 2021 | SELL | FDR | IBEX | 56.2226 | 33.05 EUR |  | 1.858 € | +66.92% |
| Q4 2021 | SELL | MOD | US | 132.1653 | 11.00 USD | 1.1561 | 1.258 € | -32.49% |
| Q4 2021 | SELL | MTS | IBEX | 37.5115 | 29.34 EUR |  | 1.101 € | +21.11% |

### 2022 (16 buys, 16 sells, 50.973 € total volume — net annual return **-16.75%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2022 | BUY | CYTK | US | 59.6320 | 33.19 USD | 1.1233 | 1.762 € |  |
| Q1 2022 | BUY | FDR | IBEX | 57.8792 | 28.10 EUR |  | 1.626 € |  |
| Q1 2022 | BUY | NVDA | US | 80.8161 | 24.49 USD | 1.1233 | 1.762 € |  |
| Q1 2022 | BUY | ROVI | IBEX | 24.8686 | 65.40 EUR |  | 1.626 € |  |
| Q1 2022 | SELL | BBVA | IBEX | 207.2488 | 5.63 EUR |  | 1.168 € | -7.06% |
| Q1 2022 | SELL | GSAT | US | 106.2406 | 16.05 USD | 1.1233 | 1.518 € | -9.86% |
| Q1 2022 | SELL | MP | US | 58.7753 | 39.94 USD | 1.1233 | 2.090 € | +12.19% |
| Q1 2022 | SELL | SAB | IBEX | 2993.8686 | 0.69 EUR |  | 2.058 € | -1.29% |
| Q2 2022 | BUY | COP | US | 17.3915 | 95.52 USD | 1.0541 | 1.576 € |  |
| Q2 2022 | BUY | MP | US | 43.6707 | 38.04 USD | 1.0541 | 1.576 € |  |
| Q2 2022 | BUY | SAB | IBEX | 1955.3040 | 0.74 EUR |  | 1.455 € |  |
| Q2 2022 | SELL | CYTK | US | 59.6320 | 39.87 USD | 1.0541 | 2.256 € | +28.01% |
| Q2 2022 | SELL | FDR | IBEX | 57.8792 | 26.12 EUR |  | 1.512 € | -7.05% |
| Q2 2022 | SELL | HUT | US | 74.2710 | 17.80 USD | 1.0541 | 1.254 € | -25.53% |
| Q3 2022 | BUY | ANA | IBEX | 6.9427 | 200.60 EUR |  | 1.393 € |  |
| Q3 2022 | BUY | CVX | US | 9.4130 | 163.78 USD | 1.0218 | 1.509 € |  |
| Q3 2022 | BUY | EOG | US | 14.5152 | 106.21 USD | 1.0218 | 1.509 € |  |
| Q3 2022 | BUY | REP | IBEX | 114.8625 | 12.12 EUR |  | 1.393 € |  |
| Q3 2022 | BUY | XOM | US | 15.9049 | 96.93 USD | 1.0218 | 1.509 € |  |
| Q3 2022 | SELL | MP | US | 43.6707 | 33.57 USD | 1.0218 | 1.435 € | -8.96% |
| Q3 2022 | SELL | NVDA | US | 80.8161 | 18.16 USD | 1.0218 | 1.436 € | -18.48% |
| Q3 2022 | SELL | ROVI | IBEX | 24.8686 | 51.00 EUR |  | 1.268 € | -22.02% |
| Q3 2022 | SELL | SAB | IBEX | 1955.3040 | 0.62 EUR |  | 1.221 € | -16.05% |
| Q3 2022 | SELL | SITM | US | 9.8579 | 185.98 USD | 1.0218 | 1.794 € | -20.56% |
| Q4 2022 | BUY | ANE | IBEX | 40.8252 | 39.76 EUR |  | 1.623 € |  |
| Q4 2022 | BUY | CABK | IBEX | 484.1067 | 3.35 EUR |  | 1.623 € |  |
| Q4 2022 | BUY | CYTK | US | 39.8054 | 43.66 USD | 0.9883 | 1.758 € |  |
| Q4 2022 | BUY | ON | US | 28.2908 | 61.43 USD | 0.9883 | 1.758 € |  |
| Q4 2022 | SELL | ANA | IBEX | 6.9427 | 182.10 EUR |  | 1.264 € | -9.22% |
| Q4 2022 | SELL | CVX | US | 9.4130 | 180.90 USD | 0.9883 | 1.723 € | +14.20% |
| Q4 2022 | SELL | EOG | US | 14.5152 | 131.99 USD | 0.9883 | 1.939 € | +28.49% |
| Q4 2022 | SELL | REP | IBEX | 114.8625 | 13.74 EUR |  | 1.579 € | +13.36% |

### 2023 (16 buys, 16 sells, 57.804 € total volume — net annual return **+100.95%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2023 | BUY | ENPH | US | 8.5123 | 221.38 USD | 1.0862 | 1.735 € |  |
| Q1 2023 | BUY | LLY | US | 5.4757 | 344.15 USD | 1.0862 | 1.735 € |  |
| Q1 2023 | BUY | MOD | US | 78.8802 | 23.89 USD | 1.0862 | 1.735 € |  |
| Q1 2023 | BUY | REP | IBEX | 106.1262 | 15.09 EUR |  | 1.601 € |  |
| Q1 2023 | BUY | SANM | US | 30.9281 | 60.93 USD | 1.0862 | 1.735 € |  |
| Q1 2023 | SELL | CABK | IBEX | 484.1067 | 4.07 EUR |  | 1.969 € | +21.29% |
| Q1 2023 | SELL | COP | US | 17.3915 | 121.87 USD | 1.0862 | 1.951 € | +23.82% |
| Q1 2023 | SELL | CYTK | US | 39.8054 | 42.48 USD | 1.0862 | 1.557 € | -11.47% |
| Q1 2023 | SELL | ON | US | 28.2908 | 73.45 USD | 1.0862 | 1.913 € | +8.79% |
| Q1 2023 | SELL | XOM | US | 15.9049 | 116.01 USD | 1.0862 | 1.699 € | +12.59% |
| Q2 2023 | BUY | ITX | IBEX | 45.9615 | 31.16 EUR |  | 1.432 € |  |
| Q2 2023 | BUY | NFLX | US | 51.8267 | 32.99 USD | 1.1020 | 1.552 € |  |
| Q2 2023 | BUY | PDD | US | 25.0882 | 68.15 USD | 1.1020 | 1.552 € |  |
| Q2 2023 | BUY | POWL | US | 128.0721 | 13.35 USD | 1.1020 | 1.552 € |  |
| Q2 2023 | BUY | SAB | IBEX | 1515.8360 | 0.94 EUR |  | 1.432 € |  |
| Q2 2023 | SELL | ANE | IBEX | 40.8252 | 32.56 EUR |  | 1.329 € | -18.11% |
| Q2 2023 | SELL | ENPH | US | 8.5123 | 164.20 USD | 1.1020 | 1.268 € | -26.89% |
| Q2 2023 | SELL | LLY | US | 5.4757 | 395.86 USD | 1.1020 | 1.967 € | +13.38% |
| Q2 2023 | SELL | REP | IBEX | 106.1262 | 13.35 EUR |  | 1.416 € | -11.56% |
| Q2 2023 | SELL | SANM | US | 30.9281 | 52.26 USD | 1.1020 | 1.467 € | -15.46% |
| Q3 2023 | BUY | AAOI | US | 344.1285 | 6.75 USD | 1.0993 | 2.113 € |  |
| Q3 2023 | BUY | BBVA | IBEX | 270.5271 | 7.21 EUR |  | 1.950 € |  |
| Q3 2023 | BUY | NVDA | US | 49.7083 | 46.73 USD | 1.0993 | 2.113 € |  |
| Q3 2023 | SELL | ITX | IBEX | 45.9615 | 34.81 EUR |  | 1.600 € | +11.71% |
| Q3 2023 | SELL | NFLX | US | 51.8267 | 43.90 USD | 1.0993 | 2.070 € | +33.40% |
| Q3 2023 | SELL | PDD | US | 25.0882 | 89.82 USD | 1.0993 | 2.050 € | +32.12% |
| Q4 2023 | BUY | IDR | IBEX | 161.1212 | 13.25 EUR |  | 2.135 € |  |
| Q4 2023 | BUY | ITX | IBEX | 65.5870 | 32.55 EUR |  | 2.135 € |  |
| Q4 2023 | BUY | META | US | 8.1189 | 301.27 USD | 1.0576 | 2.313 € |  |
| Q4 2023 | SELL | BBVA | IBEX | 270.5271 | 7.42 EUR |  | 2.008 € | +2.94% |
| Q4 2023 | SELL | MOD | US | 78.8802 | 39.50 USD | 1.0576 | 2.946 € | +69.81% |
| Q4 2023 | SELL | SAB | IBEX | 1515.8360 | 1.17 EUR |  | 1.775 € | +23.94% |

### 2024 (12 buys, 12 sells, 91.500 € total volume — net annual return **+47.44%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2024 | BUY | ACS | IBEX | 85.7576 | 36.59 EUR |  | 3.138 € |  |
| Q1 2024 | BUY | MOD | US | 53.2168 | 69.09 USD | 1.0816 | 3.399 € |  |
| Q1 2024 | BUY | ROVI | IBEX | 48.9910 | 64.05 EUR |  | 3.138 € |  |
| Q1 2024 | BUY | VRT | US | 65.2716 | 56.33 USD | 1.0816 | 3.399 € |  |
| Q1 2024 | SELL | IDR | IBEX | 161.1212 | 16.47 EUR |  | 2.654 € | +24.30% |
| Q1 2024 | SELL | ITX | IBEX | 65.5870 | 39.71 EUR |  | 2.604 € | +22.00% |
| Q1 2024 | SELL | META | US | 8.1189 | 390.14 USD | 1.0816 | 2.929 € | +26.62% |
| Q1 2024 | SELL | POWL | US | 128.0721 | 39.51 USD | 1.0816 | 4.678 € | +201.54% |
| Q2 2024 | BUY | BBVA | IBEX | 316.2893 | 10.18 EUR |  | 3.218 € |  |
| Q2 2024 | BUY | POWL | US | 90.4668 | 47.67 USD | 1.0665 | 4.044 € |  |
| Q2 2024 | SELL | ACS | IBEX | 85.7576 | 37.58 EUR |  | 3.223 € | +2.71% |
| Q2 2024 | SELL | NVDA | US | 49.7083 | 86.40 USD | 1.0665 | 4.027 € | +90.58% |
| Q3 2024 | BUY | ASTS | US | 222.0990 | 20.68 USD | 1.0825 | 4.243 € |  |
| Q3 2024 | BUY | NVDA | US | 39.2498 | 117.02 USD | 1.0825 | 4.243 € |  |
| Q3 2024 | BUY | SAB | IBEX | 1401.0014 | 1.95 EUR |  | 2.735 € |  |
| Q3 2024 | SELL | AAOI | US | 344.1285 | 9.55 USD | 1.0825 | 3.036 € | +43.68% |
| Q3 2024 | SELL | BBVA | IBEX | 316.2893 | 9.70 EUR |  | 3.069 € | -4.63% |
| Q3 2024 | SELL | POWL | US | 90.4668 | 61.21 USD | 1.0825 | 5.115 € | +26.51% |
| Q4 2024 | BUY | IESC | US | 22.8826 | 218.66 USD | 1.0883 | 4.598 € |  |
| Q4 2024 | BUY | ITX | IBEX | 81.1451 | 52.30 EUR |  | 4.244 € |  |
| Q4 2024 | BUY | SMTC | US | 113.2272 | 44.19 USD | 1.0883 | 4.598 € |  |
| Q4 2024 | SELL | NVDA | US | 39.2498 | 132.76 USD | 1.0883 | 4.788 € | +12.85% |
| Q4 2024 | SELL | ROVI | IBEX | 48.9910 | 78.10 EUR |  | 3.826 € | +21.94% |
| Q4 2024 | SELL | VRT | US | 65.2716 | 109.29 USD | 1.0883 | 6.555 € | +92.82% |

### 2025 (8 buys, 8 sells, 102.415 € total volume — net annual return **+92.18%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2025 | BUY | HOOD | US | 100.3206 | 51.95 USD | 1.0362 | 5.030 € |  |
| Q1 2025 | BUY | IAG | IBEX | 1149.7508 | 4.04 EUR |  | 4.643 € |  |
| Q1 2025 | BUY | PLTR | US | 63.1792 | 82.49 USD | 1.0362 | 5.030 € |  |
| Q1 2025 | BUY | RKLB | US | 179.4030 | 29.05 USD | 1.0362 | 5.030 € |  |
| Q1 2025 | SELL | IESC | US | 22.8826 | 221.28 USD | 1.0362 | 4.887 € | +6.29% |
| Q1 2025 | SELL | ITX | IBEX | 81.1451 | 52.72 EUR |  | 4.278 € | +0.80% |
| Q1 2025 | SELL | MOD | US | 53.2168 | 101.45 USD | 1.0362 | 5.210 € | +53.27% |
| Q1 2025 | SELL | SMTC | US | 113.2272 | 66.96 USD | 1.0362 | 7.317 € | +59.15% |
| Q2 2025 | BUY | IDR | IBEX | 159.3263 | 28.02 EUR |  | 4.464 € |  |
| Q2 2025 | SELL | SAB | IBEX | 1401.0014 | 2.56 EUR |  | 3.592 € | +31.35% |
| Q3 2025 | BUY | AGX | US | 37.1438 | 244.98 USD | 1.1416 | 7.971 € |  |
| Q3 2025 | SELL | ASTS | US | 222.0990 | 53.17 USD | 1.1416 | 10.344 € | +143.80% |
| Q4 2025 | BUY | BE | US | 87.5279 | 132.16 USD | 1.1536 | 10.027 € |  |
| Q4 2025 | BUY | UNI | IBEX | 3955.6074 | 2.34 EUR |  | 9.256 € |  |
| Q4 2025 | SELL | AGX | US | 37.1438 | 306.21 USD | 1.1536 | 9.859 € | +23.69% |
| Q4 2025 | SELL | IAG | IBEX | 1149.7508 | 4.76 EUR |  | 5.477 € | +17.98% |

## Important notes

- **Real prices**: daily closes from `data/monthly-historic-prices.csv`, resampled to month-end. Covers all IBEX 35 plus the full US large/mid-cap universe defined in `src/universe.py`.
- **Real EUR/USD historical rates** are used per rebalance day. The rate moved from ~1.15 in 2019 to parity (~1.00) in 2022 and back to ~1.15 in 2025.
- **No commissions are modeled** in the backtest. Real execution will subtract 0.1-0.3% per year of CAGR depending on broker tier.
- **Survivorship bias**: the universe contains stocks that exist today. Stocks that delisted are not represented.
- **Composition timing bias**: some stocks IPO'd within the backtest window (PLTR 2020, NU 2021, ARM 2023, SNDK relisted 2025). They enter the universe as their data becomes available.

A real-money implementation should expect **5-15 percentage points lower CAGR** than this backtest, due to commissions, execution timing, slippage, and the fact that the future regime will not be 2019-2025.
