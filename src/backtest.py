"""
================================================================================
HISTORICAL BACKTEST (2019-2025)
================================================================================
Reproduces the mixed USA/Spain momentum strategy on synthetic price data
calibrated to known historical annual returns, with REAL historical EUR/USD
exchange rates from data/eurusd_rates.csv.

KEY CHANGES vs the earlier backtest:
  - Reads EUR/USD daily rates from data/eurusd_rates.csv and uses the rate
    of each rebalance day to convert US prices to EUR (the old version used
    a constant 1.1758 rate).
  - Uses updated capital allocation: 65% US + 30% IBEX + 5% cash reserve.
  - Writes results in production-compatible JSON files:
      backtests/backtest-portfolio.json (final state)
      backtests/backtest-history.json (one entry per rebalance, append-only)
  - Generates a detailed CSV table with one row per executed trade.

Each backtest quarter, the JSON files are updated EXACTLY the way the
production files (data/portfolio.json, data/history.json) are updated, so
the backtest can be audited the same way as live runs.

USAGE:
    python src/backtest.py                            # runs the simulation
    python scripts/build_backtest_dashboard.py        # builds the PNG dashboard
    python scripts/build_backtest_report.py           # builds the .md report

OUTPUTS:
    src/backtest.py writes:
        backtests/backtest-portfolio.json   Final portfolio state
        backtests/backtest-history.json     Rebalance-by-rebalance log
        backtests/backtest-trades.csv       One row per buy/sell with qty, amount, return
        backtests/backtest-metrics.json     Numeric summary (used by the report scripts)

    scripts/build_backtest_dashboard.py writes:
        backtests/backtest-dashboard.png    Executive dashboard image

    scripts/build_backtest_report.py writes:
        backtests/backtest-results.md       Human-readable summary
================================================================================
"""

import pandas as pd
import numpy as np
import json
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from universe import CONFIG

# ============================================================================
# PATHS
# ============================================================================
ROOT = Path(__file__).parent.parent
EURUSD_FILE = ROOT / "data" / "eurusd_rates.csv"
BACKTESTS_DIR = ROOT / "backtests"
BACKTESTS_DIR.mkdir(exist_ok=True)
BT_PORTFOLIO_FILE = BACKTESTS_DIR / "backtest-portfolio.json"
BT_HISTORY_FILE = BACKTESTS_DIR / "backtest-history.json"
BT_TRADES_FILE = BACKTESTS_DIR / "backtest-trades.csv"

# ============================================================================
# SYNTHETIC PRICE CALIBRATION
# Approximate annual returns 2014-2025, calibrated from public historical data.
# Used to generate monthly prices that reproduce known year-end behavior of
# each stock, including major events (COVID 2020, rate hikes 2022, AI boom 2024).
# This is NOT real daily/monthly historical data. For a production-grade
# backtest, replace with actual prices downloaded via yfinance.
# ============================================================================

IBEX_CALIBRATION = {
    "ROVI":{"start":12,"ann":[0.20,0.30,0.30,0.20,0.10,0.20,0.55,0.95,-0.30,-0.15,0.05,0.10],"vol":0.08},
    "ANE": {"start":30,"ann":[0.10,0.20,0.10,0.15,0.0,0.25,0.40,0.20,0.05,-0.10,-0.05,0.10],"vol":0.07},
    "CLNX":{"start":14,"ann":[0.0,0.15,0.05,0.20,0.12,0.65,0.20,-0.05,-0.32,0.20,0.05,0.10],"vol":0.08},
    "AENA":{"start":90,"ann":[0.30,0.50,0.30,0.25,-0.05,0.30,-0.35,0.12,0.08,0.30,0.35,0.25],"vol":0.07},
    "ACX": {"start":11,"ann":[0.10,0.05,0.20,0.15,-0.20,0.05,-0.18,0.45,-0.18,0.10,-0.05,0.15],"vol":0.08},
    "FER": {"start":16,"ann":[0.15,0.05,-0.05,0.10,-0.05,0.25,-0.18,0.20,0.18,0.35,0.30,0.20],"vol":0.06},
    "UNI": {"start":8, "ann":[0.10,0.20,0.05,0.10,0.05,0.15,0.10,0.20,0.30,0.20,0.25,0.20],"vol":0.06},
    "ELE": {"start":17,"ann":[-0.05,0.10,0.15,0.15,0.15,0.20,0.20,-0.20,-0.10,0.10,0.20,0.25],"vol":0.05},
    "REP": {"start":19,"ann":[-0.15,-0.30,0.30,0.10,-0.05,-0.05,-0.50,0.50,0.34,-0.05,-0.10,0.08],"vol":0.08},
    "FDR": {"start":6, "ann":[0.10,0.20,0.15,0.20,-0.15,0.15,-0.20,0.18,0.05,0.20,0.15,0.20],"vol":0.07},
    "NTGY":{"start":21,"ann":[-0.10,-0.05,0.10,0.15,0.15,0.05,-0.15,0.30,0.45,-0.15,0.10,0.20],"vol":0.06},
    "SCYR":{"start":2, "ann":[0.05,0.10,0.05,0.15,-0.10,0.15,-0.30,0.20,0.05,0.30,0.25,0.40],"vol":0.08},
    "GRF": {"start":25,"ann":[0.20,0.30,-0.20,0.05,0.10,0.10,-0.10,-0.35,-0.50,0.20,0.05,0.20],"vol":0.09},
    "IBE": {"start":5, "ann":[0.10,0.05,0.15,0.10,0.10,0.28,0.27,-0.11,0.05,0.09,0.15,0.28],"vol":0.05},
    "ANA": {"start":60,"ann":[0.10,0.20,0.15,0.10,-0.05,0.30,0.18,0.15,0.10,-0.05,-0.10,0.10],"vol":0.06},
    "BKT": {"start":7, "ann":[0.05,0.05,-0.10,0.40,-0.32,0.05,-0.30,0.40,0.05,0.45,0.30,0.45],"vol":0.07},
    "CABK":{"start":4.5,"ann":[-0.10,-0.20,-0.05,0.25,-0.35,-0.10,-0.25,1.10,0.45,0.50,0.55,0.55],"vol":0.09},
    "COL": {"start":6, "ann":[0.15,0.20,0.05,0.10,0.05,0.40,-0.05,0.10,-0.20,0.05,0.05,0.20],"vol":0.06},
    "SAN": {"start":7, "ann":[-0.20,-0.30,0.10,0.05,-0.27,0.20,-0.35,0.20,0.10,0.45,0.30,0.50],"vol":0.08},
    "BBVA":{"start":9, "ann":[-0.05,-0.20,0.05,0.05,-0.35,0.07,-0.19,0.30,0.07,0.46,0.14,0.74],"vol":0.08},
    "ITX": {"start":23,"ann":[0.05,0.32,-0.05,-0.10,-0.20,0.42,-0.16,0.10,-0.13,0.50,0.30,0.08],"vol":0.06},
}

# Prices below are USD denominated for the US universe
SP500_CALIBRATION = {
    "BA":  {"start":130,  "ann":[-0.05,0.10,0.10,0.90,0.10,-0.05,-0.35,-0.05,-0.05,0.40,-0.30,0.10],"vol":0.10},
    "NVDA":{"start":0.4,  "ann":[0.30,0.65,2.27,0.82,-0.31,0.76,1.22,1.25,-0.50,2.40,1.71,0.45],"vol":0.12},
    "ADBE":{"start":60,   "ann":[0.25,0.30,0.10,0.70,0.27,0.45,0.55,0.15,-0.40,0.75,0.10,-0.10],"vol":0.08},
    "NFLX":{"start":49,   "ann":[-0.05,1.34,0.10,0.55,0.40,0.20,0.65,-0.10,-0.50,0.65,0.85,0.30],"vol":0.10},
    "AVGO":{"start":9.2,  "ann":[0.43,0.45,0.20,0.45,0.0,0.27,0.39,0.55,-0.16,1.04,1.10,0.30],"vol":0.09},
    "AMD": {"start":4,    "ann":[-0.55,-0.10,2.95,0.10,0.80,0.15,1.00,0.55,-0.55,1.30,-0.10,0.40],"vol":0.14},
    "MSFT":{"start":38,   "ann":[0.27,0.22,0.15,0.41,0.21,0.55,0.41,0.52,-0.28,0.58,0.12,0.20],"vol":0.06},
    "GOOGL":{"start":56,  "ann":[-0.04,0.46,0.0,0.36,-0.01,0.28,0.31,0.65,-0.39,0.58,0.36,0.20],"vol":0.07},
    "META":{"start":55,   "ann":[0.43,0.34,0.10,0.55,-0.26,0.57,0.33,0.23,-0.64,1.94,0.65,0.18],"vol":0.10},
    "AAPL":{"start":70,   "ann":[0.40,-0.03,0.10,0.46,-0.07,0.86,0.82,0.34,-0.27,0.49,0.30,0.10],"vol":0.07},
    "AMZN":{"start":19,   "ann":[-0.22,1.18,0.10,0.56,0.28,0.23,0.76,0.02,-0.50,0.81,0.44,0.15],"vol":0.09},
    "TSLA":{"start":14.6, "ann":[0.50,0.50,-0.10,0.45,0.07,0.26,7.43,0.50,-0.65,1.02,0.63,0.10],"vol":0.15},
    "ORCL":{"start":40,   "ann":[-0.05,-0.18,0.04,0.27,0.16,0.36,0.30,0.20,-0.05,0.30,0.66,0.20],"vol":0.07},
    "CRM": {"start":55,   "ann":[0.15,0.30,0.10,0.50,0.30,0.20,0.40,0.15,-0.50,0.95,0.15,0.15],"vol":0.09},
    "NOW": {"start":65,   "ann":[0.15,0.30,0.10,0.55,0.30,0.55,0.95,0.20,-0.40,0.80,0.50,0.10],"vol":0.09},
    "LLY": {"start":63,   "ann":[0.36,0.20,-0.13,0.20,0.34,0.13,0.30,0.65,0.32,0.59,0.32,-0.10],"vol":0.08},
    "UNH": {"start":89,   "ann":[0.36,0.18,0.36,0.41,0.13,0.18,0.20,0.43,0.07,0.01,0.05,-0.45],"vol":0.07},
    "V":   {"start":53,   "ann":[0.18,0.18,0.05,0.46,0.16,0.43,0.17,0.0,-0.04,0.26,0.22,0.15],"vol":0.05},
    "JPM": {"start":56,   "ann":[0.10,0.10,0.30,0.26,-0.07,0.43,-0.05,0.28,-0.15,0.27,0.45,0.20],"vol":0.05},
    "QCOM":{"start":74,   "ann":[-0.05,-0.30,0.35,-0.05,-0.10,0.55,0.75,0.20,-0.40,0.40,0.10,0.05],"vol":0.08},
    "PLTR":{"start":10,   "ann":[0.05,0.10,0.15,0.20,0.10,0.20,0.30,-0.20,-0.65,1.65,3.40,0.50],"vol":0.15},
    "COST":{"start":119,  "ann":[0.20,0.06,-0.02,0.20,0.10,0.45,0.30,0.50,-0.20,0.50,0.40,0.10],"vol":0.05},
    "XOM": {"start":100,  "ann":[-0.10,-0.13,0.15,-0.10,-0.19,0.07,-0.41,0.49,0.80,-0.09,0.10,0.15],"vol":0.06},
    "BRK-B":{"start":124, "ann":[0.05,-0.13,0.20,0.21,0.03,0.11,0.02,0.29,0.04,0.16,0.27,0.15],"vol":0.04},
    "WMT": {"start":76,   "ann":[0.14,-0.27,0.16,0.46,-0.05,0.28,0.21,0.01,-0.01,0.13,0.71,0.05],"vol":0.05},
}

# ============================================================================
# SPANISH IRPF BRACKETS (Base del Ahorro) per year
# ============================================================================
IRPF_BRACKETS = {
    2019: [(0,6000,0.19),(6000,50000,0.21),(50000,float("inf"),0.23)],
    2020: [(0,6000,0.19),(6000,50000,0.21),(50000,float("inf"),0.23)],
    2021: [(0,6000,0.19),(6000,50000,0.21),(50000,200000,0.23),(200000,float("inf"),0.26)],
    2022: [(0,6000,0.19),(6000,50000,0.21),(50000,200000,0.23),(200000,300000,0.27),(300000,float("inf"),0.28)],
    2023: [(0,6000,0.19),(6000,50000,0.21),(50000,200000,0.23),(200000,300000,0.27),(300000,float("inf"),0.28)],
    2024: [(0,6000,0.19),(6000,50000,0.21),(50000,200000,0.23),(200000,300000,0.27),(300000,float("inf"),0.28)],
    2025: [(0,6000,0.19),(6000,50000,0.21),(50000,200000,0.23),(200000,300000,0.27),(300000,float("inf"),0.30)],
}

def calc_irpf(gain, year):
    if gain <= 0:
        return 0.0
    tax = 0.0
    for low, high, rate in IRPF_BRACKETS[year]:
        if gain > low:
            tax += (min(gain, high) - low) * rate
    return tax


# ============================================================================
# EUR/USD HISTORICAL RATES
# ============================================================================

def load_eurusd_rates():
    """Load historical EUR/USD rates from data/eurusd_rates.csv.

    Returns a pandas Series indexed by date with the daily Close rate
    (1 EUR = X USD).
    """
    if not EURUSD_FILE.exists():
        raise FileNotFoundError(
            f"EUR/USD rates file not found at {EURUSD_FILE}. "
            f"Please ensure data/eurusd_rates.csv exists in the project root."
        )
    df = pd.read_csv(EURUSD_FILE)
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%y", errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    return df.set_index("Date")["Close"]


def get_rate_on_or_before(rates_series, target_date):
    """Get the EUR/USD rate on or just before target_date.

    If the target is a market holiday, fall back to the latest preceding
    business day with data (forward-fill).
    """
    target = pd.Timestamp(target_date).normalize()
    available = rates_series[rates_series.index <= target]
    if len(available) == 0:
        # If target is before any data, use the earliest available
        return float(rates_series.iloc[0])
    return float(available.iloc[-1])


# ============================================================================
# SYNTHETIC PRICE GENERATION
# ============================================================================

def build_series(start_price, annual_returns, vol_monthly, n_months, seed_offset):
    """Generate a single price series given annual returns and monthly volatility."""
    np.random.seed(42 + seed_offset)
    prices = [start_price]
    for annual_ret in annual_returns:
        monthly_mean = (1 + annual_ret) ** (1 / 12) - 1
        for _ in range(12):
            shock = np.random.normal(0, vol_monthly)
            prices.append(max(prices[-1] * (1 + monthly_mean + shock), 0.1))
    return prices[1:n_months + 1]


def build_prices(calibration, dates):
    """Generate the price matrix for an entire universe."""
    prices = pd.DataFrame(index=dates)
    for i, (ticker, c) in enumerate(calibration.items()):
        prices[ticker] = build_series(c["start"], c["ann"], c["vol"], len(dates), i)
    return prices


# ============================================================================
# JSON FILE WRITERS (matching production format from data/portfolio.json
# and data/history.json)
# ============================================================================

def save_backtest_portfolio(cash_eur, positions, last_rebalance, initial_capital_eur,
                            net_capital_contributed_eur):
    """Write backtest-portfolio.json mirroring data/portfolio.json schema."""
    data = {
        "_account_type": "BACKTEST (Synthetic 2019-2025)",
        "_purpose": "Final state of the historical backtest. Same schema as data/portfolio.json.",
        "initial_capital_eur": initial_capital_eur,
        "net_capital_contributed_eur": net_capital_contributed_eur,
        "cash_eur": round(cash_eur, 2),
        "positions": positions,
        "last_rebalance": str(last_rebalance) if last_rebalance else None,
    }
    with open(BT_PORTFOLIO_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def save_backtest_history(history):
    """Write backtest-history.json mirroring data/history.json schema."""
    with open(BT_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, default=str)


# ============================================================================
# MAIN BACKTEST
# ============================================================================

def main():
    print("=" * 78)
    print("BACKTEST: Mixed USA/Spain Momentum Strategy (2019-2025)")
    print(f"Configuration: {CONFIG['N_SP500_POSITIONS']} US + {CONFIG['N_IBEX_POSITIONS']} IBEX")
    print(f"Weights: {CONFIG['WEIGHT_SP500']:.0%} US + {CONFIG['WEIGHT_IBEX']:.0%} IBEX "
          f"+ {CONFIG.get('CASH_RESERVE', 0):.0%} cash reserve")
    print("Using REAL historical EUR/USD rates from data/eurusd_rates.csv")
    print("=" * 78)

    # ----- Load EUR/USD historical rates -----
    print("\n[1/5] Loading EUR/USD historical rates...")
    eurusd_rates = load_eurusd_rates()
    print(f"      Loaded {len(eurusd_rates)} daily rates from "
          f"{eurusd_rates.index.min().date()} to {eurusd_rates.index.max().date()}")

    # ----- Generate synthetic prices -----
    print("\n[2/5] Generating synthetic monthly prices...")
    dates = pd.date_range("2014-01-31", "2025-12-31", freq="ME")
    prices_ibex = build_prices(IBEX_CALIBRATION, dates)
    prices_sp = build_prices(SP500_CALIBRATION, dates)
    print(f"      IBEX universe: {len(IBEX_CALIBRATION)} stocks")
    print(f"      US universe:   {len(SP500_CALIBRATION)} stocks (calibration sample)")

    # ----- Compute momentum 12-1 -----
    print("\n[3/5] Computing momentum 12-1...")
    momentum_ibex = prices_ibex.shift(1) / prices_ibex.shift(12) - 1
    momentum_sp = prices_sp.shift(1) / prices_sp.shift(12) - 1

    # ----- Simulate quarterly rebalances -----
    print("\n[4/5] Running quarterly rebalances 2019-2025...")
    INITIAL_CAPITAL = 2000.0
    WEIGHT_SP = CONFIG["WEIGHT_SP500"]      # 0.65
    WEIGHT_IBEX = CONFIG["WEIGHT_IBEX"]     # 0.30
    N_SP = CONFIG["N_SP500_POSITIONS"]      # 4
    N_IBEX = CONFIG["N_IBEX_POSITIONS"]     # 2

    all_sim_dates = momentum_ibex.dropna().index.intersection(momentum_sp.dropna().index)
    all_sim_dates = all_sim_dates[all_sim_dates >= "2019-01-01"]
    rebalance_dates = [d for d in all_sim_dates if d.month in [1, 4, 7, 10]]

    cash_eur = INITIAL_CAPITAL
    holdings = {}      # ticker -> dict with shares, avg_price_eur, market, buy_date
    yearly_realized_gain = {}
    monthly_log = []
    history_entries = []
    trades_records = []  # detailed CSV rows

    for date in all_sim_dates:
        year = date.year
        is_rebalance = date in rebalance_dates

        if is_rebalance:
            # Use REAL EUR/USD rate of this specific rebalance day
            eur_usd = get_rate_on_or_before(eurusd_rates, date)

            mom_sp_t = momentum_sp.loc[date].dropna()
            mom_ibex_t = momentum_ibex.loc[date].dropna()
            top_sp = mom_sp_t.nlargest(N_SP).index.tolist()
            top_ibex = mom_ibex_t.nlargest(N_IBEX).index.tolist()
            new_top = set(top_sp + top_ibex)

            # Snapshot pre-rebalance value
            pre_value_eur = cash_eur + sum(
                _position_value_eur(t, info, prices_sp.loc[date], prices_ibex.loc[date], eur_usd)
                for t, info in holdings.items()
            )

            orders_to_sell = []
            orders_to_buy = []

            # --- SELL positions no longer in top ---
            for t in list(holdings.keys()):
                if t not in new_top:
                    info = holdings[t]
                    if info["market"] == "SP":
                        price_usd = prices_sp.loc[date, t]
                        value_eur = info["shares"] * price_usd / eur_usd
                        gain_eur = value_eur - info["shares"] * info["avg_price_eur"]
                        return_pct = (value_eur / (info["shares"] * info["avg_price_eur"]) - 1) * 100
                    else:
                        price_eur = prices_ibex.loc[date, t]
                        value_eur = info["shares"] * price_eur
                        gain_eur = value_eur - info["shares"] * info["avg_price_eur"]
                        return_pct = (value_eur / (info["shares"] * info["avg_price_eur"]) - 1) * 100
                        price_usd = None

                    cash_eur += value_eur
                    yearly_realized_gain[year] = yearly_realized_gain.get(year, 0) + gain_eur

                    orders_to_sell.append({
                        "ticker": t,
                        "market": info["market"],
                        "shares": round(info["shares"], 4),
                        "ref_price": round(price_usd if info["market"] == "SP" else price_eur, 4),
                        "currency": "USD" if info["market"] == "SP" else "EUR",
                        "value_eur": round(value_eur, 2),
                    })
                    trades_records.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "year": year,
                        "quarter": f"Q{(date.month - 1) // 3 + 1} {year}",
                        "action": "SELL",
                        "ticker": t,
                        "market": info["market"],
                        "shares": round(info["shares"], 4),
                        "price_local": round(price_usd if info["market"] == "SP" else price_eur, 4),
                        "currency": "USD" if info["market"] == "SP" else "EUR",
                        "eur_usd_rate": round(eur_usd, 4) if info["market"] == "SP" else "",
                        "amount_eur": round(value_eur, 2),
                        "return_pct": round(return_pct, 2),
                    })
                    del holdings[t]

            # --- Compute new targets and BUY ---
            current_held_value_eur = sum(
                _position_value_eur(t, info, prices_sp.loc[date], prices_ibex.loc[date], eur_usd)
                for t, info in holdings.items()
            )
            total_eur = cash_eur + current_held_value_eur
            target_per_sp_eur = (total_eur * WEIGHT_SP) / N_SP
            target_per_ibex_eur = (total_eur * WEIGHT_IBEX) / N_IBEX

            for t in top_sp:
                if t not in holdings:
                    price_usd = prices_sp.loc[date, t]
                    invest_eur = target_per_sp_eur
                    if invest_eur <= 0 or invest_eur > cash_eur:
                        continue
                    avg_price_eur = price_usd / eur_usd
                    shares = invest_eur / avg_price_eur
                    holdings[t] = {
                        "shares": shares,
                        "avg_price_eur": avg_price_eur,
                        "market": "SP",
                        "buy_date": date.strftime("%Y-%m-%d"),
                    }
                    cash_eur -= invest_eur
                    orders_to_buy.append({
                        "ticker": t,
                        "market": "SP",
                        "shares": round(shares, 4),
                        "ref_price": round(price_usd, 4),
                        "currency": "USD",
                        "value_eur": round(invest_eur, 2),
                    })
                    trades_records.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "year": year,
                        "quarter": f"Q{(date.month - 1) // 3 + 1} {year}",
                        "action": "BUY",
                        "ticker": t,
                        "market": "SP",
                        "shares": round(shares, 4),
                        "price_local": round(price_usd, 4),
                        "currency": "USD",
                        "eur_usd_rate": round(eur_usd, 4),
                        "amount_eur": round(invest_eur, 2),
                        "return_pct": "",
                    })

            for t in top_ibex:
                if t not in holdings:
                    price_eur = prices_ibex.loc[date, t]
                    invest_eur = target_per_ibex_eur
                    if invest_eur <= 0 or invest_eur > cash_eur:
                        continue
                    shares = invest_eur / price_eur
                    holdings[t] = {
                        "shares": shares,
                        "avg_price_eur": price_eur,
                        "market": "IBEX",
                        "buy_date": date.strftime("%Y-%m-%d"),
                    }
                    cash_eur -= invest_eur
                    orders_to_buy.append({
                        "ticker": t,
                        "market": "IBEX",
                        "shares": round(shares, 4),
                        "ref_price": round(price_eur, 4),
                        "currency": "EUR",
                        "value_eur": round(invest_eur, 2),
                    })
                    trades_records.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "year": year,
                        "quarter": f"Q{(date.month - 1) // 3 + 1} {year}",
                        "action": "BUY",
                        "ticker": t,
                        "market": "IBEX",
                        "shares": round(shares, 4),
                        "price_local": round(price_eur, 4),
                        "currency": "EUR",
                        "eur_usd_rate": "",
                        "amount_eur": round(invest_eur, 2),
                        "return_pct": "",
                    })

            # --- Append history entry (one per rebalance, like data/history.json) ---
            post_value_eur = cash_eur + sum(
                _position_value_eur(t, info, prices_sp.loc[date], prices_ibex.loc[date], eur_usd)
                for t, info in holdings.items()
            )
            history_entries.append({
                "date": date.strftime("%Y-%m-%d"),
                "eur_usd_rate": round(eur_usd, 4),
                "portfolio_value_eur_before": round(pre_value_eur, 2),
                "portfolio_value_eur_after": round(post_value_eur, 2),
                "cash_before_eur": round(pre_value_eur - sum(
                    _position_value_eur(t, holdings.get(t, {"shares":0,"avg_price_eur":0,"market":"SP"}),
                                         prices_sp.loc[date], prices_ibex.loc[date], eur_usd)
                    for t in list(holdings.keys())
                ), 2),
                "selected_sp500": top_sp,
                "selected_ibex": top_ibex,
                "momentum_sp500_top": {t: round(float(mom_sp_t[t]), 4) for t in top_sp},
                "momentum_ibex_top": {t: round(float(mom_ibex_t[t]), 4) for t in top_ibex},
                "orders_to_sell": orders_to_sell,
                "orders_to_buy": orders_to_buy,
                "_note": "Backtest entry. Commissions excluded.",
            })

        # Monthly log for stats
        # Use the most recent EUR/USD rate available for valuing US positions
        eur_usd_month = get_rate_on_or_before(eurusd_rates, date)
        cur_val = sum(
            _position_value_eur(t, info, prices_sp.loc[date], prices_ibex.loc[date], eur_usd_month)
            for t, info in holdings.items()
        )
        monthly_log.append({"date": date, "value_eur": cash_eur + cur_val})

    # ----- Year-end tax adjustments -----
    df_log = pd.DataFrame(monthly_log).set_index("date")
    yearly_summary = []
    total_taxes = 0.0
    for year in range(2019, 2026):
        year_data = df_log[df_log.index.year == year]
        if len(year_data) == 0:
            continue
        valor_ini = (df_log[df_log.index < f"{year}-01-01"]["value_eur"].iloc[-1]
                     if year > 2019 else INITIAL_CAPITAL)
        valor_fin_bruto = year_data["value_eur"].iloc[-1]
        realized = yearly_realized_gain.get(year, 0)
        tax = calc_irpf(realized, year)
        total_taxes += tax
        yearly_summary.append({
            "year": year,
            "start": valor_ini,
            "end_gross": valor_fin_bruto,
            "end_net": valor_fin_bruto - tax,
            "return_net": (valor_fin_bruto - tax) / valor_ini - 1,
            "tax": tax,
            "realized_gain": realized,
        })
        df_log.loc[df_log.index >= f"{year+1}-01-01", "value_eur"] -= tax if year < 2025 else 0

    valor_serie = df_log["value_eur"].copy()
    final_tax_2025 = calc_irpf(yearly_realized_gain.get(2025, 0), 2025)
    valor_serie.iloc[-1] -= final_tax_2025

    returns_net = valor_serie.pct_change()
    returns_net.iloc[0] = valor_serie.iloc[0] / INITIAL_CAPITAL - 1
    n_years = len(returns_net) / 12

    final_capital = float(valor_serie.iloc[-1])
    total_return = final_capital / INITIAL_CAPITAL - 1
    cagr = (final_capital / INITIAL_CAPITAL) ** (1 / n_years) - 1
    vol = returns_net.std() * np.sqrt(12)
    sharpe = returns_net.mean() / returns_net.std() * np.sqrt(12)
    max_dd = ((valor_serie / valor_serie.cummax()) - 1).min()

    # ----- Print summary table -----
    print(f"\n{'Year':<6}{'V.start':>12}{'V.end net':>14}{'Return net':>13}"
          f"{'Tax':>12}{'Realized':>14}")
    print("-" * 78)
    for s in yearly_summary:
        print(f"{s['year']:<6}{s['start']:>11,.0f}€{s['end_net']:>13,.0f}€"
              f"{s['return_net']:>+12.2%}{s['tax']:>11,.0f}€{s['realized_gain']:>13,.0f}€")

    print(f"\n{'=' * 78}")
    print("FINAL RESULTS (2019-2025, 7 years, net of Spanish IRPF)")
    print('=' * 78)
    print(f"  Initial capital:       {INITIAL_CAPITAL:>10,.2f} EUR")
    print(f"  Final capital:         {final_capital:>10,.2f} EUR")
    print(f"  Total return:          {total_return * 100:>+10.2f}%")
    print(f"  CAGR (net):            {cagr * 100:>+10.2f}%")
    print(f"  Annualized volatility: {vol * 100:>10.2f}%")
    print(f"  Sharpe ratio (rf=0):   {sharpe:>10.2f}")
    print(f"  Max drawdown:          {max_dd * 100:>10.2f}%")
    print(f"  Total taxes:           {total_taxes + final_tax_2025:>10,.2f} EUR")
    print("  Note: commissions excluded from backtest (recorded per-trade in real execution).")

    # ----- Save JSON files in production format -----
    print(f"\n[5/5] Writing output files to {BACKTESTS_DIR}/...")

    # Convert holdings to JSON-friendly dict
    last_date = rebalance_dates[-1] if rebalance_dates else None
    final_eur_usd = get_rate_on_or_before(eurusd_rates, dates[-1])
    final_positions = {}
    for t, info in holdings.items():
        final_positions[t] = {
            "shares": round(info["shares"], 4),
            "avg_price_eur": round(info["avg_price_eur"], 4),
            "market": info["market"],
            "buy_date": info["buy_date"],
        }

    save_backtest_portfolio(
        cash_eur=cash_eur,
        positions=final_positions,
        last_rebalance=last_date.strftime("%Y-%m-%d") if last_date else None,
        initial_capital_eur=INITIAL_CAPITAL,
        net_capital_contributed_eur=INITIAL_CAPITAL,
    )
    print(f"      Wrote {BT_PORTFOLIO_FILE.name}")

    save_backtest_history(history_entries)
    print(f"      Wrote {BT_HISTORY_FILE.name} ({len(history_entries)} rebalance entries)")

    # ----- Save trades CSV -----
    trades_df = pd.DataFrame(trades_records)
    trades_df.to_csv(BT_TRADES_FILE, index=False)
    print(f"      Wrote {BT_TRADES_FILE.name} ({len(trades_df)} trades)")

    # ----- Save summary metrics as JSON for the markdown generator -----
    metrics = {
        "initial_capital_eur": INITIAL_CAPITAL,
        "final_capital_eur": round(final_capital, 2),
        "total_return": round(total_return, 4),
        "cagr": round(cagr, 4),
        "volatility": round(vol, 4),
        "sharpe": round(sharpe, 4),
        "max_drawdown": round(max_dd, 4),
        "total_taxes_eur": round(total_taxes + final_tax_2025, 2),
        "n_rebalances": len(history_entries),
        "n_trades": len(trades_records),
        "yearly_summary": [
            {k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()}
            for s in yearly_summary
        ],
    }
    with open(BACKTESTS_DIR / "backtest-metrics.json", "w") as f:
        json.dump(metrics, f, indent=2, default=str)
    print(f"      Wrote backtest-metrics.json")

    print("\nDone. Now run:")
    print("    python scripts/build_backtest_dashboard.py   # generates dashboard image")
    print("    python scripts/build_backtest_report.py      # generates results .md")


def _position_value_eur(ticker, info, prices_sp_row, prices_ibex_row, eur_usd):
    """Helper: compute EUR value of a position at given prices and FX rate."""
    if info["market"] == "SP":
        if ticker not in prices_sp_row.index:
            return info["shares"] * info["avg_price_eur"]
        return info["shares"] * prices_sp_row[ticker] / eur_usd
    else:
        if ticker not in prices_ibex_row.index:
            return info["shares"] * info["avg_price_eur"]
        return info["shares"] * prices_ibex_row[ticker]


if __name__ == "__main__":
    main()
