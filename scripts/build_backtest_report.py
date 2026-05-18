"""
Generates backtests/backtest-results.md with a detailed summary table.

USAGE:
    python scripts/build_backtest_report.py
"""

import json
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent
BACKTESTS_DIR = ROOT / "backtests"
OUTPUT_FILE = BACKTESTS_DIR / "backtest-results.md"


def fmt_eur(v):
    return f"{v:,.0f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(v):
    return f"{v:+.2f}%"


def build_report():
    with open(BACKTESTS_DIR / "backtest-metrics.json") as f:
        m = json.load(f)
    trades = pd.read_csv(BACKTESTS_DIR / "backtest-trades.csv")

    data_source = m.get("data_source", "synthetic")
    is_real = data_source == "real"

    lines = []
    lines.append("# Backtest results (2019-2025)")
    lines.append("")
    if is_real:
        lines.append(
            "Reproducible run of `src/backtest.py` against **REAL historical price data** "
            "from `data/monthly-historic-prices.csv` and **REAL historical EUR/USD rates** "
            "from `data/eurusd.rates.csv`."
        )
    else:
        lines.append(
            "Reproducible run of `src/backtest.py` against synthetic prices "
            "calibrated to known annual returns, with real historical EUR/USD rates."
        )
    lines.append("")
    lines.append("> Re-running `python src/backtest.py` regenerates the JSON/CSV outputs. "
                 "Then run `python scripts/build_backtest_dashboard.py` and "
                 "`python scripts/build_backtest_report.py` to regenerate the dashboard "
                 "image and this markdown report.")
    lines.append("")

    # ----- Strategy parameters -----
    lines.append("## Strategy parameters")
    lines.append("")
    lines.append("- **4 stocks from the US universe** + **2 stocks from IBEX 35** = 6 positions total")
    lines.append("- Weights: **65% USA / 30% Spain / 5% cash reserve**")
    lines.append("- Rebalancing: **quarterly** (Jan, Apr, Jul, Oct)")
    lines.append("- Selection: **dynamic each quarter** (no static pre-selection)")
    lines.append("- Fractional shares: enabled")
    lines.append("- Initial capital: **2,000 EUR**")
    lines.append(f"- US universe: **{m.get('us_universe_size', '?')}** stocks (NYSE + NASDAQ, "
                 f"includes S&P 500 large caps + non-S&P 500 + recent momentum mid-caps)")
    lines.append(f"- IBEX universe: **{m.get('ibex_universe_size', '?')}** stocks (complete IBEX 35)")
    if is_real:
        lines.append("- Price data: **real historical daily prices** from "
                     "`data/monthly-historic-prices.csv`, resampled to month-end closes")
    else:
        lines.append("- Price data: synthetic, calibrated to known annual returns")
    lines.append("- EUR/USD: **real historical rates per rebalance day** "
                 "(from `data/eurusd.rates.csv`)")
    lines.append("- Commissions: not modeled (recorded manually in real execution)")
    lines.append("- Tax framework: Spanish IRPF \"base del ahorro\"")
    lines.append("")

    # ----- Global summary -----
    lines.append("## Global summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Initial capital | {fmt_eur(m['initial_capital_eur'])} |")
    lines.append(f"| Final capital | **{fmt_eur(m['final_capital_eur'])}** |")
    lines.append(f"| Total return | {m['total_return']*100:+.2f}% |")
    lines.append(f"| **CAGR (net of taxes)** | **{m['cagr']*100:+.2f}%** |")
    lines.append(f"| Annualized volatility | {m['volatility']*100:.2f}% |")
    lines.append(f"| **Sharpe ratio** | **{m['sharpe']:.2f}** |")
    lines.append(f"| **Max drawdown** | **{m['max_drawdown']*100:.2f}%** |")
    lines.append(f"| Total taxes | {fmt_eur(m['total_taxes_eur'])} |")
    lines.append(f"| Total trades | {m['n_trades']} |")
    lines.append(f"| Rebalances | {m['n_rebalances']} |")
    lines.append("")

    # ----- Executive dashboard -----
    lines.append("## Executive dashboard")
    lines.append("")
    lines.append("![Backtest Dashboard](backtest-dashboard.png)")
    lines.append("")

    # ----- Year-by-year breakdown -----
    lines.append("## Year-by-year breakdown")
    lines.append("")
    lines.append("| Year | Capital start | Capital end (net) | Net return | Tax paid | Realized gain |")
    lines.append("|------|--------------:|------------------:|-----------:|---------:|--------------:|")
    for s in m["yearly_summary"]:
        lines.append(
            f"| {s['year']} "
            f"| {fmt_eur(s['start'])} "
            f"| {fmt_eur(s['end_net'])} "
            f"| **{fmt_pct(s['return_net']*100)}** "
            f"| {fmt_eur(s['tax'])} "
            f"| {fmt_eur(s['realized_gain'])} |"
        )
    lines.append("")

    # ----- Most-selected stocks -----
    buys = trades[trades["action"] == "BUY"]
    us_freq = buys[buys["market"] == "SP"]["ticker"].value_counts().head(15)
    ibex_freq = buys[buys["market"] == "IBEX"]["ticker"].value_counts().head(10)

    lines.append("## Most-selected stocks")
    lines.append("")
    lines.append("### US universe (top 15)")
    lines.append("")
    lines.append("| Ticker | Times selected |")
    lines.append("|---|---:|")
    for ticker, count in us_freq.items():
        lines.append(f"| {ticker} | {count} |")
    lines.append("")
    lines.append("### IBEX 35 (top 10)")
    lines.append("")
    lines.append("| Ticker | Times selected |")
    lines.append("|---|---:|")
    for ticker, count in ibex_freq.items():
        lines.append(f"| {ticker} | {count} |")
    lines.append("")

    # ----- Detailed quarterly trade table -----
    lines.append("## Detailed quarterly trades")
    lines.append("")
    lines.append("One row per executed buy/sell. Sells show realized return at exit; "
                 "buys leave the return column empty (the return crystallizes when sold).")
    lines.append("")

    trades["date"] = pd.to_datetime(trades["date"])
    trades["year"] = trades["date"].dt.year

    for year in sorted(trades["year"].unique()):
        year_trades = trades[trades["year"] == year].copy()
        year_trades = year_trades.sort_values(["date", "action", "ticker"])

        year_sells = year_trades[year_trades["action"] == "SELL"]
        n_buys = len(year_trades[year_trades["action"] == "BUY"])
        n_sells = len(year_sells)
        total_amount_eur = year_trades["amount_eur"].sum()
        year_metric = next((s for s in m["yearly_summary"] if s["year"] == year), None)
        net_return_str = (f" — net annual return **{fmt_pct(year_metric['return_net']*100)}**"
                          if year_metric else "")

        lines.append(f"### {year} ({n_buys} buys, {n_sells} sells, "
                     f"{fmt_eur(total_amount_eur)} total volume{net_return_str})")
        lines.append("")
        lines.append("| Quarter | Action | Ticker | Market | Shares | Price | EUR/USD | Amount (€) | Return % |")
        lines.append("|---------|--------|--------|--------|-------:|------:|--------:|-----------:|---------:|")
        for _, row in year_trades.iterrows():
            return_str = ""
            if row["action"] == "SELL" and pd.notna(row["return_pct"]) and row["return_pct"] != "":
                try:
                    r = float(row["return_pct"])
                    return_str = f"{r:+.2f}%"
                except (ValueError, TypeError):
                    return_str = ""

            eur_usd_str = ""
            if pd.notna(row["eur_usd_rate"]) and row["eur_usd_rate"] != "":
                try:
                    eur_usd_str = f"{float(row['eur_usd_rate']):.4f}"
                except (ValueError, TypeError):
                    eur_usd_str = ""

            lines.append(
                f"| {row['quarter']} "
                f"| {row['action']} "
                f"| {row['ticker']} "
                f"| {row['market']} "
                f"| {float(row['shares']):.4f} "
                f"| {float(row['price_local']):.2f} {row['currency']} "
                f"| {eur_usd_str} "
                f"| {fmt_eur(float(row['amount_eur']))} "
                f"| {return_str} |"
            )
        lines.append("")

    # ----- Notes -----
    lines.append("## Important notes")
    lines.append("")
    if is_real:
        lines.append("- **Real prices**: daily closes from `data/monthly-historic-prices.csv`, "
                     "resampled to month-end. Covers all IBEX 35 plus the full US large/mid-cap "
                     "universe defined in `src/universe.py`.")
    lines.append("- **Real EUR/USD historical rates** are used per rebalance day. "
                 "The rate moved from ~1.15 in 2019 to parity (~1.00) in 2022 and back "
                 "to ~1.15 in 2025.")
    lines.append("- **No commissions are modeled** in the backtest. Real execution "
                 "will subtract 0.1-0.3% per year of CAGR depending on broker tier.")
    lines.append("- **Survivorship bias**: the universe contains stocks that exist today. "
                 "Stocks that delisted are not represented.")
    lines.append("- **Composition timing bias**: some stocks IPO'd within the backtest window "
                 "(PLTR 2020, NU 2021, ARM 2023, SNDK relisted 2025). They enter the universe "
                 "as their data becomes available.")
    lines.append("")
    lines.append("A real-money implementation should expect **5-15 percentage points lower CAGR** "
                 "than this backtest, due to commissions, execution timing, slippage, and the "
                 "fact that the future regime will not be 2019-2025.")
    lines.append("")

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    build_report()
