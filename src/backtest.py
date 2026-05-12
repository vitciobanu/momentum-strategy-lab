"""
================================================================================
HISTORICAL BACKTEST (2019-2025)
================================================================================
Reproduces the mixed USA/Spain momentum strategy on synthetic price data
calibrated to known historical annual returns.

The backtest uses pre-selection based on 2015-2018 momentum to avoid
look-ahead bias.

USAGE:
    python src/backtest.py
================================================================================
"""

import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from universe import CONFIG

# ============================================================================
# Synthetic price calibration data
# 
# These are approximate annual returns (2014-2025) for each stock, calibrated
# from publicly available historical data (Yahoo Finance, Macrotrends).
# Used to generate monthly prices that reproduce the known year-end behavior
# of each stock, including major events (COVID 2020, rate hikes 2022, etc).
#
# This is NOT the same as using real daily/monthly historical prices.
# For a production-grade backtest, replace this with actual historical data
# downloaded via yfinance.
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
    "EBRO":{"start":14,"ann":[0.05,0.10,0.15,0.10,-0.10,0.05,0.10,-0.05,0.0,0.05,0.10,0.10],"vol":0.04},
    "ANA": {"start":60,"ann":[0.10,0.20,0.15,0.10,-0.05,0.30,0.18,0.15,0.10,-0.05,-0.10,0.10],"vol":0.06},
    "BKT": {"start":7, "ann":[0.05,0.05,-0.10,0.40,-0.32,0.05,-0.30,0.40,0.05,0.45,0.30,0.45],"vol":0.07},
    "CABK":{"start":4.5,"ann":[-0.10,-0.20,-0.05,0.25,-0.35,-0.10,-0.25,1.10,0.45,0.50,0.55,0.55],"vol":0.09},
    "COL": {"start":6, "ann":[0.15,0.20,0.05,0.10,0.05,0.40,-0.05,0.10,-0.20,0.05,0.05,0.20],"vol":0.06},
    "SAN": {"start":7, "ann":[-0.20,-0.30,0.10,0.05,-0.27,0.20,-0.35,0.20,0.10,0.45,0.30,0.50],"vol":0.08},
}

SP500_CALIBRATION = {
    "BA":  {"start":130,  "ann":[-0.05,0.10,0.10,0.90,0.10,-0.05,-0.35,-0.05,-0.05,0.40,-0.30,0.10],"vol":0.10},
    "NVDA":{"start":0.4,  "ann":[0.30,0.65,2.27,0.82,-0.31,0.76,1.22,1.25,-0.50,2.40,1.71,0.45],"vol":0.12},
    "ADBE":{"start":60,   "ann":[0.25,0.30,0.10,0.70,0.27,0.45,0.55,0.15,-0.40,0.75,0.10,-0.10],"vol":0.08},
    "NFLX":{"start":49,   "ann":[-0.05,1.34,0.10,0.55,0.40,0.20,0.65,-0.10,-0.50,0.65,0.85,0.30],"vol":0.10},
    "AVGO":{"start":9.2,  "ann":[0.43,0.45,0.20,0.45,0.0,0.27,0.39,0.55,-0.16,1.04,1.10,0.30],"vol":0.09},
    "AMD": {"start":4,    "ann":[-0.55,-0.10,2.95,0.10,0.80,0.15,1.00,0.55,-0.55,1.30,-0.10,0.40],"vol":0.14},
    "MSFT":{"start":38,   "ann":[0.27,0.22,0.15,0.41,0.21,0.55,0.41,0.52,-0.28,0.58,0.12,0.20],"vol":0.06},
    "MCD": {"start":91,   "ann":[-0.05,0.30,0.05,0.45,0.05,0.15,0.10,0.30,-0.05,0.10,-0.05,0.05],"vol":0.04},
    "INTU":{"start":78,   "ann":[0.10,0.10,0.15,0.50,0.20,0.35,0.35,0.65,-0.40,0.55,0.05,0.05],"vol":0.07},
    "V":   {"start":53,   "ann":[0.18,0.18,0.05,0.46,0.16,0.43,0.17,0.0,-0.04,0.26,0.22,0.15],"vol":0.05},
    "DIS": {"start":76,   "ann":[0.27,0.13,-0.03,0.05,0.20,0.35,0.25,-0.15,-0.45,0.05,0.20,0.05],"vol":0.06},
    "NKE": {"start":45,   "ann":[0.20,0.30,-0.18,0.25,0.20,0.40,0.40,0.20,-0.30,0.0,-0.30,-0.10],"vol":0.06},
    "TSLA":{"start":14.6, "ann":[0.50,0.50,-0.10,0.45,0.07,0.26,7.43,0.50,-0.65,1.02,0.63,0.10],"vol":0.15},
    "BAC": {"start":17,   "ann":[0.15,-0.05,0.32,0.36,-0.16,0.45,-0.13,0.50,-0.25,0.05,0.35,0.30],"vol":0.07},
    "NOW": {"start":65,   "ann":[0.15,0.30,0.10,0.55,0.30,0.55,0.95,0.20,-0.40,0.80,0.50,0.10],"vol":0.09},
    "MA":  {"start":86,   "ann":[0.04,0.05,0.10,0.46,0.25,0.59,0.18,0.0,-0.03,0.23,0.22,0.15],"vol":0.05},
    "TXN": {"start":47,   "ann":[0.10,-0.05,0.50,0.45,-0.10,0.50,0.30,0.20,-0.10,0.05,0.20,0.15],"vol":0.06},
    "ACN": {"start":76,   "ann":[0.10,0.30,-0.05,0.40,0.0,0.55,0.30,0.55,-0.35,0.35,0.05,-0.05],"vol":0.06},
    "ABBV":{"start":65,   "ann":[0.10,-0.05,-0.10,0.55,0.25,-0.05,0.30,0.30,0.20,0.05,0.20,0.20],"vol":0.06},
    "CRM": {"start":55,   "ann":[0.15,0.30,0.10,0.50,0.30,0.20,0.40,0.15,-0.50,0.95,0.15,0.15],"vol":0.09},
}

# Spanish IRPF tax brackets per year (base del ahorro)
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
    COMM_IBEX = CONFIG["COMMISSION_IBEX_EUR"]
    COMM_SP = CONFIG["COMMISSION_SP500_USD"] / EUR_USD
    
    all_sim_dates = momentum_ibex.dropna().index.intersection(momentum_sp.dropna().index)
    all_sim_dates = all_sim_dates[all_sim_dates >= "2019-01-01"]
    rebalance_dates = [d for d in all_sim_dates if d.month in [1, 4, 7, 10]]
    
    cash = INITIAL_CAPITAL
    holdings = {}
    yearly_realized_gain = {}
    monthly_log = []
    total_commissions = 0.0
    
    for date in all_sim_dates:
        year = date.year
        is_rebalance = date in rebalance_dates
        n_ops = 0
        
        if is_rebalance:
            mom_sp_t = momentum_sp.loc[date].dropna()
            mom_ibex_t = momentum_ibex.loc[date].dropna()
            top_sp = mom_sp_t.nlargest(CONFIG["N_SP500_POSITIONS"]).index.tolist()
            top_ibex = mom_ibex_t.nlargest(CONFIG["N_IBEX_POSITIONS"]).index.tolist()
            new_top = top_sp + top_ibex
            
            for t in list(holdings.keys()):
                if t not in new_top:
                    n_shares, cost, market = holdings[t]
                    price = prices_sp.loc[date, t] if market == "SP" else prices_ibex.loc[date, t]
                    comm = COMM_SP if market == "SP" else COMM_IBEX
                    cash += n_shares * price - comm
                    total_commissions += comm
                    yearly_realized_gain[year] = yearly_realized_gain.get(year, 0) + n_shares * (price - cost) - comm
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
                    invest = target_per_sp - COMM_SP
                    if invest <= 0 or invest > cash: continue
                    holdings[t] = (invest / price, price, "SP")
                    cash -= invest + COMM_SP
                    total_commissions += COMM_SP
                    n_ops += 1
            
            for t in top_ibex:
                if t not in holdings:
                    price = prices_ibex.loc[date, t]
                    invest = target_per_ibex - COMM_IBEX
                    if invest <= 0 or invest > cash: continue
                    holdings[t] = (invest / price, price, "IBEX")
                    cash -= invest + COMM_IBEX
                    total_commissions += COMM_IBEX
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
    print(f"  Total commissions:     {total_commissions:>10,.2f} EUR")
    print(f"  Total taxes:           {total_taxes + calc_irpf(yearly_realized_gain.get(2025, 0), 2025):>10,.2f} EUR")

if __name__ == "__main__":
    main()
