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
| Final capital | **46.916 €** |
| Total return | +2245.78% |
| **CAGR (net of taxes)** | **+56.95%** |
| Annualized volatility | 44.61% |
| **Sharpe ratio** | **1.24** |
| **Max drawdown** | **-44.26%** |
| Total taxes | 10.390 € |
| Total trades | 158 |
| Rebalances | 28 |

## Executive dashboard

![Backtest Dashboard](backtest-dashboard.png)

## The 2021-2022 drawdown: what really happened

The strategy reached a peak in **October 2021** at **12.238,13 €**, then suffered a sustained decline reaching its lowest point in **June 2022** at **6.821,91 €** — a drawdown of **-44.26%** from the previous peak.

From peak to trough took **8 months**. The portfolio then took another **14 months** to reach the previous peak again, finally crossing it in **August 2023**. Total time underwater: **~22 months**.

This is the most important number to internalize before trusting the strategy. The +56.95% headline CAGR is real, but reaching it required holding through almost two years of seeing the portfolio worth less than its previous best. Anyone who panicked and exited near the trough crystallized a -44% loss; those who held saw the portfolio continue to **46.916 €** by the end of the backtest.

## Year-by-year breakdown

| Year | Capital start | Capital end (net) | Net return | Tax paid | Realized gain |
|------|--------------:|------------------:|-----------:|---------:|--------------:|
| 2019 | 2.000 € | 3.985 € | **+99.27%** | 0 € | -38 € |
| 2020 | 3.985 € | 10.038 € | **+151.88%** | 677 € | 3.564 € |
| 2021 | 10.038 € | 9.693 € | **-3.44%** | 858 € | 4.514 € |
| 2022 | 9.693 € | 8.016 € | **-17.30%** | 0 € | -784 € |
| 2023 | 8.016 € | 16.067 € | **+100.44%** | 476 € | 2.503 € |
| 2024 | 16.067 € | 24.112 € | **+50.07%** | 2.454 € | 12.259 € |
| 2025 | 24.112 € | 46.916 € | **+94.57%** | 2.963 € | 14.679 € |

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
| 2019-08 | 3.564,57 € | +6.14% | 0,00% |
| 2019-09 | 3.023,00 € | -15.19% | -15.19% |
| 2019-10 | 3.154,49 € | +4.35% | -11.50% |
| 2019-11 | 4.013,30 € | +27.23% | 0,00% |
| 2019-12 | 3.985,35 € | -0.70% | -0.70% |
| 2020-01 | 3.692,66 € | -7.34% | -7.99% |
| 2020-02 | 4.287,26 € | +16.10% | 0,00% |
| 2020-03 | 3.308,35 € | -22.83% | -22.83% |
| 2020-04 | 4.315,72 € | +30.45% | 0,00% |
| 2020-05 | 5.135,69 € | +19.00% | 0,00% |
| 2020-06 | 5.061,56 € | -1.44% | -1.44% |
| 2020-07 | 6.061,95 € | +19.76% | 0,00% |
| 2020-08 | 7.458,09 € | +23.03% | 0,00% |
| 2020-09 | 6.900,34 € | -7.48% | -7.48% |
| 2020-10 | 6.926,82 € | +0.38% | -7.12% |
| 2020-11 | 9.299,27 € | +34.25% | 0,00% |
| 2020-12 | 10.038,18 € | +7.95% | 0,00% |
| 2021-01 | 10.881,33 € | +8.40% | 0,00% |
| 2021-02 | 9.871,77 € | -9.28% | -9.28% |
| 2021-03 | 9.466,67 € | -4.10% | -13.00% |
| 2021-04 | 9.027,63 € | -4.64% | -17.04% |
| 2021-05 | 8.821,70 € | -2.28% | -18.93% |
| 2021-06 | 9.978,36 € | +13.11% | -8.30% |
| 2021-07 | 9.943,26 € | -0.35% | -8.62% |
| 2021-08 | 11.005,85 € | +10.69% | 0,00% |
| 2021-09 | 10.595,94 € | -3.72% | -3.72% |
| 2021-10 | 12.238,13 € | +15.50% | 0,00% |
| 2021-11 | 12.155,20 € | -0.68% | -0.68% |
| 2021-12 | 9.692,72 € | -20.26% | -20.80% |
| 2022-01 | 8.599,00 € | -11.28% | -29.74% |
| 2022-02 | 8.618,55 € | +0.23% | -29.58% |
| 2022-03 | 9.013,66 € | +4.58% | -26.35% |
| 2022-04 | 7.530,67 € | -16.45% | -38.47% |
| 2022-05 | 8.221,12 € | +9.17% | -32.82% |
| 2022-06 | 6.821,91 € | -17.02% | -44.26% |
| 2022-07 | 7.142,89 € | +4.71% | -41.63% |
| 2022-08 | 7.546,43 € | +5.65% | -38.34% |
| 2022-09 | 7.005,97 € | -7.16% | -42.75% |
| 2022-10 | 8.579,19 € | +22.46% | -29.90% |
| 2022-11 | 8.524,39 € | -0.64% | -30.35% |
| 2022-12 | 8.015,91 € | -5.97% | -34.50% |
| 2023-01 | 8.443,54 € | +5.33% | -31.01% |
| 2023-02 | 8.358,60 € | -1.01% | -31.70% |
| 2023-03 | 8.159,93 € | -2.38% | -33.32% |
| 2023-04 | 7.388,76 € | -9.45% | -39.63% |
| 2023-05 | 8.869,21 € | +20.04% | -27.53% |
| 2023-06 | 9.868,36 € | +11.27% | -19.36% |
| 2023-07 | 10.618,47 € | +7.60% | -13.23% |
| 2023-08 | 14.412,58 € | +35.73% | 0,00% |
| 2023-09 | 13.613,82 € | -5.54% | -5.54% |
| 2023-10 | 11.767,17 € | -13.56% | -18.35% |
| 2023-11 | 14.361,30 € | +22.05% | -0.36% |
| 2023-12 | 16.067,49 € | +11.88% | 0,00% |
| 2024-01 | 17.541,33 € | +9.17% | 0,00% |
| 2024-02 | 20.541,27 € | +17.10% | 0,00% |
| 2024-03 | 21.836,35 € | +6.30% | 0,00% |
| 2024-04 | 21.247,02 € | -2.70% | -2.70% |
| 2024-05 | 22.952,19 € | +8.03% | 0,00% |
| 2024-06 | 20.849,14 € | -9.16% | -9.16% |
| 2024-07 | 22.532,62 € | +8.07% | -1.83% |
| 2024-08 | 23.814,46 € | +5.69% | 0,00% |
| 2024-09 | 24.228,51 € | +1.74% | 0,00% |
| 2024-10 | 24.792,33 € | +2.33% | 0,00% |
| 2024-11 | 30.050,34 € | +21.21% | 0,00% |
| 2024-12 | 24.111,90 € | -19.76% | -19.76% |
| 2025-01 | 25.318,09 € | +5.00% | -15.75% |
| 2025-02 | 26.320,73 € | +3.96% | -12.41% |
| 2025-03 | 22.085,55 € | -16.09% | -26.50% |
| 2025-04 | 24.426,46 € | +10.60% | -18.71% |
| 2025-05 | 29.461,52 € | +20.61% | -1.96% |
| 2025-06 | 36.888,30 € | +25.21% | 0,00% |
| 2025-07 | 42.869,54 € | +16.21% | 0,00% |
| 2025-08 | 41.733,86 € | -2.65% | -2.65% |
| 2025-09 | 47.918,47 € | +14.82% | 0,00% |
| 2025-10 | 55.068,88 € | +14.92% | 0,00% |
| 2025-11 | 47.300,94 € | -14.11% | -14.11% |
| 2025-12 | 46.915,68 € | -0.81% | -14.81% |

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
| ITX | 3 |
| SLR | 2 |
| ANA | 2 |
| FDR | 2 |
| ROVI | 2 |
| REP | 2 |
| IDR | 2 |
| NTGY | 1 |
| MTS | 1 |

## Detailed quarterly trades

One row per executed buy/sell. Sells show realized return at exit; buys leave the return column empty (the return crystallizes when sold).

### 2019 (12 buys, 8 sells, 7.350 € total volume — net annual return **+99.27%**)

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
| Q3 2019 | BUY | MELI | US | 0.9725 | 621.42 USD | 1.1074 | 546 € |  |
| Q3 2019 | SELL | ANA | IBEX | 3.2427 | 96.30 EUR |  | 312 € | -6.78% |
| Q3 2019 | SELL | LLY | US | 3.4773 | 108.95 USD | 1.1074 | 342 € | -5.73% |
| Q3 2019 | SELL | SLR | IBEX | 55.6586 | 5.38 EUR |  | 299 € | -0.28% |
| Q4 2019 | BUY | KLAC | US | 3.3812 | 169.04 USD | 1.1150 | 513 € |  |
| Q4 2019 | BUY | PDD | US | 13.9813 | 40.88 USD | 1.1150 | 513 € |  |
| Q4 2019 | SELL | AMD | US | 14.7296 | 33.93 USD | 1.1150 | 448 € | +23.52% |
| Q4 2019 | SELL | MELI | US | 0.9725 | 521.52 USD | 1.1150 | 455 € | -16.65% |

### 2020 (9 buys, 8 sells, 15.859 € total volume — net annual return **+151.88%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2020 | BUY | AMD | US | 14.1626 | 47.00 USD | 1.1093 | 600 € |  |
| Q1 2020 | BUY | TER | US | 10.0870 | 65.99 USD | 1.1093 | 600 € |  |
| Q1 2020 | SELL | KLAC | US | 3.3812 | 165.74 USD | 1.1093 | 505 € | -1.45% |
| Q1 2020 | SELL | PDD | US | 13.9813 | 35.22 USD | 1.1093 | 444 € | -13.40% |
| Q2 2020 | BUY | PDD | US | 16.1947 | 47.44 USD | 1.0955 | 701 € |  |
| Q2 2020 | BUY | TSLA | US | 14.7377 | 52.13 USD | 1.0955 | 701 € |  |
| Q2 2020 | SELL | ARWR | US | 26.3407 | 34.43 USD | 1.0955 | 828 € | +154.72% |
| Q2 2020 | SELL | TER | US | 10.0870 | 62.54 USD | 1.0955 | 576 € | -4.03% |
| Q3 2020 | BUY | NVDA | US | 109.3136 | 10.61 USD | 1.1774 | 985 € |  |
| Q3 2020 | BUY | SLR | IBEX | 70.8723 | 12.83 EUR |  | 909 € |  |
| Q3 2020 | BUY | VICR | US | 14.2361 | 81.47 USD | 1.1774 | 985 € |  |
| Q3 2020 | SELL | AMD | US | 14.1626 | 77.43 USD | 1.1774 | 931 € | +55.22% |
| Q3 2020 | SELL | ENPH | US | 51.4426 | 60.36 USD | 1.1774 | 2.637 € | +711.46% |
| Q4 2020 | BUY | BE | US | 103.7180 | 12.64 USD | 1.1647 | 1.126 € |  |
| Q4 2020 | BUY | ENPH | US | 13.3652 | 98.09 USD | 1.1647 | 1.126 € |  |
| Q4 2020 | SELL | PDD | US | 16.1947 | 89.98 USD | 1.1647 | 1.251 € | +78.40% |
| Q4 2020 | SELL | VICR | US | 14.2361 | 78.00 USD | 1.1647 | 953 € | -3.22% |

### 2021 (10 buys, 10 sells, 35.339 € total volume — net annual return **-3.44%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2021 | BUY | PDD | US | 13.7557 | 165.71 USD | 1.2136 | 1.878 € |  |
| Q1 2021 | BUY | SITM | US | 18.6764 | 122.05 USD | 1.2136 | 1.878 € |  |
| Q1 2021 | SELL | BE | US | 103.7180 | 34.91 USD | 1.2136 | 2.984 € | +165.06% |
| Q1 2021 | SELL | NVDA | US | 109.3136 | 12.99 USD | 1.2136 | 1.170 € | +18.78% |
| Q2 2021 | BUY | GSAT | US | 99.4898 | 19.05 USD | 1.2018 | 1.577 € |  |
| Q2 2021 | BUY | HUT | US | 69.5516 | 27.25 USD | 1.2018 | 1.577 € |  |
| Q2 2021 | BUY | MTS | IBEX | 60.0918 | 24.23 EUR |  | 1.456 € |  |
| Q2 2021 | SELL | ENPH | US | 13.3652 | 139.25 USD | 1.2018 | 1.549 € | +37.58% |
| Q2 2021 | SELL | PDD | US | 13.7557 | 133.93 USD | 1.2018 | 1.533 € | -18.38% |
| Q2 2021 | SELL | SLR | IBEX | 70.8723 | 17.05 EUR |  | 1.209 € | +32.93% |
| Q3 2021 | BUY | FDR | IBEX | 46.6492 | 34.15 EUR |  | 1.593 € |  |
| Q3 2021 | BUY | MOD | US | 122.4480 | 16.73 USD | 1.1870 | 1.726 € |  |
| Q3 2021 | BUY | MP | US | 54.4539 | 37.62 USD | 1.1870 | 1.726 € |  |
| Q3 2021 | SELL | SITM | US | 18.6764 | 135.64 USD | 1.1870 | 2.134 € | +13.63% |
| Q3 2021 | SELL | TSLA | US | 14.7377 | 229.07 USD | 1.1870 | 2.844 € | +305.55% |
| Q4 2021 | BUY | SAB | IBEX | 2781.8787 | 0.70 EUR |  | 1.937 € |  |
| Q4 2021 | BUY | SITM | US | 9.1599 | 264.89 USD | 1.1561 | 2.099 € |  |
| Q4 2021 | SELL | FDR | IBEX | 46.6492 | 33.05 EUR |  | 1.542 € | -3.22% |
| Q4 2021 | SELL | MOD | US | 122.4480 | 11.00 USD | 1.1561 | 1.165 € | -32.49% |
| Q4 2021 | SELL | MTS | IBEX | 60.0918 | 29.34 EUR |  | 1.763 € | +21.11% |

### 2022 (16 buys, 15 sells, 46.517 € total volume — net annual return **-17.30%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2022 | BUY | CYTK | US | 55.7336 | 33.19 USD | 1.1233 | 1.647 € |  |
| Q1 2022 | BUY | FDR | IBEX | 54.0954 | 28.10 EUR |  | 1.520 € |  |
| Q1 2022 | BUY | NVDA | US | 75.5328 | 24.49 USD | 1.1233 | 1.647 € |  |
| Q1 2022 | BUY | ROVI | IBEX | 23.2428 | 65.40 EUR |  | 1.520 € |  |
| Q1 2022 | SELL | GSAT | US | 99.4898 | 16.05 USD | 1.1233 | 1.422 € | -9.86% |
| Q1 2022 | SELL | MP | US | 54.4539 | 39.94 USD | 1.1233 | 1.936 € | +12.19% |
| Q1 2022 | SELL | SAB | IBEX | 2781.8787 | 0.69 EUR |  | 1.912 € | -1.29% |
| Q2 2022 | BUY | COP | US | 16.2568 | 95.52 USD | 1.0541 | 1.473 € |  |
| Q2 2022 | BUY | MP | US | 40.8214 | 38.04 USD | 1.0541 | 1.473 € |  |
| Q2 2022 | BUY | SAB | IBEX | 1827.7297 | 0.74 EUR |  | 1.360 € |  |
| Q2 2022 | SELL | CYTK | US | 55.7336 | 39.87 USD | 1.0541 | 2.108 € | +28.01% |
| Q2 2022 | SELL | FDR | IBEX | 54.0954 | 26.12 EUR |  | 1.413 € | -7.05% |
| Q2 2022 | SELL | HUT | US | 69.5516 | 17.80 USD | 1.0541 | 1.174 € | -25.53% |
| Q3 2022 | BUY | ANA | IBEX | 6.4889 | 200.60 EUR |  | 1.302 € |  |
| Q3 2022 | BUY | CVX | US | 8.7976 | 163.78 USD | 1.0218 | 1.410 € |  |
| Q3 2022 | BUY | EOG | US | 13.5663 | 106.21 USD | 1.0218 | 1.410 € |  |
| Q3 2022 | BUY | REP | IBEX | 107.3538 | 12.12 EUR |  | 1.302 € |  |
| Q3 2022 | BUY | XOM | US | 14.8651 | 96.93 USD | 1.0218 | 1.410 € |  |
| Q3 2022 | SELL | MP | US | 40.8214 | 33.57 USD | 1.0218 | 1.341 € | -8.96% |
| Q3 2022 | SELL | NVDA | US | 75.5328 | 18.16 USD | 1.0218 | 1.342 € | -18.48% |
| Q3 2022 | SELL | ROVI | IBEX | 23.2428 | 51.00 EUR |  | 1.185 € | -22.02% |
| Q3 2022 | SELL | SAB | IBEX | 1827.7297 | 0.62 EUR |  | 1.142 € | -16.05% |
| Q3 2022 | SELL | SITM | US | 9.1599 | 185.98 USD | 1.0218 | 1.667 € | -20.56% |
| Q4 2022 | BUY | ANE | IBEX | 38.1567 | 39.76 EUR |  | 1.517 € |  |
| Q4 2022 | BUY | CABK | IBEX | 452.4633 | 3.35 EUR |  | 1.517 € |  |
| Q4 2022 | BUY | CYTK | US | 37.2035 | 43.66 USD | 0.9883 | 1.644 € |  |
| Q4 2022 | BUY | ON | US | 26.4416 | 61.43 USD | 0.9883 | 1.644 € |  |
| Q4 2022 | SELL | ANA | IBEX | 6.4889 | 182.10 EUR |  | 1.182 € | -9.22% |
| Q4 2022 | SELL | CVX | US | 8.7976 | 180.90 USD | 0.9883 | 1.610 € | +14.20% |
| Q4 2022 | SELL | EOG | US | 13.5663 | 131.99 USD | 0.9883 | 1.812 € | +28.49% |
| Q4 2022 | SELL | REP | IBEX | 107.3538 | 13.74 EUR |  | 1.476 € | +13.36% |

### 2023 (16 buys, 16 sells, 54.025 € total volume — net annual return **+100.44%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2023 | BUY | ENPH | US | 7.9558 | 221.38 USD | 1.0862 | 1.621 € |  |
| Q1 2023 | BUY | LLY | US | 5.1177 | 344.15 USD | 1.0862 | 1.621 € |  |
| Q1 2023 | BUY | MOD | US | 73.7240 | 23.89 USD | 1.0862 | 1.621 € |  |
| Q1 2023 | BUY | REP | IBEX | 99.1890 | 15.09 EUR |  | 1.497 € |  |
| Q1 2023 | BUY | SANM | US | 28.9064 | 60.93 USD | 1.0862 | 1.621 € |  |
| Q1 2023 | SELL | CABK | IBEX | 452.4633 | 4.07 EUR |  | 1.840 € | +21.29% |
| Q1 2023 | SELL | COP | US | 16.2568 | 121.87 USD | 1.0862 | 1.824 € | +23.82% |
| Q1 2023 | SELL | CYTK | US | 37.2035 | 42.48 USD | 1.0862 | 1.455 € | -11.47% |
| Q1 2023 | SELL | ON | US | 26.4416 | 73.45 USD | 1.0862 | 1.788 € | +8.79% |
| Q1 2023 | SELL | XOM | US | 14.8651 | 116.01 USD | 1.0862 | 1.588 € | +12.59% |
| Q2 2023 | BUY | ITX | IBEX | 42.9572 | 31.16 EUR |  | 1.339 € |  |
| Q2 2023 | BUY | NFLX | US | 48.4389 | 32.99 USD | 1.1020 | 1.450 € |  |
| Q2 2023 | BUY | PDD | US | 23.4483 | 68.15 USD | 1.1020 | 1.450 € |  |
| Q2 2023 | BUY | POWL | US | 119.7003 | 13.35 USD | 1.1020 | 1.450 € |  |
| Q2 2023 | BUY | SAB | IBEX | 1416.7496 | 0.94 EUR |  | 1.339 € |  |
| Q2 2023 | SELL | ANE | IBEX | 38.1567 | 32.56 EUR |  | 1.242 € | -18.11% |
| Q2 2023 | SELL | ENPH | US | 7.9558 | 164.20 USD | 1.1020 | 1.185 € | -26.89% |
| Q2 2023 | SELL | LLY | US | 5.1177 | 395.86 USD | 1.1020 | 1.838 € | +13.38% |
| Q2 2023 | SELL | REP | IBEX | 99.1890 | 13.35 EUR |  | 1.324 € | -11.56% |
| Q2 2023 | SELL | SANM | US | 28.9064 | 52.26 USD | 1.1020 | 1.371 € | -15.46% |
| Q3 2023 | BUY | AAOI | US | 321.6336 | 6.75 USD | 1.0993 | 1.975 € |  |
| Q3 2023 | BUY | BBVA | IBEX | 252.8434 | 7.21 EUR |  | 1.823 € |  |
| Q3 2023 | BUY | NVDA | US | 46.4590 | 46.73 USD | 1.0993 | 1.975 € |  |
| Q3 2023 | SELL | ITX | IBEX | 42.9572 | 34.81 EUR |  | 1.495 € | +11.71% |
| Q3 2023 | SELL | NFLX | US | 48.4389 | 43.90 USD | 1.0993 | 1.934 € | +33.40% |
| Q3 2023 | SELL | PDD | US | 23.4483 | 89.82 USD | 1.0993 | 1.916 € | +32.12% |
| Q4 2023 | BUY | IDR | IBEX | 150.5891 | 13.25 EUR |  | 1.995 € |  |
| Q4 2023 | BUY | ITX | IBEX | 61.2997 | 32.55 EUR |  | 1.995 € |  |
| Q4 2023 | BUY | META | US | 7.5882 | 301.27 USD | 1.0576 | 2.162 € |  |
| Q4 2023 | SELL | BBVA | IBEX | 252.8434 | 7.42 EUR |  | 1.877 € | +2.94% |
| Q4 2023 | SELL | MOD | US | 73.7240 | 39.50 USD | 1.0576 | 2.754 € | +69.81% |
| Q4 2023 | SELL | SAB | IBEX | 1416.7496 | 1.17 EUR |  | 1.659 € | +23.94% |

### 2024 (11 buys, 11 sells, 81.349 € total volume — net annual return **+50.07%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2024 | BUY | ACS | IBEX | 80.1519 | 36.59 EUR |  | 2.933 € |  |
| Q1 2024 | BUY | MOD | US | 49.7381 | 69.09 USD | 1.0816 | 3.177 € |  |
| Q1 2024 | BUY | ROVI | IBEX | 45.7885 | 64.05 EUR |  | 2.933 € |  |
| Q1 2024 | BUY | VRT | US | 61.0049 | 56.33 USD | 1.0816 | 3.177 € |  |
| Q1 2024 | SELL | IDR | IBEX | 150.5891 | 16.47 EUR |  | 2.480 € | +24.30% |
| Q1 2024 | SELL | ITX | IBEX | 61.2997 | 39.71 EUR |  | 2.434 € | +22.00% |
| Q1 2024 | SELL | META | US | 7.5882 | 390.14 USD | 1.0816 | 2.737 € | +26.62% |
| Q1 2024 | SELL | POWL | US | 119.7003 | 39.51 USD | 1.0816 | 4.373 € | +201.54% |
| Q2 2024 | BUY | POWL | US | 84.5532 | 47.67 USD | 1.0665 | 3.779 € |  |
| Q2 2024 | SELL | ACS | IBEX | 80.1519 | 37.58 EUR |  | 3.012 € | +2.71% |
| Q2 2024 | SELL | NVDA | US | 46.4590 | 86.40 USD | 1.0665 | 3.764 € | +90.58% |
| Q3 2024 | BUY | ASTS | US | 208.7653 | 20.68 USD | 1.0825 | 3.988 € |  |
| Q3 2024 | BUY | NVDA | US | 36.8934 | 117.02 USD | 1.0825 | 3.988 € |  |
| Q3 2024 | SELL | AAOI | US | 321.6336 | 9.55 USD | 1.0825 | 2.838 € | +43.68% |
| Q3 2024 | SELL | POWL | US | 84.5532 | 61.21 USD | 1.0825 | 4.781 € | +26.51% |
| Q4 2024 | BUY | IESC | US | 21.6776 | 218.66 USD | 1.0883 | 4.355 € |  |
| Q4 2024 | BUY | ITX | IBEX | 76.8720 | 52.30 EUR |  | 4.020 € |  |
| Q4 2024 | BUY | SAB | IBEX | 2247.9202 | 1.79 EUR |  | 4.020 € |  |
| Q4 2024 | BUY | SMTC | US | 107.2646 | 44.19 USD | 1.0883 | 4.355 € |  |
| Q4 2024 | SELL | NVDA | US | 36.8934 | 132.76 USD | 1.0883 | 4.501 € | +12.85% |
| Q4 2024 | SELL | ROVI | IBEX | 45.7885 | 78.10 EUR |  | 3.576 € | +21.94% |
| Q4 2024 | SELL | VRT | US | 61.0049 | 109.29 USD | 1.0883 | 6.126 € | +92.82% |

### 2025 (8 buys, 8 sells, 100.371 € total volume — net annual return **+94.57%**)

| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |
|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|
| Q1 2025 | BUY | HOOD | US | 96.5335 | 51.95 USD | 1.0362 | 4.840 € |  |
| Q1 2025 | BUY | IAG | IBEX | 1106.3476 | 4.04 EUR |  | 4.467 € |  |
| Q1 2025 | BUY | PLTR | US | 60.7942 | 82.49 USD | 1.0362 | 4.840 € |  |
| Q1 2025 | BUY | RKLB | US | 172.6305 | 29.05 USD | 1.0362 | 4.840 € |  |
| Q1 2025 | SELL | IESC | US | 21.6776 | 221.28 USD | 1.0362 | 4.629 € | +6.29% |
| Q1 2025 | SELL | ITX | IBEX | 76.8720 | 52.72 EUR |  | 4.053 € | +0.80% |
| Q1 2025 | SELL | MOD | US | 49.7381 | 101.45 USD | 1.0362 | 4.870 € | +53.27% |
| Q1 2025 | SELL | SMTC | US | 107.2646 | 66.96 USD | 1.0362 | 6.932 € | +59.15% |
| Q2 2025 | BUY | IDR | IBEX | 154.6641 | 28.02 EUR |  | 4.334 € |  |
| Q2 2025 | SELL | SAB | IBEX | 2247.9202 | 2.56 EUR |  | 5.764 € | +43.36% |
| Q3 2025 | BUY | AGX | US | 35.8437 | 244.98 USD | 1.1416 | 7.692 € |  |
| Q3 2025 | SELL | ASTS | US | 208.7653 | 53.17 USD | 1.1416 | 9.723 € | +143.80% |
| Q4 2025 | BUY | BE | US | 84.4445 | 132.16 USD | 1.1536 | 9.674 € |  |
| Q4 2025 | BUY | UNI | IBEX | 3816.2608 | 2.34 EUR |  | 8.930 € |  |
| Q4 2025 | SELL | AGX | US | 35.8437 | 306.21 USD | 1.1536 | 9.514 € | +23.69% |
| Q4 2025 | SELL | IAG | IBEX | 1106.3476 | 4.76 EUR |  | 5.271 € | +17.98% |

## Important notes

- **Real prices**: daily closes from `data/monthly-historic-prices.csv`, resampled to month-end. Covers all IBEX 35 plus the full US large/mid-cap universe defined in `src/universe.py`.
- **Real EUR/USD historical rates** are used per rebalance day. The rate moved from ~1.15 in 2019 to parity (~1.00) in 2022 and back to ~1.15 in 2025.
- **No commissions are modeled** in the backtest. Real execution will subtract 0.1-0.3% per year of CAGR depending on broker tier.
- **Survivorship bias**: the universe contains stocks that exist today. Stocks that delisted are not represented.
- **Composition timing bias**: some stocks IPO'd within the backtest window (PLTR 2020, NU 2021, ARM 2023, SNDK relisted 2025). They enter the universe as their data becomes available.

A real-money implementation should expect **5-15 percentage points lower CAGR** than this backtest, due to commissions, execution timing, slippage, and the fact that the future regime will not be 2019-2025.
