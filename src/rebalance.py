"""
================================================================================
MOMENTUM 12-1 QUARTERLY REBALANCE — Mixed USA/Spain portfolio
================================================================================

Strategy: Buy past winners (top 4 from S&P 500, top 2 from IBEX 35 by 12-1
<<<<<<< HEAD
momentum) with fixed 67%/33% capital allocation. Rebalance every 3 months.

This script is your "decision maker". Each quarter:
1. Downloads recent monthly prices via yfinance
2. Computes 12-1 momentum for both universes
3. Compares your current portfolio with the new TOP 6
4. Prints the buy/sell orders you need to execute in IBKR
5. Saves a record in data/history.json

You then manually execute the orders in IBKR and update data/portfolio.json.
=======
momentum) with fixed 65%/30% capital allocation. Rebalance every 3 months.

This script is your "decision maker". Each quarter:
1. Downloads recent monthly prices via yfinance for the FULL universe
2. Computes 12-1 momentum for both markets independently
3. Compares your current portfolio with the new TOP 6
4. Prints buy/sell orders to execute in IBKR
5. Saves a record of the decision in data/history.json

You then execute the orders in IBKR and update data/portfolio.json with the
resulting positions and the actual commissions you paid.
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)

================================================================================
USAGE:
    python src/rebalance.py
================================================================================
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

<<<<<<< HEAD
# Allow importing from this directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from universe import IBEX_TOP20, SP500_TOP20, CONFIG
=======
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from universe import IBEX_35, SP500_LARGE_CAP, CONFIG
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)

# ============================================================================
# CONSTANTS
# ============================================================================

ROOT = Path(__file__).parent.parent
PORTFOLIO_FILE = ROOT / "data" / "portfolio.json"
HISTORY_FILE = ROOT / "data" / "history.json"

# ============================================================================
# PORTFOLIO PERSISTENCE
# ============================================================================

def load_portfolio():
    """Load current portfolio from data/portfolio.json.
<<<<<<< HEAD
    
    If the file does not exist, create it with default values (this happens
    only on the very first run when cloning the repo fresh)."""
=======

    If the file does not exist, create it with default values (this happens
    only on the very first run when cloning the repo fresh). The default
    initial capital is 2,000 EUR but should be set by the user editing
    portfolio.json directly BEFORE the first run.
    """
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    if not PORTFOLIO_FILE.exists():
        print(f"\n[!] {PORTFOLIO_FILE} not found. Creating with default values.")
        PORTFOLIO_FILE.parent.mkdir(parents=True, exist_ok=True)
        default = {
            "_account_type": "IBKR DEMO (Paper Trading)",
<<<<<<< HEAD
            "cash_eur": 0,
            "positions": {},
            "last_rebalance": None,
            "initial_capital_eur": 2000.0,
=======
            "initial_capital_eur": 2000.0,
            "cash_eur": 0,
            "positions": {},
            "last_rebalance": None,
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
        }
        with open(PORTFOLIO_FILE, "w") as f:
            json.dump(default, f, indent=2)
    with open(PORTFOLIO_FILE, "r") as f:
        data = json.load(f)
    # Remove comment keys (any key starting with _)
    return {k: v for k, v in data.items() if not k.startswith("_")}

def load_history():
    if not HISTORY_FILE.exists():
        return []
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_history(history):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, default=str)

# ============================================================================
# DATA DOWNLOAD
# ============================================================================

def download_universe(yahoo_tickers, label):
<<<<<<< HEAD
    """Download last 18 months of monthly prices for a list of tickers."""
    print(f"  Downloading {label} ({len(yahoo_tickers)} stocks)...")
    end = datetime.today()
    start = end - timedelta(days=18 * 31)
    
=======
    """Download last ~18 months of monthly prices for a list of tickers."""
    print(f"  Downloading {label}...")
    end = datetime.today()
    start = end - timedelta(days=18 * 31)

>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    data = yf.download(
        list(yahoo_tickers),
        start=start,
        end=end,
        interval="1mo",
        auto_adjust=True,
        progress=False,
        threads=True,
    )
<<<<<<< HEAD
    
=======

>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Close"]
    else:
        prices = data[["Close"]]
        prices.columns = list(yahoo_tickers)
<<<<<<< HEAD
    
    return prices

def download_current_prices(yahoo_tickers):
    """Get the latest daily close for each ticker."""
    data = yf.download(
        list(yahoo_tickers),
        period="5d",
=======

    return prices

def download_current_prices(yahoo_tickers):
    """Get the latest available daily close for each ticker.

    Uses the last NON-NaN value per ticker, so tickers that didn't trade on
    the most recent day (holidays, suspensions, late data) still return a
    usable price from a recent prior day.
    """
    data = yf.download(
        list(yahoo_tickers),
        period="10d",
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=True,
    )
    if isinstance(data.columns, pd.MultiIndex):
<<<<<<< HEAD
        return data["Close"].iloc[-1]
    return pd.Series({list(yahoo_tickers)[0]: data["Close"].iloc[-1]})
=======
        # For each ticker (column), get the last non-NaN close
        closes = data["Close"]
        # ffill propagates last valid value forward, then we take the very last row
        return closes.ffill().iloc[-1]
    # Single ticker case
    series = data["Close"].dropna()
    if len(series) == 0:
        return pd.Series({list(yahoo_tickers)[0]: np.nan})
    return pd.Series({list(yahoo_tickers)[0]: series.iloc[-1]})
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)

def get_eur_usd_rate():
    """Get current EUR/USD exchange rate."""
    try:
        ticker = yf.Ticker("EURUSD=X")
        hist = ticker.history(period="5d")
<<<<<<< HEAD
        rate = hist["Close"].iloc[-1]
        return float(rate)
=======
        rate = float(hist["Close"].dropna().iloc[-1])
        return rate
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    except Exception as e:
        print(f"  [Warning] Could not fetch live EUR/USD rate: {e}")
        print(f"  Using reference: {CONFIG['EUR_USD_REFERENCE']}")
        return CONFIG["EUR_USD_REFERENCE"]

# ============================================================================
# MOMENTUM CALCULATION
# ============================================================================

def compute_momentum(prices):
<<<<<<< HEAD
    """
    Momentum 12-1: return from 12 months ago to 1 month ago.
=======
    """Momentum 12-1: return from 12 months ago to 1 month ago.
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    Skip the most recent month to avoid short-term reversal noise.
    """
    if len(prices) < 13:
        raise ValueError(f"Need at least 13 months of prices, got {len(prices)}")
<<<<<<< HEAD
    
    p_t_minus_1 = prices.iloc[-2]    # last closed month
    p_t_minus_12 = prices.iloc[-13]  # 12 months before that
    
=======

    p_t_minus_1 = prices.iloc[-2]    # last closed month
    p_t_minus_12 = prices.iloc[-13]  # 12 months before that

>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    momentum = (p_t_minus_1 / p_t_minus_12) - 1
    return momentum.dropna().sort_values(ascending=False)

# ============================================================================
# REBALANCE LOGIC
# ============================================================================

<<<<<<< HEAD
def compute_rebalance(portfolio, mom_sp, mom_ibex, prices_sp, prices_ibex, eur_usd):
    """
    Decide what to buy and sell.
    
    Targets:
    - Top N_SP500_POSITIONS from S&P 500, weighted 67% total, equal-weight within
    - Top N_IBEX_POSITIONS from IBEX, weighted 33% total, equal-weight within
    """
    cash_eur = portfolio["cash_eur"]
    positions = portfolio["positions"]  # {ticker: {shares, avg_price_eur, market}}
    
    # Current portfolio valuation in EUR
    current_value = 0.0
    position_values = {}
    for ticker, info in positions.items():
        market = info.get("market", "SP")  # default SP for backward compat
        if market == "IBEX":
            price = prices_ibex.get(ticker, info["avg_price_eur"])
            value_eur = info["shares"] * price
        else:
            price_usd = prices_sp.get(ticker, info["avg_price_eur"] * eur_usd)
            value_eur = info["shares"] * price_usd / eur_usd
        position_values[ticker] = value_eur
        current_value += value_eur
    
    total_value = cash_eur + current_value
    
    # Targets
=======
def compute_position_value_eur(ticker, info, current_prices_sp_usd,
                                current_prices_ibex_eur, eur_usd):
    """Compute current EUR value of a position, handling missing prices gracefully."""
    market = info.get("market", "SP")
    shares = info["shares"]
    if market == "IBEX":
        price = current_prices_ibex_eur.get(ticker)
        if price is None or pd.isna(price):
            # Fall back to last known cost basis if live price unavailable
            return shares * info["avg_price_eur"]
        return shares * price
    else:
        price_usd = current_prices_sp_usd.get(ticker)
        if price_usd is None or pd.isna(price_usd):
            return shares * info["avg_price_eur"]
        return shares * price_usd / eur_usd

def compute_rebalance(portfolio, mom_sp, mom_ibex,
                      current_prices_sp_usd, current_prices_ibex_eur, eur_usd):
    """Decide what to buy and sell.

    Targets:
    - Top N_SP500_POSITIONS from S&P 500, weighted 65% total
    - Top N_IBEX_POSITIONS from IBEX, weighted 30% total
    - Equal weight within each region
    """
    cash_eur = portfolio["cash_eur"]
    positions = portfolio["positions"]
    allow_fractional = CONFIG["ALLOW_FRACTIONAL_SHARES"]

    # 1. Current portfolio valuation in EUR
    current_value = 0.0
    position_values_eur = {}
    for ticker, info in positions.items():
        value_eur = compute_position_value_eur(
            ticker, info, current_prices_sp_usd, current_prices_ibex_eur, eur_usd
        )
        position_values_eur[ticker] = value_eur
        current_value += value_eur

    total_value = cash_eur + current_value

    # 2. Target allocations
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    n_sp = CONFIG["N_SP500_POSITIONS"]
    n_ibex = CONFIG["N_IBEX_POSITIONS"]
    target_sp_total = total_value * CONFIG["WEIGHT_SP500"]
    target_ibex_total = total_value * CONFIG["WEIGHT_IBEX"]
<<<<<<< HEAD
    target_per_sp = target_sp_total / n_sp
    target_per_ibex = target_ibex_total / n_ibex
    
    # Top selection by momentum
    new_top_sp = mom_sp.head(n_sp).index.tolist()
    new_top_ibex = mom_ibex.head(n_ibex).index.tolist()
    new_top_all = new_top_sp + new_top_ibex
    
    # SELL: positions no longer in top
=======
    target_per_sp_eur = target_sp_total / n_sp
    target_per_ibex_eur = target_ibex_total / n_ibex

    # 3. New TOP by momentum
    new_top_sp = mom_sp.head(n_sp).index.tolist()
    new_top_ibex = mom_ibex.head(n_ibex).index.tolist()
    new_top_all = new_top_sp + new_top_ibex

    # 4. SELL: positions no longer in top
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    to_sell = []
    for ticker, info in positions.items():
        if ticker not in new_top_all:
            market = info.get("market", "SP")
<<<<<<< HEAD
            if market == "IBEX":
                price = prices_ibex.get(ticker, info["avg_price_eur"])
                value_eur = info["shares"] * price
                commission_eur = CONFIG["COMMISSION_IBEX_EUR"]
            else:
                price_usd = prices_sp.get(ticker, 0)
                value_eur = info["shares"] * price_usd / eur_usd
                commission_eur = CONFIG["COMMISSION_SP500_USD"] / eur_usd
                price = price_usd  # show in USD for SP500 orders
            
            cost_basis_eur = info["shares"] * info["avg_price_eur"]
            gain_eur = value_eur - cost_basis_eur - commission_eur
            gain_pct = (value_eur / cost_basis_eur - 1) * 100 if cost_basis_eur > 0 else 0
            
            to_sell.append({
                "ticker": ticker,
                "market": market,
                "shares": info["shares"],
                "price": price,
                "value_eur": value_eur,
                "gain_eur": gain_eur,
                "gain_pct": gain_pct,
                "currency": "EUR" if market == "IBEX" else "USD",
            })
    
    # BUY: tickers in new top that aren't in portfolio
    to_buy = []
    
    # S&P 500 buys
    for ticker in new_top_sp:
        if ticker not in positions:
            price_usd = prices_sp.get(ticker)
            if price_usd is None or pd.isna(price_usd):
                continue
            # Target in EUR, convert to USD for share calculation
            target_eur = target_per_sp
            commission_eur = CONFIG["COMMISSION_SP500_USD"] / eur_usd
            invest_eur = target_eur - commission_eur
            invest_usd = invest_eur * eur_usd
            n_shares = int(invest_usd / price_usd)
            if n_shares == 0:
                continue
            value_usd = n_shares * price_usd
            value_eur = value_usd / eur_usd
            to_buy.append({
                "ticker": ticker,
                "market": "SP",
                "shares": n_shares,
                "price_usd": price_usd,
                "value_usd": value_usd,
                "value_eur": value_eur,
                "momentum": mom_sp[ticker] * 100,
                "currency": "USD",
            })
    
    # IBEX buys
    for ticker in new_top_ibex:
        if ticker not in positions:
            price = prices_ibex.get(ticker)
            if price is None or pd.isna(price):
                continue
            commission_eur = CONFIG["COMMISSION_IBEX_EUR"]
            invest_eur = target_per_ibex - commission_eur
            n_shares = int(invest_eur / price)
            if n_shares == 0:
                continue
            value_eur = n_shares * price
            to_buy.append({
                "ticker": ticker,
                "market": "IBEX",
                "shares": n_shares,
                "price": price,
                "value_eur": value_eur,
                "momentum": mom_ibex[ticker] * 100,
                "currency": "EUR",
            })
    
    return {
        "total_value": total_value,
        "cash_eur": cash_eur,
        "position_values": position_values,
=======
            shares = info["shares"]
            if market == "IBEX":
                price = current_prices_ibex_eur.get(ticker)
                if price is None or pd.isna(price):
                    price = info["avg_price_eur"]
                value_eur = shares * price
                currency = "EUR"
            else:
                price_usd = current_prices_sp_usd.get(ticker)
                if price_usd is None or pd.isna(price_usd):
                    price_usd = info["avg_price_eur"] * eur_usd
                value_eur = shares * price_usd / eur_usd
                price = price_usd
                currency = "USD"

            cost_basis_eur = shares * info["avg_price_eur"]
            gain_eur = value_eur - cost_basis_eur
            gain_pct = (value_eur / cost_basis_eur - 1) * 100 if cost_basis_eur > 0 else 0

            to_sell.append({
                "ticker": ticker, "market": market, "shares": shares,
                "price": price, "value_eur": value_eur,
                "gain_eur": gain_eur, "gain_pct": gain_pct,
                "currency": currency,
            })

    # 5. BUY: new tickers in top that aren't currently held
    to_buy = []
    warnings = []

    # S&P 500 buys
    for ticker in new_top_sp:
        if ticker not in positions:
            price_usd = current_prices_sp_usd.get(ticker)
            if price_usd is None or pd.isna(price_usd):
                warnings.append(f"  [!] No live price for {ticker} (SP500). Skipping.")
                continue

            target_eur = target_per_sp_eur
            invest_usd = target_eur * eur_usd

            if allow_fractional:
                n_shares = invest_usd / price_usd
                # Round to 4 decimals (IBKR typically allows this precision)
                n_shares = round(n_shares, 4)
            else:
                n_shares = int(invest_usd / price_usd)
                if n_shares == 0:
                    warnings.append(
                        f"  [!] Cannot afford 1 share of {ticker} at {price_usd:.2f} USD "
                        f"(target ~ {target_eur:.0f} EUR). Consider enabling fractional shares."
                    )
                    continue

            value_usd = n_shares * price_usd
            value_eur = value_usd / eur_usd
            to_buy.append({
                "ticker": ticker, "market": "SP",
                "shares": n_shares, "price_usd": price_usd,
                "value_usd": value_usd, "value_eur": value_eur,
                "momentum": mom_sp[ticker] * 100, "currency": "USD",
            })

    # IBEX buys
    for ticker in new_top_ibex:
        if ticker not in positions:
            price_eur = current_prices_ibex_eur.get(ticker)
            if price_eur is None or pd.isna(price_eur):
                warnings.append(f"  [!] No live price for {ticker} (IBEX). Skipping.")
                continue

            target_eur = target_per_ibex_eur

            if allow_fractional:
                n_shares = round(target_eur / price_eur, 4)
            else:
                n_shares = int(target_eur / price_eur)
                if n_shares == 0:
                    warnings.append(
                        f"  [!] Cannot afford 1 share of {ticker} at {price_eur:.2f} EUR "
                        f"(target ~ {target_eur:.0f} EUR). Consider enabling fractional shares."
                    )
                    continue

            value_eur = n_shares * price_eur
            to_buy.append({
                "ticker": ticker, "market": "IBEX",
                "shares": n_shares, "price": price_eur,
                "value_eur": value_eur,
                "momentum": mom_ibex[ticker] * 100, "currency": "EUR",
            })

    return {
        "total_value": total_value,
        "cash_eur": cash_eur,
        "position_values_eur": position_values_eur,
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
        "new_top_sp": new_top_sp,
        "new_top_ibex": new_top_ibex,
        "to_sell": to_sell,
        "to_buy": to_buy,
<<<<<<< HEAD
=======
        "warnings": warnings,
        "target_per_sp_eur": target_per_sp_eur,
        "target_per_ibex_eur": target_per_ibex_eur,
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    }

# ============================================================================
# REPORTING
# ============================================================================

<<<<<<< HEAD
def print_report(plan, portfolio, mom_sp, mom_ibex, prices_sp, prices_ibex, eur_usd):
    today = datetime.today().strftime("%Y-%m-%d")
    
    print("\n" + "="*78)
    print(f"  QUARTERLY REBALANCE PLAN — {today}")
    print(f"  Strategy: Momentum 12-1, top {CONFIG['N_SP500_POSITIONS']} S&P + "
          f"top {CONFIG['N_IBEX_POSITIONS']} IBEX")
    print(f"  Reference: 1 EUR = {eur_usd:.4f} USD")
    print("="*78)
    
=======
def print_report(plan, portfolio, mom_sp, mom_ibex,
                 current_prices_sp_usd, current_prices_ibex_eur, eur_usd):
    today = datetime.today().strftime("%Y-%m-%d")
    fractional = "fractional shares ON" if CONFIG["ALLOW_FRACTIONAL_SHARES"] else "whole shares only"

    print("\n" + "="*78)
    print(f"  QUARTERLY REBALANCE PLAN — {today}")
    print(f"  Strategy: Momentum 12-1, top {CONFIG['N_SP500_POSITIONS']} S&P + "
          f"top {CONFIG['N_IBEX_POSITIONS']} IBEX  ({fractional})")
    print(f"  Reference: 1 EUR = {eur_usd:.4f} USD")
    print("="*78)

>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    # Current state
    print(f"\n>> CURRENT PORTFOLIO STATE")
    print(f"   Cash:                 {portfolio['cash_eur']:>10,.2f} EUR")
    if portfolio["positions"]:
        print(f"   Open positions:       {len(portfolio['positions'])}")
        for t, info in portfolio["positions"].items():
            market = info.get("market", "SP")
<<<<<<< HEAD
            value_eur = plan["position_values"].get(t, 0)
            gain_pct = (value_eur / (info["shares"] * info["avg_price_eur"]) - 1) * 100 if info["avg_price_eur"] > 0 else 0
            print(f"     {t:6s} [{market:4s}]  {info['shares']:>5} shares  "
                  f"avg {info['avg_price_eur']:>8.3f} EUR  "
                  f"value {value_eur:>8,.2f} EUR  ({gain_pct:+.2f}%)")
    else:
        print(f"   (No positions — fresh portfolio)")
    print(f"   TOTAL VALUE:          {plan['total_value']:>10,.2f} EUR")
    
    # Momentum rankings
    print(f"\n>> MOMENTUM RANKING — S&P 500 TOP 20")
    for i, (ticker, mom) in enumerate(mom_sp.items(), 1):
        price = prices_sp.get(ticker, np.nan)
        marker = " <- SELECTED" if i <= CONFIG["N_SP500_POSITIONS"] else ""
        print(f"   #{i:<3}  {ticker:6s}  mom: {mom*100:>+7.2f}%  "
              f"price: {price:>9.2f} USD{marker}")
    
    print(f"\n>> MOMENTUM RANKING — IBEX 35 TOP 20")
    for i, (ticker, mom) in enumerate(mom_ibex.items(), 1):
        price = prices_ibex.get(ticker, np.nan)
        marker = " <- SELECTED" if i <= CONFIG["N_IBEX_POSITIONS"] else ""
        print(f"   #{i:<3}  {ticker:6s}  mom: {mom*100:>+7.2f}%  "
              f"price: {price:>9.3f} EUR{marker}")
    
    # Orders
    print(f"\n>> IBKR ORDERS TO EXECUTE")
    print("-"*78)
    
=======
            value_eur = plan["position_values_eur"].get(t, 0)
            cost_eur = info["shares"] * info["avg_price_eur"]
            gain_pct = (value_eur / cost_eur - 1) * 100 if cost_eur > 0 else 0
            print(f"     {t:6s} [{market:4s}]  {info['shares']:>8.4f} shares  "
                  f"avg {info['avg_price_eur']:>9.3f} EUR  "
                  f"value {value_eur:>9,.2f} EUR  ({gain_pct:+.2f}%)")
    else:
        print(f"   (No positions — fresh portfolio)")
    print(f"   TOTAL VALUE:          {plan['total_value']:>10,.2f} EUR")
    print(f"   Target per SP500 pos: {plan['target_per_sp_eur']:>10,.2f} EUR")
    print(f"   Target per IBEX  pos: {plan['target_per_ibex_eur']:>10,.2f} EUR")

    # Momentum rankings — top 15
    def _print_ranking(mom_series, prices_series, n_selected, currency_label, market_name, is_usd=False):
        n_total = len(mom_series)
        print(f"\n>> MOMENTUM RANKING — {market_name} ({n_total} stocks, showing top 15)")
        for i, (ticker, mom) in enumerate(mom_series.head(15).items(), 1):
            price = prices_series.get(ticker, np.nan)
            marker = " <- SELECTED" if i <= n_selected else ""
            price_str = f"{price:>9.3f}" if not pd.isna(price) else "      n/a"
            print(f"   #{i:<3}  {ticker:6s}  mom: {mom*100:>+8.2f}%  "
                  f"price: {price_str} {currency_label}{marker}")
        if n_total > 15:
            print(f"   ... ({n_total - 15} more stocks not shown)")

    _print_ranking(mom_sp, current_prices_sp_usd, CONFIG["N_SP500_POSITIONS"],
                   "USD", "S&P 500 LARGE CAP")
    _print_ranking(mom_ibex, current_prices_ibex_eur, CONFIG["N_IBEX_POSITIONS"],
                   "EUR", "IBEX 35")

    # Orders
    print(f"\n>> IBKR ORDERS TO EXECUTE")
    print("-"*78)

>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    if plan["to_sell"]:
        print(f"\n  SELL ({len(plan['to_sell'])} orders) — execute FIRST to free cash:")
        for s in plan["to_sell"]:
            if s["market"] == "IBEX":
<<<<<<< HEAD
                print(f"    SELL  {s['shares']:>4} {s['ticker']:6s} (BME)  @ MARKET   "
                      f"ref: {s['price']:>7.3f} EUR  ->  {s['value_eur']:>9,.2f} EUR"
                      f"   P&L: {s['gain_eur']:+8.2f} EUR ({s['gain_pct']:+.2f}%)")
            else:
                print(f"    SELL  {s['shares']:>4} {s['ticker']:6s} (US)   @ MARKET   "
                      f"ref: {s['price']:>7.2f} USD  ->  {s['value_eur']:>9,.2f} EUR"
                      f"   P&L: {s['gain_eur']:+8.2f} EUR ({s['gain_pct']:+.2f}%)")
    else:
        print(f"\n  SELL: (no sales this quarter)")
    
=======
                print(f"    SELL  {s['shares']:>9.4f} {s['ticker']:6s} (BME)  @ MARKET   "
                      f"ref: {s['price']:>9.3f} EUR  -> {s['value_eur']:>9,.2f} EUR"
                      f"   P&L: {s['gain_eur']:+9.2f} EUR ({s['gain_pct']:+.2f}%)")
            else:
                print(f"    SELL  {s['shares']:>9.4f} {s['ticker']:6s} (US)   @ MARKET   "
                      f"ref: {s['price']:>9.3f} USD  -> {s['value_eur']:>9,.2f} EUR"
                      f"   P&L: {s['gain_eur']:+9.2f} EUR ({s['gain_pct']:+.2f}%)")
    else:
        print(f"\n  SELL: (no sales this quarter)")

>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    # Held positions
    held = [t for t in portfolio["positions"]
            if t in plan["new_top_sp"] + plan["new_top_ibex"]]
    if held:
        print(f"\n  HOLD ({len(held)}):")
        for t in held:
            print(f"    HOLD  {t}")
<<<<<<< HEAD
    
=======

>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    if plan["to_buy"]:
        print(f"\n  BUY ({len(plan['to_buy'])} orders) — execute SECOND with available cash:")
        for b in plan["to_buy"]:
            if b["market"] == "IBEX":
<<<<<<< HEAD
                print(f"    BUY   {b['shares']:>4} {b['ticker']:6s} (BME)  @ MARKET   "
                      f"ref: {b['price']:>7.3f} EUR  ->  {b['value_eur']:>9,.2f} EUR"
                      f"   momentum: {b['momentum']:+.2f}%")
            else:
                print(f"    BUY   {b['shares']:>4} {b['ticker']:6s} (US)   @ MARKET   "
                      f"ref: {b['price_usd']:>7.2f} USD  ->  {b['value_eur']:>9,.2f} EUR"
                      f"   momentum: {b['momentum']:+.2f}%")
    else:
        print(f"\n  BUY: (no purchases this quarter)")
    
    # Economic summary
    n_ibex_ops = sum(1 for s in plan["to_sell"] if s["market"] == "IBEX") + \
                 sum(1 for b in plan["to_buy"] if b["market"] == "IBEX")
    n_sp_ops = sum(1 for s in plan["to_sell"] if s["market"] == "SP") + \
               sum(1 for b in plan["to_buy"] if b["market"] == "SP")
    commission_total_eur = (n_ibex_ops * CONFIG["COMMISSION_IBEX_EUR"] +
                            n_sp_ops * CONFIG["COMMISSION_SP500_USD"] / eur_usd)
    
    total_sell = sum(s["value_eur"] for s in plan["to_sell"])
    total_buy = sum(b["value_eur"] for b in plan["to_buy"])
    
    print(f"\n>> ECONOMIC SUMMARY")
    print(f"   Total sells:          {total_sell:>10,.2f} EUR ({n_ibex_ops + n_sp_ops} ops if counting sells separately)")
    print(f"   IBEX operations:      {n_ibex_ops} x {CONFIG['COMMISSION_IBEX_EUR']} EUR = "
          f"{n_ibex_ops * CONFIG['COMMISSION_IBEX_EUR']:.2f} EUR")
    print(f"   S&P 500 operations:   {n_sp_ops} x {CONFIG['COMMISSION_SP500_USD']} USD = "
          f"{n_sp_ops * CONFIG['COMMISSION_SP500_USD'] / eur_usd:.2f} EUR")
    print(f"   Total commissions:    {commission_total_eur:>10,.2f} EUR")
    print(f"   Estimated final cash: "
          f"{portfolio['cash_eur'] + total_sell - total_buy - commission_total_eur:>10,.2f} EUR")
    
=======
                print(f"    BUY   {b['shares']:>9.4f} {b['ticker']:6s} (BME)  @ MARKET   "
                      f"ref: {b['price']:>9.3f} EUR  -> {b['value_eur']:>9,.2f} EUR"
                      f"   mom: {b['momentum']:+.2f}%")
            else:
                print(f"    BUY   {b['shares']:>9.4f} {b['ticker']:6s} (US)   @ MARKET   "
                      f"ref: {b['price_usd']:>9.3f} USD  -> {b['value_eur']:>9,.2f} EUR"
                      f"   mom: {b['momentum']:+.2f}%")
    else:
        print(f"\n  BUY: (no purchases this quarter)")

    if plan["warnings"]:
        print(f"\n  WARNINGS:")
        for w in plan["warnings"]:
            print(w)

    # Economic summary (no commissions — user records actuals manually)
    total_sell = sum(s["value_eur"] for s in plan["to_sell"])
    total_buy = sum(b["value_eur"] for b in plan["to_buy"])
    n_ops_total = len(plan["to_sell"]) + len(plan["to_buy"])

    print(f"\n>> ECONOMIC SUMMARY (before commissions)")
    print(f"   Total sells proceeds:  {total_sell:>10,.2f} EUR")
    print(f"   Total buys cost:       {total_buy:>10,.2f} EUR")
    print(f"   Number of operations:  {n_ops_total}")
    print(f"   Estimated final cash:  "
          f"{portfolio['cash_eur'] + total_sell - total_buy:>10,.2f} EUR  "
          f"(BEFORE subtracting actual commissions paid)")

>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    print("\n" + "="*78)
    print("  NEXT STEPS")
    print("="*78)
    print("""
  1. Open IBKR (TWS or Client Portal)
  2. Execute orders in this order:
     - SELLS first (to free cash)
     - BUYS second (use the freed cash)
     - Order type: MARKET during liquid hours
     - Madrid (BME): 10:00-17:30 CET
     - US Markets: 15:30-22:00 CET (regular session)
<<<<<<< HEAD
  3. After all orders are filled, update data/portfolio.json:
     - cash_eur: your real EUR balance in IBKR
     - positions: shares and avg_price_eur for each held ticker
       (for SP500 stocks: avg_price_eur = avg_price_usd / current_eur_usd_rate)
     - last_rebalance: today's date
  4. Next rebalance: 3 months from now, between day 5-10
=======
  3. After all orders are filled, update data/portfolio.json with the actual
     execution results from IBKR:
     - cash_eur: your real EUR balance after the rebalance
     - positions: shares, avg_price_eur, market, buy_date, commission_paid_eur
       (for SP500 positions: avg_price_eur = avg_price_usd / eur_usd_rate_at_trade)
     - last_rebalance: today's date
  4. Commit the updated portfolio.json and history.json to the repo.
  5. Next rebalance: 3 months from now, between day 5-10 of Jan/Apr/Jul/Oct.
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
""")

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*78)
    print("  MOMENTUM 12-1 QUARTERLY REBALANCE")
    print(f"  {datetime.today().strftime('%Y-%m-%d %H:%M')}")
    print("="*78)
<<<<<<< HEAD
    
    # 1. Load portfolio
    portfolio = load_portfolio()
    is_first_run = len(portfolio.get("positions", {})) == 0 and portfolio.get("cash_eur", 0) == 0
    
    if is_first_run:
        print("\n[!] First run detected. Initializing portfolio with 2,000 EUR.")
        print("    Edit data/portfolio.json to change initial capital if needed.")
        portfolio["cash_eur"] = 2000.0
        portfolio["positions"] = {}
    
    # 2. Download EUR/USD rate
    print(f"\n[1/4] Fetching EUR/USD exchange rate...")
    eur_usd = get_eur_usd_rate()
    print(f"      1 EUR = {eur_usd:.4f} USD")
    
    # 3. Download prices
    print(f"\n[2/4] Downloading monthly prices...")
    try:
        prices_sp_monthly = download_universe(SP500_TOP20.values(), "S&P 500 TOP 20")
        prices_ibex_monthly = download_universe(IBEX_TOP20.values(), "IBEX TOP 20")
        
        # Rename columns from Yahoo tickers back to short names
        sp_rename = {v: k for k, v in SP500_TOP20.items()}
        ibex_rename = {v: k for k, v in IBEX_TOP20.items()}
        prices_sp_monthly = prices_sp_monthly.rename(columns=sp_rename)
        prices_ibex_monthly = prices_ibex_monthly.rename(columns=ibex_rename)
        
        # Current daily prices
        prices_sp_now = download_current_prices(SP500_TOP20.values())
        prices_ibex_now = download_current_prices(IBEX_TOP20.values())
        prices_sp_now.index = [sp_rename.get(t, t) for t in prices_sp_now.index]
        prices_ibex_now.index = [ibex_rename.get(t, t) for t in prices_ibex_now.index]
    except Exception as e:
        print(f"\n[ERROR] Failed to download prices: {e}")
        sys.exit(1)
    
    print(f"      S&P 500: {len(prices_sp_monthly)} months, "
          f"IBEX: {len(prices_ibex_monthly)} months")
    
=======

    # 1. Load portfolio
    portfolio = load_portfolio()
    initial_capital = portfolio.get("initial_capital_eur", 2000.0)
    is_first_run = (len(portfolio.get("positions", {})) == 0
                    and portfolio.get("cash_eur", 0) == 0)

    if is_first_run:
        print(f"\n[!] First run detected. Initializing cash with "
              f"initial_capital_eur = {initial_capital:,.2f} EUR")
        print("    (To change this, edit data/portfolio.json before re-running)")
        portfolio["cash_eur"] = initial_capital
        portfolio["positions"] = {}

    # 2. EUR/USD rate
    print(f"\n[1/4] Fetching EUR/USD exchange rate...")
    eur_usd = get_eur_usd_rate()
    print(f"      1 EUR = {eur_usd:.4f} USD")

    # 3. Download prices
    print(f"\n[2/4] Downloading monthly prices...")
    try:
        prices_sp_monthly = download_universe(
            SP500_LARGE_CAP.values(),
            f"S&P 500 large cap ({len(SP500_LARGE_CAP)} stocks)"
        )
        prices_ibex_monthly = download_universe(
            IBEX_35.values(),
            f"IBEX 35 ({len(IBEX_35)} stocks)"
        )

        # Rename columns from Yahoo tickers back to short names
        sp_rename = {v: k for k, v in SP500_LARGE_CAP.items()}
        ibex_rename = {v: k for k, v in IBEX_35.items()}
        prices_sp_monthly = prices_sp_monthly.rename(columns=sp_rename)
        prices_ibex_monthly = prices_ibex_monthly.rename(columns=ibex_rename)

        # Current daily prices (use ffill to recover from late/missing data)
        prices_sp_now = download_current_prices(SP500_LARGE_CAP.values())
        prices_ibex_now = download_current_prices(IBEX_35.values())
        prices_sp_now.index = [sp_rename.get(t, t) for t in prices_sp_now.index]
        prices_ibex_now.index = [ibex_rename.get(t, t) for t in prices_ibex_now.index]

        # Report any tickers with no live price
        nan_sp = [t for t in SP500_LARGE_CAP if pd.isna(prices_sp_now.get(t, np.nan))]
        nan_ibex = [t for t in IBEX_35 if pd.isna(prices_ibex_now.get(t, np.nan))]
        if nan_sp:
            print(f"      [!] No live price for {len(nan_sp)} SP500 ticker(s): "
                  f"{', '.join(nan_sp[:5])}{'...' if len(nan_sp) > 5 else ''}")
        if nan_ibex:
            print(f"      [!] No live price for {len(nan_ibex)} IBEX ticker(s): "
                  f"{', '.join(nan_ibex)}")
    except Exception as e:
        print(f"\n[ERROR] Failed to download prices: {e}")
        sys.exit(1)

    print(f"      S&P 500: {len(prices_sp_monthly)} months, "
          f"IBEX: {len(prices_ibex_monthly)} months")

>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    # 4. Compute momentum
    print(f"\n[3/4] Computing momentum 12-1...")
    mom_sp = compute_momentum(prices_sp_monthly)
    mom_ibex = compute_momentum(prices_ibex_monthly)
<<<<<<< HEAD
    
=======

>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    # 5. Plan rebalance
    print(f"\n[4/4] Calculating rebalance plan...")
    plan = compute_rebalance(portfolio, mom_sp, mom_ibex,
                             prices_sp_now, prices_ibex_now, eur_usd)
<<<<<<< HEAD
    
    # 6. Print report
    print_report(plan, portfolio, mom_sp, mom_ibex,
                 prices_sp_now, prices_ibex_now, eur_usd)
    
    # 7. Save to history
=======

    # 6. Print report
    print_report(plan, portfolio, mom_sp, mom_ibex,
                 prices_sp_now, prices_ibex_now, eur_usd)

    # 7. Save to history (append-only)
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
    history = load_history()
    history.append({
        "date": datetime.today().strftime("%Y-%m-%d"),
        "eur_usd_rate": float(eur_usd),
<<<<<<< HEAD
        "portfolio_value_eur": float(plan["total_value"]),
=======
        "portfolio_value_eur_before": float(plan["total_value"]),
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
        "cash_before_eur": float(portfolio["cash_eur"]),
        "selected_sp500": plan["new_top_sp"],
        "selected_ibex": plan["new_top_ibex"],
        "momentum_sp500_top": {t: float(mom_sp[t]) for t in plan["new_top_sp"]},
        "momentum_ibex_top": {t: float(mom_ibex[t]) for t in plan["new_top_ibex"]},
        "orders_to_sell": [
<<<<<<< HEAD
            {"ticker": s["ticker"], "market": s["market"], "shares": s["shares"],
             "ref_price": float(s["price"]), "value_eur": float(s["value_eur"])}
            for s in plan["to_sell"]
        ],
        "orders_to_buy": [
            {"ticker": b["ticker"], "market": b["market"], "shares": b["shares"],
             "ref_price": float(b.get("price", b.get("price_usd", 0))),
             "value_eur": float(b["value_eur"]),
             "currency": b["currency"]}
            for b in plan["to_buy"]
        ],
    })
    save_history(history)
    print(f"[i] History saved to {HISTORY_FILE.relative_to(ROOT)}")
    print(f"[i] Remember to update {PORTFOLIO_FILE.relative_to(ROOT)} after executing trades.\n")
=======
            {
                "ticker": s["ticker"], "market": s["market"],
                "shares": float(s["shares"]),
                "ref_price": float(s["price"]),
                "currency": s["currency"],
                "value_eur": float(s["value_eur"]),
            }
            for s in plan["to_sell"]
        ],
        "orders_to_buy": [
            {
                "ticker": b["ticker"], "market": b["market"],
                "shares": float(b["shares"]),
                "ref_price": float(b.get("price", b.get("price_usd", 0))),
                "currency": b["currency"],
                "value_eur": float(b["value_eur"]),
            }
            for b in plan["to_buy"]
        ],
        "_note": "Update this entry after execution with actual_commissions_eur "
                 "and actual_fill_prices if you want a complete record.",
    })
    save_history(history)
    print(f"[i] History saved to {HISTORY_FILE.relative_to(ROOT)}")
    print(f"[i] Remember to update {PORTFOLIO_FILE.relative_to(ROOT)} "
          f"after executing trades.\n")
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)

if __name__ == "__main__":
    main()
