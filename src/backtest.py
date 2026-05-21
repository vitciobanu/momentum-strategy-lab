"""
================================================================================
HISTORICAL BACKTEST (2019-2025) — REAL PRICE DATA
================================================================================
Reproduces the mixed USA/Spain momentum strategy using REAL historical prices
from data/monthly-historic-prices.csv and REAL historical EUR/USD rates from
data/eurusd.rates.csv.

Closes GitHub issue #10: Migrate backtest to use real price data instead of
synthetic data.

DATA SOURCES:
  data/monthly-historic-prices.csv: daily close prices for the universe stocks
    (English-month-name date format, e.g. "January 2, 2014")
  data/eurusd.rates.csv: daily EUR/USD rates (dd-mm-yy format)

The backtest resamples daily prices to end-of-month closes, computes momentum
12-1 (12-month return excluding the most recent month), and rebalances on the
first month of each quarter (Jan/Apr/Jul/Oct).

USAGE:
    python src/backtest.py                            # runs the simulation
    python scripts/build_backtest_dashboard.py        # builds the PNG dashboard
    python scripts/build_backtest_report.py           # builds the .md report

OUTPUTS (in backtests/):
    backtest-portfolio.json    Final portfolio state
    backtest-history.json      Rebalance-by-rebalance log
    backtest-trades.csv        One row per buy/sell with qty, amount, return
    backtest-metrics.json      Numeric summary (used by the report scripts)
================================================================================
"""

import pandas as pd
import numpy as np
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from universe import IBEX_35, US_LARGE_CAP, CONFIG

# ============================================================================
# PATHS
# ============================================================================
ROOT = Path(__file__).parent.parent
PRICES_FILE = ROOT / "data" / "monthly-historic-prices.csv"
EURUSD_FILE = ROOT / "data" / "eurusd.rates.csv"
BACKTESTS_DIR = ROOT / "backtests"
BACKTESTS_DIR.mkdir(exist_ok=True)
BT_PORTFOLIO_FILE = BACKTESTS_DIR / "backtest-portfolio.json"
BT_HISTORY_FILE = BACKTESTS_DIR / "backtest-history.json"
BT_TRADES_FILE = BACKTESTS_DIR / "backtest-trades.csv"
BT_METRICS_FILE = BACKTESTS_DIR / "backtest-metrics.json"

# ============================================================================
# TICKER MAPPING
# Some tickers in the CSV use non-standard short forms. Map them to the
# canonical form used by universe.py.
# ============================================================================
CSV_TICKER_RENAME = {
    "ICAG":  "IAG",     # International Airlines Group
    "REDE":  "RED",     # Redeia Corporación
    "SABE":  "SAB",     # Banco de Sabadell
    "PUIGb": "PUIG",    # Puig Brands
    "MT":    "MTS",     # ArcelorMittal
    "BRKb":  "BRK-B",   # Berkshire Hathaway Class B
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
    """Calculate Spanish IRPF on capital gains for a given year."""
    if gain <= 0:
        return 0.0
    tax = 0.0
    for low, high, rate in IRPF_BRACKETS[year]:
        if gain > low:
            tax += (min(gain, high) - low) * rate
    return tax


# ============================================================================
# DATA LOADING
# ============================================================================

def load_prices():
    """Load daily prices from data/monthly-historic-prices.csv and resample
    to month-end closes.

    Returns a wide DataFrame: index = month-end dates, columns = tickers.
    """
    if not PRICES_FILE.exists():
        raise FileNotFoundError(
            f"Prices file not found at {PRICES_FILE}. "
            f"Please ensure data/monthly-historic-prices.csv exists."
        )
    df = pd.read_csv(PRICES_FILE, encoding="latin-1")
    df["Date"] = pd.to_datetime(df["Date"], format="%B %d, %Y", errors="coerce")
    df = df.dropna(subset=["Date"])
    df["Ticker"] = df["Ticker"].replace(CSV_TICKER_RENAME)

    # Pivot to wide: rows=dates, cols=tickers
    wide = df.pivot_table(
        index="Date", columns="Ticker", values="Close", aggfunc="last"
    ).sort_index()

    # Resample to month-end closes (last observation of each month)
    monthly = wide.resample("ME").last()
    return monthly


def load_eurusd():
    """Load daily EUR/USD rates and return a Series indexed by date.

    The CSV may have either 2-digit (dd-mm-yy) or 4-digit (dd-mm-yyyy) years.
    Try both formats.
    """
    if not EURUSD_FILE.exists():
        raise FileNotFoundError(
            f"EUR/USD rates file not found at {EURUSD_FILE}. "
            f"Please ensure data/eurusd.rates.csv exists."
        )
    df = pd.read_csv(EURUSD_FILE)
    # Try dd-mm-yy first, fallback to dd-mm-yyyy
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%y", errors="coerce")
    mask_failed = df["Date"].isna()
    if mask_failed.any():
        df.loc[mask_failed, "Date"] = pd.to_datetime(
            df.loc[mask_failed, "Date"] if False else
            pd.read_csv(EURUSD_FILE)["Date"][mask_failed],
            format="%d-%m-%Y", errors="coerce"
        )
    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    return df.set_index("Date")["Close"]


def get_rate_on_or_before(rates_series, target_date):
    """Get the EUR/USD rate on or just before target_date (forward-fill)."""
    target = pd.Timestamp(target_date).normalize()
    available = rates_series[rates_series.index <= target]
    if len(available) == 0:
        return float(rates_series.iloc[0])
    return float(available.iloc[-1])


# ============================================================================
# JSON FILE WRITERS (matching production schema)
# ============================================================================

def save_backtest_portfolio(cash_eur, positions, last_rebalance,
                            initial_capital_eur, net_capital_contributed_eur):
    data = {
        "_account_type": "BACKTEST (Real prices 2019-2025)",
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
    with open(BT_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, default=str)


# ============================================================================
# HELPERS
# ============================================================================

def _position_value_eur(ticker, info, prices_row, ibex_set, eur_usd):
    """Compute EUR value of a position at the given month-end prices."""
    if ticker not in prices_row.index or pd.isna(prices_row[ticker]):
        # Fall back to cost basis if no live price (shouldn't happen with real data)
        return info["shares"] * info["avg_price_eur"]
    price = prices_row[ticker]
    if ticker in ibex_set:
        return info["shares"] * price  # IBEX prices are EUR
    else:
        return info["shares"] * price / eur_usd  # US prices are USD


# ============================================================================
# MAIN BACKTEST
# ============================================================================

def main():
    print("=" * 78)
    print("BACKTEST: Mixed USA/Spain Momentum Strategy (2019-2025)")
    print(f"Configuration: {CONFIG['N_SP500_POSITIONS']} US + {CONFIG['N_IBEX_POSITIONS']} IBEX")
    print(f"Weights: {CONFIG['WEIGHT_SP500']:.0%} US + {CONFIG['WEIGHT_IBEX']:.0%} IBEX "
          f"+ {CONFIG.get('CASH_RESERVE', 0):.0%} cash reserve")
    print("Data source: REAL historical prices from data/monthly-historic-prices.csv")
    print("=" * 78)

    # ----- Load data -----
    print("\n[1/5] Loading historical prices...")
    all_prices = load_prices()
    print(f"      Loaded {all_prices.shape[1]} tickers, "
          f"{all_prices.shape[0]} month-end dates "
          f"({all_prices.index.min().date()} to {all_prices.index.max().date()})")

    print("\n[2/5] Loading EUR/USD historical rates...")
    eurusd_rates = load_eurusd()
    print(f"      Loaded {len(eurusd_rates)} daily rates "
          f"({eurusd_rates.index.min().date()} to {eurusd_rates.index.max().date()})")

    # ----- Split into IBEX and US universes -----
    ibex_tickers = [t for t in IBEX_35 if t in all_prices.columns]
    us_tickers = [t for t in US_LARGE_CAP if t in all_prices.columns]
    print(f"\n[3/5] Universe coverage:")
    print(f"      IBEX:  {len(ibex_tickers)}/{len(IBEX_35)} tickers in dataset")
    print(f"      US:    {len(us_tickers)}/{len(US_LARGE_CAP)} tickers in dataset")
    missing_ibex = [t for t in IBEX_35 if t not in all_prices.columns]
    missing_us = [t for t in US_LARGE_CAP if t not in all_prices.columns]
    if missing_ibex:
        print(f"      [!] Missing IBEX: {', '.join(missing_ibex)}")
    if missing_us:
        print(f"      [!] Missing US ({len(missing_us)}): {', '.join(missing_us[:10])}"
              f"{'...' if len(missing_us) > 10 else ''}")

    prices_ibex = all_prices[ibex_tickers]
    prices_us = all_prices[us_tickers]
    ibex_set = set(ibex_tickers)

    # ----- Compute momentum 12-1 -----
    print("\n[4/5] Computing momentum 12-1 and running rebalances...")
    momentum_ibex = prices_ibex.shift(1) / prices_ibex.shift(12) - 1
    momentum_us = prices_us.shift(1) / prices_us.shift(12) - 1

    INITIAL_CAPITAL = 2000.0
    WEIGHT_SP = CONFIG["WEIGHT_SP500"]
    WEIGHT_IBEX = CONFIG["WEIGHT_IBEX"]
    N_SP = CONFIG["N_SP500_POSITIONS"]
    N_IBEX = CONFIG["N_IBEX_POSITIONS"]

    # Simulation runs from 2019-01-01 to end of available data
    all_sim_dates = momentum_us.dropna(how="all").index.intersection(
        momentum_ibex.dropna(how="all").index
    )
    all_sim_dates = all_sim_dates[all_sim_dates >= "2019-01-01"]
    all_sim_dates = all_sim_dates[all_sim_dates <= "2025-12-31"]
    rebalance_dates = [d for d in all_sim_dates if d.month in [1, 4, 7, 10]]

    cash_eur = INITIAL_CAPITAL
    holdings = {}  # ticker -> {shares, avg_price_eur, market, buy_date}
    yearly_realized_gain = {}
    monthly_log = []
    history_entries = []
    trades_records = []

    for date in all_sim_dates:
        year = date.year
        is_rebalance = date in rebalance_dates

        if is_rebalance:
            eur_usd = get_rate_on_or_before(eurusd_rates, date)
            mom_us_t = momentum_us.loc[date].dropna()
            mom_ibex_t = momentum_ibex.loc[date].dropna()
            top_us = mom_us_t.nlargest(N_SP).index.tolist()
            top_ibex = mom_ibex_t.nlargest(N_IBEX).index.tolist()
            new_top = set(top_us + top_ibex)

            # Pre-rebalance valuation
            pre_value_eur = cash_eur + sum(
                _position_value_eur(t, info, all_prices.loc[date], ibex_set, eur_usd)
                for t, info in holdings.items()
            )
            cash_before_eur = cash_eur

            orders_to_sell = []
            orders_to_buy = []

            # --- SELL positions no longer in top ---
            for t in list(holdings.keys()):
                if t not in new_top:
                    info = holdings[t]
                    if t in ibex_set:
                        price = all_prices.loc[date, t]
                        if pd.isna(price):
                            price = info["avg_price_eur"]
                        value_eur = info["shares"] * price
                        currency = "EUR"
                    else:
                        price_usd = all_prices.loc[date, t]
                        if pd.isna(price_usd):
                            price_usd = info["avg_price_eur"] * eur_usd
                        value_eur = info["shares"] * price_usd / eur_usd
                        price = price_usd
                        currency = "USD"

                    cost_basis = info["shares"] * info["avg_price_eur"]
                    gain_eur = value_eur - cost_basis
                    return_pct = (value_eur / cost_basis - 1) * 100 if cost_basis > 0 else 0
                    cash_eur += value_eur
                    yearly_realized_gain[year] = yearly_realized_gain.get(year, 0) + gain_eur

                    orders_to_sell.append({
                        "ticker": t,
                        "market": "IBEX" if t in ibex_set else "US",
                        "shares": round(info["shares"], 4),
                        "ref_price": round(float(price), 4),
                        "currency": currency,
                        "value_eur": round(value_eur, 2),
                    })
                    trades_records.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "year": year,
                        "quarter": f"Q{(date.month - 1) // 3 + 1} {year}",
                        "action": "SELL",
                        "ticker": t,
                        "market": "IBEX" if t in ibex_set else "US",
                        "shares": round(info["shares"], 4),
                        "price_local": round(float(price), 4),
                        "currency": currency,
                        "eur_usd_rate": round(eur_usd, 4) if t not in ibex_set else "",
                        "amount_eur": round(value_eur, 2),
                        "return_pct": round(return_pct, 2),
                    })
                    del holdings[t]

            # --- Compute new targets ---
            current_held_value_eur = sum(
                _position_value_eur(t, info, all_prices.loc[date], ibex_set, eur_usd)
                for t, info in holdings.items()
            )
            total_eur = cash_eur + current_held_value_eur
            target_per_sp_eur = (total_eur * WEIGHT_SP) / N_SP
            target_per_ibex_eur = (total_eur * WEIGHT_IBEX) / N_IBEX

            # --- BUY new positions ---
            for t in top_us:
                if t not in holdings:
                    price_usd = all_prices.loc[date, t]
                    if pd.isna(price_usd):
                        continue
                    invest_eur = min(target_per_sp_eur, cash_eur)
                    if invest_eur <= 0:
                        continue
                    avg_price_eur = price_usd / eur_usd
                    shares = invest_eur / avg_price_eur
                    holdings[t] = {
                        "shares": shares,
                        "avg_price_eur": avg_price_eur,
                        "market": "US",
                        "buy_date": date.strftime("%Y-%m-%d"),
                    }
                    cash_eur -= invest_eur
                    orders_to_buy.append({
                        "ticker": t,
                        "market": "US",
                        "shares": round(shares, 4),
                        "ref_price": round(float(price_usd), 4),
                        "currency": "USD",
                        "value_eur": round(invest_eur, 2),
                    })
                    trades_records.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "year": year,
                        "quarter": f"Q{(date.month - 1) // 3 + 1} {year}",
                        "action": "BUY",
                        "ticker": t,
                        "market": "US",
                        "shares": round(shares, 4),
                        "price_local": round(float(price_usd), 4),
                        "currency": "USD",
                        "eur_usd_rate": round(eur_usd, 4),
                        "amount_eur": round(invest_eur, 2),
                        "return_pct": "",
                    })

            for t in top_ibex:
                if t not in holdings:
                    price_eur = all_prices.loc[date, t]
                    if pd.isna(price_eur):
                        continue
                    invest_eur = min(target_per_ibex_eur, cash_eur)
                    if invest_eur <= 0:
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
                        "ref_price": round(float(price_eur), 4),
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
                        "price_local": round(float(price_eur), 4),
                        "currency": "EUR",
                        "eur_usd_rate": "",
                        "amount_eur": round(invest_eur, 2),
                        "return_pct": "",
                    })

            post_value_eur = cash_eur + sum(
                _position_value_eur(t, info, all_prices.loc[date], ibex_set, eur_usd)
                for t, info in holdings.items()
            )
            history_entries.append({
                "date": date.strftime("%Y-%m-%d"),
                "eur_usd_rate": round(eur_usd, 4),
                "portfolio_value_eur_before": round(pre_value_eur, 2),
                "portfolio_value_eur_after": round(post_value_eur, 2),
                "cash_before_eur": round(cash_before_eur, 2),
                "selected_us": top_us,
                "selected_ibex": top_ibex,
                "momentum_us_top": {t: round(float(mom_us_t[t]), 4) for t in top_us},
                "momentum_ibex_top": {t: round(float(mom_ibex_t[t]), 4) for t in top_ibex},
                "orders_to_sell": orders_to_sell,
                "orders_to_buy": orders_to_buy,
                "_note": "Backtest entry. Commissions excluded.",
            })

        # Monthly log
        eur_usd_month = get_rate_on_or_before(eurusd_rates, date)
        cur_val = sum(
            _position_value_eur(t, info, all_prices.loc[date], ibex_set, eur_usd_month)
            for t, info in holdings.items()
        )
        monthly_log.append({"date": date, "value_eur": cash_eur + cur_val})

    # ----- Year-end tax adjustments -----
    df_log = pd.DataFrame(monthly_log).set_index("date")
    yearly_summary = []
    total_taxes = 0.0
    final_year = max(d.year for d in all_sim_dates)

    for year in range(2019, final_year + 1):
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
        df_log.loc[df_log.index >= f"{year}-12-31", "value_eur"] -= (
            tax if year < final_year else 0
        )

    valor_serie = df_log["value_eur"].copy()
    final_tax_last = calc_irpf(yearly_realized_gain.get(final_year, 0), final_year)
    valor_serie.iloc[-1] -= final_tax_last

    returns_net = valor_serie.pct_change()
    returns_net.iloc[0] = valor_serie.iloc[0] / INITIAL_CAPITAL - 1
    n_years = len(returns_net) / 12

    final_capital = float(valor_serie.iloc[-1])
    total_return = final_capital / INITIAL_CAPITAL - 1
    cagr = (final_capital / INITIAL_CAPITAL) ** (1 / n_years) - 1
    vol = returns_net.std() * np.sqrt(12)
    sharpe = returns_net.mean() / returns_net.std() * np.sqrt(12)
    max_dd = ((valor_serie / valor_serie.cummax()) - 1).min()

    # ----- Print summary -----
    print(f"\n{'Year':<6}{'V.start':>12}{'V.end net':>14}{'Return net':>13}"
          f"{'Tax':>12}{'Realized':>14}")
    print("-" * 78)
    for s in yearly_summary:
        print(f"{s['year']:<6}{s['start']:>11,.0f}€{s['end_net']:>13,.0f}€"
              f"{s['return_net']:>+12.2%}{s['tax']:>11,.0f}€{s['realized_gain']:>13,.0f}€")

    print(f"\n{'=' * 78}")
    print("FINAL RESULTS (real prices + real EUR/USD)")
    print('=' * 78)
    print(f"  Initial capital:       {INITIAL_CAPITAL:>10,.2f} EUR")
    print(f"  Final capital:         {final_capital:>10,.2f} EUR")
    print(f"  Total return:          {total_return * 100:>+10.2f}%")
    print(f"  CAGR (net):            {cagr * 100:>+10.2f}%")
    print(f"  Annualized volatility: {vol * 100:>10.2f}%")
    print(f"  Sharpe ratio (rf=0):   {sharpe:>10.2f}")
    print(f"  Max drawdown:          {max_dd * 100:>10.2f}%")
    print(f"  Total taxes:           {total_taxes + final_tax_last:>10,.2f} EUR")
    print("  Note: commissions excluded. Record per-trade actuals in production.")

    # ----- Save outputs -----
    print(f"\n[5/5] Writing output files to {BACKTESTS_DIR}/...")

    last_date = rebalance_dates[-1] if rebalance_dates else None
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
    print(f"      Wrote {BT_HISTORY_FILE.name} ({len(history_entries)} rebalances)")
    trades_df = pd.DataFrame(trades_records)
    trades_df.to_csv(BT_TRADES_FILE, index=False)
    print(f"      Wrote {BT_TRADES_FILE.name} ({len(trades_df)} trades)")

    # Build the monthly log with drawdown for downstream charts and report.
    # valor_serie already has yearly taxes deducted (the v1.3.1 fix), so this
    # IS the net trajectory the investor would have seen month-by-month.
    running_peak = valor_serie.cummax()
    drawdown_pct = (valor_serie / running_peak - 1) * 100
    monthly_log_export = [
        {
            "date": d.strftime("%Y-%m-%d"),
            "value_eur": round(float(v), 2),
            "drawdown_pct": round(float(drawdown_pct.loc[d]), 4),
        }
        for d, v in valor_serie.items()
    ]

    metrics = {
        "data_source": "real",
        "initial_capital_eur": INITIAL_CAPITAL,
        "final_capital_eur": round(final_capital, 2),
        "total_return": round(total_return, 4),
        "cagr": round(cagr, 4),
        "volatility": round(vol, 4),
        "sharpe": round(sharpe, 4),
        "max_drawdown": round(max_dd, 4),
        "total_taxes_eur": round(total_taxes + final_tax_last, 2),
        "n_rebalances": len(history_entries),
        "n_trades": len(trades_records),
        "us_universe_size": len(us_tickers),
        "ibex_universe_size": len(ibex_tickers),
        "yearly_summary": [
            {k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()}
            for s in yearly_summary
        ],
        "monthly_log": monthly_log_export,
    }
    with open(BT_METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2, default=str)
    print(f"      Wrote {BT_METRICS_FILE.name}")

    print("\nDone. Now run:")
    print("    python scripts/build_backtest_dashboard.py   # generates dashboard image")
    print("    python scripts/build_backtest_report.py      # generates results .md")


if __name__ == "__main__":
    main()
