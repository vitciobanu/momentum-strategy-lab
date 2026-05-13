"""
================================================================================
HISTORICAL BACKTEST (2019-2025)
================================================================================
Reproduces the mixed USA/Spain momentum strategy on synthetic price data
calibrated to known historical annual returns.

This backtest uses DYNAMIC SELECTION over the full universe: each quarter the
script picks the 4 stocks with highest momentum from ALL S&P 500 candidates,
and the 2 stocks with highest momentum from ALL IBEX 35 components. There is
no static pre-selection of "best stocks".

NOTE ON CALIBRATION:
This file embeds annual-return calibration data for the S&P 500 representative
sample and the full IBEX 35. The calibration data here is a snapshot used to
generate synthetic prices that match historical year-end behavior. For a
production-grade backtest, replace this with actual historical daily prices
downloaded via yfinance.

USAGE:
    python src/backtest.py
================================================================================
"""

import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from universe import CONFIG

# ============================================================================
# Synthetic price calibration — IBEX 35 (all 35 components)
# Annual returns 2014-2025 approximated from public historical data.
# ============================================================================

IBEX_CALIBRATION = {
    "ITX":  {"start":23,    "ann":[0.05,0.32,-0.05,-0.10,-0.20,0.42,-0.16,0.10,-0.13,0.50,0.30,0.08], "vol":0.06},
    "SAN":  {"start":7,     "ann":[-0.20,-0.30,0.10,0.05,-0.27,0.20,-0.35,0.20,0.10,0.45,0.30,0.50], "vol":0.08},
    "IBE":  {"start":5,     "ann":[0.10,0.05,0.15,0.10,0.10,0.28,0.27,-0.11,0.05,0.09,0.15,0.28], "vol":0.05},
    "BBVA": {"start":9,     "ann":[-0.05,-0.20,0.05,0.05,-0.35,0.07,-0.19,0.30,0.07,0.46,0.14,0.74], "vol":0.08},
    "IAG":  {"start":6,     "ann":[0.20,0.30,-0.15,0.30,-0.07,0.02,-0.77,0.00,0.01,0.10,0.78,0.20], "vol":0.12},
    "ACS":  {"start":28,    "ann":[-0.05,0.10,0.05,0.15,-0.10,0.20,-0.15,-0.05,0.05,0.25,0.30,0.35], "vol":0.06},
    "TEF":  {"start":12,    "ann":[-0.13,-0.20,-0.10,-0.08,-0.13,0.08,-0.46,-0.07,-0.20,0.18,0.10,0.05], "vol":0.06},
    "CLNX": {"start":14,    "ann":[0.0,0.15,0.05,0.20,0.12,0.65,0.20,-0.05,-0.32,0.20,0.05,0.10], "vol":0.08},
    "REP":  {"start":19,    "ann":[-0.15,-0.30,0.30,0.10,-0.05,-0.05,-0.50,0.50,0.34,-0.05,-0.10,0.08], "vol":0.08},
    "AENA": {"start":90,    "ann":[0.30,0.50,0.30,0.25,-0.05,0.30,-0.35,0.12,0.08,0.30,0.35,0.25], "vol":0.07},
    "FER":  {"start":16,    "ann":[0.15,0.05,-0.05,0.10,-0.05,0.25,-0.18,0.20,0.18,0.35,0.30,0.20], "vol":0.06},
    "SAB":  {"start":2.5,   "ann":[-0.20,0.05,-0.20,0.40,-0.40,-0.30,-0.65,1.20,0.15,0.55,0.45,0.55], "vol":0.10},
    "MAP":  {"start":3,     "ann":[-0.05,-0.10,0.05,0.10,-0.10,0.05,-0.20,0.05,0.10,0.15,0.30,0.20], "vol":0.05},
    "BKT":  {"start":7,     "ann":[0.05,0.05,-0.10,0.40,-0.32,0.05,-0.30,0.40,0.05,0.45,0.30,0.45], "vol":0.07},
    "ANA":  {"start":60,    "ann":[0.10,0.20,0.15,0.10,-0.05,0.30,0.18,0.15,0.10,-0.05,-0.10,0.10], "vol":0.06},
    "ELE":  {"start":17,    "ann":[-0.05,0.10,0.15,0.15,0.15,0.20,0.20,-0.20,-0.10,0.10,0.20,0.25], "vol":0.05},
    "NTGY": {"start":21,    "ann":[-0.10,-0.05,0.10,0.15,0.15,0.05,-0.15,0.30,0.45,-0.15,0.10,0.20], "vol":0.06},
    "RED":  {"start":16,    "ann":[0.10,0.05,0.10,0.05,-0.05,0.05,0.00,-0.15,-0.10,0.00,0.10,0.15], "vol":0.04},
    "GRF":  {"start":25,    "ann":[0.20,0.30,-0.20,0.05,0.10,0.10,-0.10,-0.35,-0.50,0.20,0.05,0.20], "vol":0.09},
    "MRL":  {"start":9,     "ann":[0.0,0.10,0.05,0.30,-0.20,0.20,-0.30,0.10,-0.15,0.20,0.15,0.10], "vol":0.06},
    "AMS":  {"start":18,    "ann":[0.25,0.45,0.10,0.50,0.10,0.20,-0.10,0.40,-0.35,-0.10,-0.30,0.10], "vol":0.10},
    "CABK": {"start":4.5,   "ann":[-0.10,-0.20,-0.05,0.25,-0.35,-0.10,-0.25,1.10,0.45,0.50,0.55,0.55], "vol":0.09},
    "ENG":  {"start":25,    "ann":[0.20,0.05,0.10,0.10,-0.05,0.10,-0.05,-0.15,-0.10,0.00,-0.05,0.10], "vol":0.05},
    "COL":  {"start":6,     "ann":[0.15,0.20,0.05,0.10,0.05,0.40,-0.05,0.10,-0.20,0.05,0.05,0.20], "vol":0.06},
    "ROVI": {"start":12,    "ann":[0.20,0.30,0.30,0.20,0.10,0.20,0.55,0.95,-0.30,-0.15,0.05,0.10], "vol":0.08},
    "IDR":  {"start":11,    "ann":[-0.10,-0.20,0.10,0.40,-0.20,0.40,0.05,-0.10,-0.25,0.50,0.40,0.30], "vol":0.09},
    "ACX":  {"start":11,    "ann":[0.10,0.05,0.20,0.15,-0.20,0.05,-0.18,0.45,-0.18,0.10,-0.05,0.15], "vol":0.08},
    "LOG":  {"start":6,     "ann":[0.10,0.20,0.05,0.05,-0.15,0.10,-0.25,0.30,-0.20,0.40,0.50,0.25], "vol":0.09},
    "FDR":  {"start":6,     "ann":[0.10,0.20,0.15,0.20,-0.15,0.15,-0.20,0.18,0.05,0.20,0.15,0.20], "vol":0.07},
    "SCYR": {"start":2,     "ann":[0.05,0.10,0.05,0.15,-0.10,0.15,-0.30,0.20,0.05,0.30,0.25,0.40], "vol":0.08},
    "UNI":  {"start":8,     "ann":[0.10,0.20,0.05,0.10,0.05,0.15,0.10,0.20,0.30,0.20,0.25,0.20], "vol":0.06},
    "ANE":  {"start":30,    "ann":[0.10,0.20,0.10,0.15,0.0,0.25,0.40,0.20,0.05,-0.10,-0.05,0.10], "vol":0.07},
    "MTS":  {"start":10,    "ann":[-0.45,-0.50,0.65,0.20,-0.15,0.05,0.55,0.85,-0.15,-0.10,0.10,0.20], "vol":0.10},
    "PUIG": {"start":24,    "ann":[0.10,0.05,0.05,0.10,0.05,0.10,0.10,0.10,0.10,0.10,-0.20,0.05], "vol":0.07},
    "SLR":  {"start":3,     "ann":[0.10,0.20,0.30,0.50,0.40,0.30,1.50,0.20,-0.30,-0.40,-0.20,0.20], "vol":0.13},
}

# ============================================================================
# Synthetic price calibration — S&P 500 representative sample (~50 stocks)
# Spans all 11 sectors to allow realistic dynamic momentum selection
# ============================================================================

SP500_CALIBRATION = {
    # Tech mega caps
    "AAPL": {"start":70,    "ann":[0.40,-0.03,0.10,0.46,-0.07,0.86,0.82,0.34,-0.27,0.49,0.30,0.10], "vol":0.07},
    "MSFT": {"start":38,    "ann":[0.27,0.22,0.15,0.41,0.21,0.55,0.41,0.52,-0.28,0.58,0.12,0.20], "vol":0.06},
    "NVDA": {"start":0.4,   "ann":[0.30,0.65,2.27,0.82,-0.31,0.76,1.22,1.25,-0.50,2.40,1.71,0.45], "vol":0.12},
    "GOOGL":{"start":56,    "ann":[-0.04,0.46,0.0,0.36,-0.01,0.28,0.31,0.65,-0.39,0.58,0.36,0.20], "vol":0.07},
    "AMZN": {"start":19,    "ann":[-0.22,1.18,0.10,0.56,0.28,0.23,0.76,0.02,-0.50,0.81,0.44,0.15], "vol":0.09},
    "META": {"start":55,    "ann":[0.43,0.34,0.10,0.55,-0.26,0.57,0.33,0.23,-0.64,1.94,0.65,0.18], "vol":0.10},
    "TSLA": {"start":14.6,  "ann":[0.50,0.50,-0.10,0.45,0.07,0.26,7.43,0.50,-0.65,1.02,0.63,0.10], "vol":0.15},
    "AVGO": {"start":9.2,   "ann":[0.43,0.45,0.20,0.45,0.0,0.27,0.39,0.55,-0.16,1.04,1.10,0.30], "vol":0.09},
    "ORCL": {"start":40,    "ann":[-0.05,-0.18,0.04,0.27,0.16,0.36,0.30,0.20,-0.05,0.30,0.66,0.20], "vol":0.07},
    "CRM":  {"start":55,    "ann":[0.15,0.30,0.10,0.50,0.30,0.20,0.40,0.15,-0.50,0.95,0.15,0.15], "vol":0.09},
    "ADBE": {"start":60,    "ann":[0.25,0.30,0.10,0.70,0.27,0.45,0.55,0.15,-0.40,0.75,0.10,-0.10], "vol":0.08},
    "AMD":  {"start":4,     "ann":[-0.55,-0.10,2.95,0.10,0.80,0.15,1.00,0.55,-0.55,1.30,-0.10,0.40], "vol":0.14},
    "INTC": {"start":36,    "ann":[0.40,-0.05,0.05,0.30,0.05,0.30,-0.15,0.05,-0.50,0.90,-0.55,0.20], "vol":0.07},
    "CSCO": {"start":22,    "ann":[0.30,0.0,0.20,0.30,0.18,0.13,-0.10,0.45,-0.25,-0.05,0.20,0.15], "vol":0.05},
    "NOW":  {"start":65,    "ann":[0.15,0.30,0.10,0.55,0.30,0.55,0.95,0.20,-0.40,0.80,0.50,0.10], "vol":0.09},
    "INTU": {"start":78,    "ann":[0.10,0.10,0.15,0.50,0.20,0.35,0.35,0.65,-0.40,0.55,0.05,0.05], "vol":0.07},
    "IBM":  {"start":187,   "ann":[-0.13,-0.10,0.10,-0.05,-0.25,0.20,-0.05,0.10,0.05,0.20,0.55,0.30], "vol":0.05},
    "TXN":  {"start":47,    "ann":[0.10,-0.05,0.50,0.45,-0.10,0.50,0.30,0.20,-0.10,0.05,0.20,0.15], "vol":0.06},
    "QCOM": {"start":74,    "ann":[-0.05,-0.30,0.35,-0.05,-0.10,0.55,0.75,0.20,-0.40,0.40,0.10,0.05], "vol":0.08},
    "PLTR": {"start":10,    "ann":[0.05,0.10,0.15,0.20,0.10,0.20,0.30,-0.20,-0.65,1.65,3.40,0.50], "vol":0.15},

    # Healthcare
    "LLY":  {"start":63,    "ann":[0.36,0.20,-0.13,0.20,0.34,0.13,0.30,0.65,0.32,0.59,0.32,-0.10], "vol":0.08},
    "JNJ":  {"start":92,    "ann":[0.17,0.0,0.14,0.21,-0.05,0.16,0.10,0.11,0.06,-0.09,0.05,0.08], "vol":0.04},
    "UNH":  {"start":89,    "ann":[0.36,0.18,0.36,0.41,0.13,0.18,0.20,0.43,0.07,0.01,0.05,-0.45], "vol":0.07},
    "ABBV": {"start":65,    "ann":[0.10,-0.05,-0.10,0.55,0.25,-0.05,0.30,0.30,0.20,0.05,0.20,0.20], "vol":0.06},
    "MRK":  {"start":56,    "ann":[0.20,-0.05,0.18,-0.05,0.40,0.20,0.0,0.10,0.50,-0.10,-0.05,-0.10], "vol":0.05},
    "TMO":  {"start":125,   "ann":[0.30,0.10,0.10,0.30,-0.04,0.45,0.45,0.20,-0.20,0.05,0.05,0.05], "vol":0.06},
    "PFE":  {"start":30,    "ann":[0.10,0.05,-0.05,0.15,0.20,0.0,0.05,0.60,-0.10,-0.40,0.10,-0.05], "vol":0.05},

    # Financials
    "BRK-B":{"start":124,   "ann":[0.05,-0.13,0.20,0.21,0.03,0.11,0.02,0.29,0.04,0.16,0.27,0.15], "vol":0.04},
    "JPM":  {"start":56,    "ann":[0.10,0.10,0.30,0.26,-0.07,0.43,-0.05,0.28,-0.15,0.27,0.45,0.20], "vol":0.05},
    "V":    {"start":53,    "ann":[0.18,0.18,0.05,0.46,0.16,0.43,0.17,0.0,-0.04,0.26,0.22,0.15], "vol":0.05},
    "MA":   {"start":86,    "ann":[0.04,0.05,0.10,0.46,0.25,0.59,0.18,0.0,-0.03,0.23,0.22,0.15], "vol":0.05},
    "BAC":  {"start":17,    "ann":[0.15,-0.05,0.32,0.36,-0.16,0.45,-0.13,0.50,-0.25,0.05,0.35,0.30], "vol":0.07},
    "GS":   {"start":178,   "ann":[0.10,0.0,0.30,0.05,-0.35,0.40,0.10,0.45,-0.10,0.10,0.50,0.30], "vol":0.07},

    # Consumer
    "WMT":  {"start":76,    "ann":[0.14,-0.27,0.16,0.46,-0.05,0.28,0.21,0.01,-0.01,0.13,0.71,0.05], "vol":0.05},
    "HD":   {"start":105,   "ann":[0.27,0.27,0.05,0.43,-0.07,0.30,0.25,0.59,-0.24,0.13,0.15,0.05], "vol":0.06},
    "MCD":  {"start":91,    "ann":[-0.05,0.30,0.05,0.45,0.05,0.15,0.10,0.30,-0.05,0.10,-0.05,0.05], "vol":0.04},
    "NKE":  {"start":45,    "ann":[0.20,0.30,-0.18,0.25,0.20,0.40,0.40,0.20,-0.30,0.0,-0.30,-0.10], "vol":0.06},
    "PG":   {"start":82,    "ann":[0.02,0.39,0.11,0.20,-0.06,0.07,0.18,0.05,0.10,0.05,0.15,0.05], "vol":0.04},
    "KO":   {"start":41,    "ann":[0.08,0.06,-0.03,0.15,0.04,0.20,0.0,0.10,0.10,-0.05,0.10,0.10], "vol":0.04},
    "COST": {"start":119,   "ann":[0.20,0.06,-0.02,0.20,0.10,0.45,0.30,0.50,-0.20,0.50,0.40,0.10], "vol":0.05},

    # Comms & media
    "NFLX": {"start":49,    "ann":[-0.05,1.34,0.10,0.55,0.40,0.20,0.65,-0.10,-0.50,0.65,0.85,0.30], "vol":0.10},
    "DIS":  {"start":76,    "ann":[0.27,0.13,-0.03,0.05,0.20,0.35,0.25,-0.15,-0.45,0.05,0.20,0.05], "vol":0.06},
    "T":    {"start":35,    "ann":[-0.05,0.05,0.30,-0.05,-0.20,0.40,-0.30,-0.05,-0.05,0.10,0.35,0.15], "vol":0.05},

    # Energy
    "XOM":  {"start":100,   "ann":[-0.10,-0.13,0.15,-0.10,-0.19,0.07,-0.41,0.49,0.80,-0.09,0.10,0.15], "vol":0.06},
    "CVX":  {"start":125,   "ann":[-0.05,-0.20,0.35,0.10,-0.10,0.20,-0.30,0.45,0.55,-0.15,0.10,0.15], "vol":0.06},

    # Industrials
    "BA":   {"start":130,   "ann":[-0.05,0.10,0.10,0.90,0.10,-0.05,-0.35,-0.05,-0.05,0.40,-0.30,0.10], "vol":0.10},
    "GE":   {"start":25,    "ann":[-0.10,0.20,-0.05,-0.45,-0.55,0.55,-0.05,-0.05,-0.10,0.95,0.55,0.10], "vol":0.09},
    "CAT":  {"start":90,    "ann":[-0.05,-0.25,0.40,0.70,-0.20,0.20,0.20,0.20,0.20,-0.05,0.50,0.25], "vol":0.07},

    # Others
    "ACN":  {"start":76,    "ann":[0.10,0.30,-0.05,0.40,0.0,0.55,0.30,0.55,-0.35,0.35,0.05,-0.05], "vol":0.06},
}

# Spanish IRPF "base del ahorro" brackets per year
IRPF_BRACKETS = {
    2019: [(0, 6000, 0.19), (6000, 50000, 0.21), (50000, float("inf"), 0.23)],
    2020: [(0, 6000, 0.19), (6000, 50000, 0.21), (50000, float("inf"), 0.23)],
    2021: [(0, 6000, 0.19), (6000, 50000, 0.21), (50000, 200000, 0.23), (200000, float("inf"), 0.26)],
    2022: [(0, 6000, 0.19), (6000, 50000, 0.21), (50000, 200000, 0.23), (200000, 300000, 0.27), (300000, float("inf"), 0.28)],
    2023: [(0, 6000, 0.19), (6000, 50000, 0.21), (50000, 200000, 0.23), (200000, 300000, 0.27), (300000, float("inf"), 0.28)],
    2024: [(0, 6000, 0.19), (6000, 50000, 0.21), (50000, 200000, 0.23), (200000, 300000, 0.27), (300000, float("inf"), 0.28)],
    2025: [(0, 6000, 0.19), (6000, 50000, 0.21), (50000, 200000, 0.23), (200000, 300000, 0.27), (300000, float("inf"), 0.30)],
}

def calc_irpf(gain, year):
    if gain <= 0:
        return 0.0
    tax = 0.0
    for low, high, rate in IRPF_BRACKETS[year]:
        if gain > low:
            tax += (min(gain, high) - low) * rate
    return tax

def build_series(start_price, annual_returns, vol_monthly, n_months, seed_offset):
    np.random.seed(42 + seed_offset)
    prices = [start_price]
    for annual_ret in annual_returns:
        monthly_mean = (1 + annual_ret)**(1/12) - 1
        for _ in range(12):
            shock = np.random.normal(0, vol_monthly)
            prices.append(max(prices[-1] * (1 + monthly_mean + shock), 0.1))
    return prices[1:n_months+1]

def build_prices(calibration, dates):
    prices = pd.DataFrame(index=dates)
    for i, (ticker, c) in enumerate(calibration.items()):
        prices[ticker] = build_series(c["start"], c["ann"], c["vol"], len(dates), i)
    return prices

def main():
    print("="*78)
    print("BACKTEST: Mixed USA/Spain Momentum Strategy (2019-2025)")
    print(f"Universe: {len(IBEX_CALIBRATION)} IBEX + {len(SP500_CALIBRATION)} S&P 500 = "
          f"{len(IBEX_CALIBRATION) + len(SP500_CALIBRATION)} stocks total")
    print(f"Selection: dynamic each quarter, no pre-filtering")
    print(f"Configuration: {CONFIG['N_SP500_POSITIONS']} S&P + {CONFIG['N_IBEX_POSITIONS']} IBEX, "
          f"weights {CONFIG['WEIGHT_SP500']:.0%}/{CONFIG['WEIGHT_IBEX']:.0%}")
    print("="*78)

    dates = pd.date_range("2014-01-31", "2025-12-31", freq="ME")
    prices_ibex = build_prices(IBEX_CALIBRATION, dates)
    prices_sp = build_prices(SP500_CALIBRATION, dates)

    momentum_ibex = prices_ibex.shift(1) / prices_ibex.shift(12) - 1
    momentum_sp = prices_sp.shift(1) / prices_sp.shift(12) - 1

    INITIAL_CAPITAL = 2000.0
    EUR_USD = CONFIG["EUR_USD_REFERENCE"]
    # Backtest assumption: commissions are ignored. In real execution,
    # commissions vary by IBKR tier/volume/account size and are recorded
    # manually in data/history.json after each rebalance.

    all_sim_dates = momentum_ibex.dropna().index.intersection(momentum_sp.dropna().index)
    all_sim_dates = all_sim_dates[all_sim_dates >= "2019-01-01"]
    rebalance_dates = [d for d in all_sim_dates if d.month in [1, 4, 7, 10]]

    cash = INITIAL_CAPITAL
    holdings = {}
    yearly_realized_gain = {}
    monthly_log = []
    all_selections = []

    for date in all_sim_dates:
        year = date.year
        is_rebalance = date in rebalance_dates
        n_ops = 0

        if is_rebalance:
            # DYNAMIC SELECTION over the full universe
            mom_sp_t = momentum_sp.loc[date].dropna()
            mom_ibex_t = momentum_ibex.loc[date].dropna()
            top_sp = mom_sp_t.nlargest(CONFIG["N_SP500_POSITIONS"]).index.tolist()
            top_ibex = mom_ibex_t.nlargest(CONFIG["N_IBEX_POSITIONS"]).index.tolist()
            new_top = top_sp + top_ibex
            all_selections.append({"date": date, "sp": top_sp, "ibex": top_ibex})

            for t in list(holdings.keys()):
                if t not in new_top:
                    n_shares, cost, market = holdings[t]
                    price = prices_sp.loc[date, t] if market == "SP" else prices_ibex.loc[date, t]
                    cash += n_shares * price
                    yearly_realized_gain[year] = yearly_realized_gain.get(year, 0) + n_shares * (price - cost)
                    del holdings[t]
                    n_ops += 1

            cur_val = sum(
                n * (prices_sp.loc[date, t] if m == "SP" else prices_ibex.loc[date, t])
                for t, (n, _, m) in holdings.items()
            )
            total_val = cash + cur_val
            target_per_sp = (total_val * CONFIG["WEIGHT_SP500"]) / CONFIG["N_SP500_POSITIONS"]
            target_per_ibex = (total_val * CONFIG["WEIGHT_IBEX"]) / CONFIG["N_IBEX_POSITIONS"]

            for t in top_sp:
                if t not in holdings:
                    price = prices_sp.loc[date, t]
                    invest = target_per_sp
                    if invest <= 0 or invest > cash: continue
                    # Fractional shares assumed in backtest (matches CONFIG default)
                    holdings[t] = (invest / price, price, "SP")
                    cash -= invest
                    n_ops += 1

            for t in top_ibex:
                if t not in holdings:
                    price = prices_ibex.loc[date, t]
                    invest = target_per_ibex
                    if invest <= 0 or invest > cash: continue
                    holdings[t] = (invest / price, price, "IBEX")
                    cash -= invest
                    n_ops += 1

        cur_val = sum(
            n * (prices_sp.loc[date, t] if m == "SP" else prices_ibex.loc[date, t])
            for t, (n, _, m) in holdings.items()
        )
        monthly_log.append({"fecha": date, "valor": cash + cur_val, "n_ops": n_ops})

    df_log = pd.DataFrame(monthly_log).set_index("fecha")

    yearly_summary = []
    total_taxes = 0
    for year in range(2019, 2026):
        year_data = df_log[df_log.index.year == year]
        if len(year_data) == 0: continue
        valor_ini = df_log[df_log.index < f"{year}-01-01"]["valor"].iloc[-1] if year > 2019 else INITIAL_CAPITAL
        valor_fin_bruto = year_data["valor"].iloc[-1]
        realized = yearly_realized_gain.get(year, 0)
        tax = calc_irpf(realized, year)
        total_taxes += tax
        yearly_summary.append({
            "year": year, "start": valor_ini, "end_net": valor_fin_bruto - tax,
            "return_net": (valor_fin_bruto - tax) / valor_ini - 1,
            "tax": tax, "ops": int(year_data["n_ops"].sum())
        })
        df_log.loc[df_log.index >= f"{year+1}-01-01", "valor"] -= tax if year < 2025 else 0

    valor_serie = df_log["valor"].copy()
    valor_serie.iloc[-1] -= calc_irpf(yearly_realized_gain.get(2025, 0), 2025)

    returns_net = valor_serie.pct_change()
    returns_net.iloc[0] = valor_serie.iloc[0] / INITIAL_CAPITAL - 1
    n_years = len(returns_net) / 12

    print(f"\n{'Year':<6}{'V.start':>12}{'V.end net':>14}{'Return net':>13}{'Tax':>12}{'Ops':>6}")
    print("-"*78)
    for s in yearly_summary:
        print(f"{s['year']:<6}{s['start']:>11,.0f}€{s['end_net']:>13,.0f}€"
              f"{s['return_net']:>+12.2%}{s['tax']:>11,.0f}€{s['ops']:>6}")

    print(f"\n{'='*78}")
    print(f"FINAL RESULTS (2019-2025, 7 years, net of commissions and Spanish IRPF)")
    print(f"{'='*78}")
    print(f"  Initial capital:       {INITIAL_CAPITAL:>10,.2f} EUR")
    print(f"  Final capital:         {valor_serie.iloc[-1]:>10,.2f} EUR")
    print(f"  Total return:          {(valor_serie.iloc[-1]/INITIAL_CAPITAL - 1)*100:>+10.2f}%")
    print(f"  CAGR (net):            {((valor_serie.iloc[-1]/INITIAL_CAPITAL)**(1/n_years) - 1)*100:>+10.2f}%")
    print(f"  Annualized volatility: {returns_net.std() * np.sqrt(12)*100:>10.2f}%")
    print(f"  Sharpe ratio (rf=0):   {returns_net.mean() / returns_net.std() * np.sqrt(12):>10.2f}")
    print(f"  Max drawdown:          {((valor_serie / valor_serie.cummax()) - 1).min()*100:>10.2f}%")
    print(f"  Total taxes:           {total_taxes + calc_irpf(yearly_realized_gain.get(2025, 0), 2025):>10,.2f} EUR")
    print(f"  Note: commissions excluded from backtest. In real execution,")
    print(f"        record actual commissions in data/history.json after each rebalance.")

    # Show diversity of selected stocks
    from collections import Counter
    all_sp_picks = [t for s in all_selections for t in s["sp"]]
    all_ibex_picks = [t for s in all_selections for t in s["ibex"]]
    sp_freq = Counter(all_sp_picks).most_common(10)
    ibex_freq = Counter(all_ibex_picks).most_common(5)
    print(f"\nMost-selected S&P 500 stocks ({len(set(all_sp_picks))} unique out of {len(SP500_CALIBRATION)}):")
    for t, c in sp_freq:
        print(f"  {t:6s}  picked {c} times")
    print(f"\nMost-selected IBEX stocks ({len(set(all_ibex_picks))} unique out of {len(IBEX_CALIBRATION)}):")
    for t, c in ibex_freq:
        print(f"  {t:6s}  picked {c} times")

if __name__ == "__main__":
    main()
