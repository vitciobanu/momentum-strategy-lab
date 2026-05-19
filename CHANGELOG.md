# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.3.1] - 2026-05-19

**Fixed yearly starting capital**

### Fixed
- `src/backtest.py`: yearly tax payments are now correctly deducted from
  the start-of-next-year capital. Previously the running portfolio value
  did not propagate the tax subtraction, distorting yearly returns in
  years that followed a tax payment (2021, 2024, 2025). Global metrics
  (CAGR, Sharpe, Max DD) are unchanged.

---

## [1.3.0] - 2026-05-18

**Automated rebalance bookkeeping**

### Added
- `scripts/append-rebalance.py`: interactive helper that records executed
  trades into `data/portfolio.json` and `data/history.json`, auto-computing
  EUR values from native IBKR data (shares, USD price, USD commission, exec
  EUR/USD rate per order). No more manual math. Includes cash-math
  validation (refuses to save if off by more than 0.50 EUR), three safety
  layers against accidental double-execution, and `.bak` backups before
  overwriting. `--dry-run` flag available for testing.
- `data/history.json` now uses two entry types per rebalance:
  - `"type": "PLAN"` — written by `src/rebalance.py` with momentum values
    and planned orders.
  - `"type": "EXECUTION"` — written by `scripts/append-rebalance.py` after
    orders are filled, with real fill prices, the EUR/USD rates IBKR
    applied per US order, and real commissions in both currencies.
- `src/cagr.py`: money-weighted (XIRR) and time-weighted (TWR) annualized
  returns. Used by `src/rebalance.py` to display proper return metrics
  after each rebalance, especially relevant when capital is added or
  withdrawn mid-stream. Has no external dependencies (custom
  Newton-Raphson + bisection root finder).
- `tests/test_cagr.py`: 8 unit tests covering XIRR / TWR with edge cases
  (no growth, negative returns, mid-stream injection, withdrawal,
  invalid inputs).
- 41 momentum mid-caps + Colgate-Palmolive added to the US universe
  (now 157 stocks). New tickers include AEIS, AGX, ALAB, AMAT, AMKR,
  ARWR, ASTS, CIEN, COHR, CYTK, DOCN, FIX, FLEX, GLW, GSAT, HUT, IESC,
  INTC, MKSI, MOD, MP, MRVL, MTSI, MTZ, ON, ONTO, POWL, RKLB, RVMD,
  SANM, SATS, SITM, SMTC, STRL, TER, TTMI, VIAV, VICR, VRT, WDC, CL.
- First live rebalance executed (2026-05-18): 6 buys recorded with the
  actual EUR/USD rates IBKR applied (SNDK 1.16399, BE 1.16399, LITE
  1.16409, AAOI 1.16434). Portfolio value after commissions: 1,990.56
  EUR from 2,000 EUR initial capital (102.19 EUR cash + 1,888.37 EUR
  invested across 6 positions).

### Changed
- Momentum values in `history.json` and `backtest-history.json` are now
  stored as percentages (e.g. `2809.29` for +2809%) under new field names
  `momentum_us_top_pct` and `momentum_ibex_top_pct`. Previously stored as
  ratios under `momentum_us_top` / `momentum_ibex_top` (e.g. `28.09`).
  Existing `history.json` migrated to the new format.
- `tests/test_momentum.py` updated to use `US_LARGE_CAP` and verifies that
  the `SP500_LARGE_CAP` alias still works for backwards compatibility.

### Fixed
- `src/rebalance.py` no longer writes a hybrid entry that the user had to
  update manually after execution. The PLAN entry is now write-once and
  the EXECUTION entry is added separately by `append-rebalance.py`.

---

## [1.2.0] - 2026-05-18

**Real-data backtest and time-weighted returns**

### Added
- Migrated `src/backtest.py` from synthetic prices to fully real historical
  data. Reads daily prices from `data/monthly-historic-prices.csv`
  (resampled to month-end) and real EUR/USD rates from
  `data/eurusd.rates.csv` per rebalance day.
- Universe coverage: 157/157 US + 35/35 IBEX tickers with real data.
- Implemented time-weighted return for added/withdrawn capital
  scenarios (foundational work that became fully wired into `src/cagr.py`
  in 1.3.0).

### Results (with real data)
- CAGR: +56.95% (synthetic was +41.69%)
- Sharpe ratio: 1.24 (synthetic was 1.57)
- Max drawdown: -44.26% (synthetic was -22.80%)
- Higher return AND higher risk than the synthetic backtest, as expected.

---

## [1.1.1] - 2026-05-18

### Fixed
- `src/backtest.py` rewritten to load real historical EUR/USD rates per
  rebalance day instead of using a constant reference rate.

### Added
- New `backtests/` folder with all backtest outputs (separated from
  production data in `data/`).
- Updated capital allocation to **65% US + 30% IBEX + 5% cash reserve**
  (previously 67/33 with no explicit cash reserve).
- New script generates `backtest-results.md` with year-by-year and
  quarter-by-quarter trade detail.
- New script generates `backtest-dashboard.png` (executive dashboard image).
- New PowerShell script `commit-rebalance.ps1` that builds a structured
  commit message after each quarterly rebalance.
- Expanded the US universe from 101 to 117 stocks across NYSE and NASDAQ.
  The 16 added stocks are large-cap names that are NOT in the S&P 500
  (ARM, SNDK, LITE, AAOI, CBRS, ASML, TSM, MELI, PDD, BABA, NVO, AZN, NU,
  HOOD, BE, ENPH).

---

## [1.0.0] - 2026-05-13

**First stable release.** Clean snapshot of the strategy framework BEFORE
the first live execution. The DEMO account is empty and no real
operations have been performed yet.

### Added
- Quarterly rebalance script (`src/rebalance.py`) targeting the IBKR
  DEMO account.
- Historical backtest (`src/backtest.py`) covering 2019-2025 with
  synthetic prices calibrated to known annual returns.
- Universe definitions for IBEX 35 (35 stocks) and S&P 500 large-cap
  (~101 stocks).
- Dynamic momentum 12-1 selection (no static pre-selection).
- Fractional shares support (configurable via `ALLOW_FRACTIONAL_SHARES`).
- Capital flow tracking via `initial_capital_eur` and
  `net_capital_contributed_eur`.
- Append-only history log in `data/history.json`.
- Spanish IRPF tax modeling (Base del Ahorro brackets 2019-2025).
- Documentation: README, methodology, backtest results, disclaimer.
- Unit tests (12 tests covering universe configuration and momentum math).

### Initial state
- `data/portfolio.json`: empty (no positions, `cash_eur=0`,
  `last_rebalance=null`).
- `data/history.json`: empty array `[]`.
- Initial capital configured: 2,000 EUR.
- Account type: IBKR DEMO (paper trading).
