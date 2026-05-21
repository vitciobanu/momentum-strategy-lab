"""
Generates an executive dashboard image (PNG) summarizing the backtest results.

USAGE:
    python scripts/build_backtest_dashboard.py

Reads from backtests/ and writes backtests/backtest-dashboard.png.

Layout (v1.4.0):
    Row 1: 4 KPI cards (Capital final, CAGR, Sharpe, Max DD)
    Row 2: Monthly equity curve (full width)
    Row 3: Drawdown chart (full width, half height)
    Row 4: Yearly return bars | Top stocks selected
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from pathlib import Path

ROOT = Path(__file__).parent.parent
BACKTESTS_DIR = ROOT / "backtests"
DASHBOARD_FILE = BACKTESTS_DIR / "backtest-dashboard.png"

# Brand palette
NAVY = "#1E2761"
NAVY_DARK = "#121838"
ICE = "#CADCFC"
WHITE = "#FFFFFF"
GOLD = "#F2C94C"
RED = "#EB5757"
RED_DARK = "#C84141"
GREEN = "#27AE60"
GREY_LIGHT = "#F5F7FA"
GREY_TEXT = "#5A6478"


def load_data():
    with open(BACKTESTS_DIR / "backtest-metrics.json") as f:
        metrics = json.load(f)
    trades = pd.read_csv(BACKTESTS_DIR / "backtest-trades.csv")
    return metrics, trades


def build_dashboard():
    metrics, trades = load_data()
    monthly_log = metrics.get("monthly_log", [])

    if not monthly_log:
        raise RuntimeError(
            "backtest-metrics.json has no 'monthly_log'. Re-run src/backtest.py "
            "to regenerate the metrics file."
        )

    # Convert monthly log to pandas for plotting
    df_monthly = pd.DataFrame(monthly_log)
    df_monthly["date"] = pd.to_datetime(df_monthly["date"])
    df_monthly = df_monthly.sort_values("date").reset_index(drop=True)

    fig = plt.figure(figsize=(16, 12), facecolor=WHITE)
    fig.suptitle(
        "Momentum 12-1 Strategy — Backtest Dashboard",
        fontsize=20, fontweight="bold", color=NAVY_DARK, y=0.975,
    )

    subtitle = (
        f"2019-2025  ·  4 US + 2 IBEX  ·  65/30/5  ·  "
        f"Real historical prices  ·  Real historical EUR/USD"
    )
    fig.text(0.5, 0.939, subtitle, ha="center", fontsize=11,
             color=GREY_TEXT, style="italic")

    gs = fig.add_gridspec(
        nrows=4, ncols=4,
        height_ratios=[1, 2.2, 1.3, 1.7],
        hspace=0.7, wspace=0.35,
        left=0.05, right=0.97, top=0.91, bottom=0.05,
    )

    # ---- Row 1: KPI cards ----
    kpi_data = [
        ("FINAL CAPITAL", f"{metrics['final_capital_eur']:,.0f} €", GOLD),
        ("NET CAGR",     f"{metrics['cagr']*100:+.2f}%",          GREEN),
        ("SHARPE",        f"{metrics['sharpe']:.2f}",              NAVY),
        ("MAX DRAWDOWN",  f"{metrics['max_drawdown']*100:.2f}%",   RED),
    ]
    for i, (label, value, color) in enumerate(kpi_data):
        ax = fig.add_subplot(gs[0, i])
        ax.set_facecolor(WHITE)
        ax.axis("off")
        rect = mpatches.FancyBboxPatch(
            (0.02, 0.05), 0.96, 0.9,
            boxstyle="round,pad=0.02,rounding_size=0.02",
            transform=ax.transAxes,
            facecolor=GREY_LIGHT, edgecolor="none",
        )
        ax.add_patch(rect)
        stripe = mpatches.Rectangle(
            (0.02, 0.05), 0.04, 0.9,
            transform=ax.transAxes,
            facecolor=color, edgecolor="none",
        )
        ax.add_patch(stripe)
        ax.text(0.12, 0.65, label, fontsize=9, color=NAVY,
                fontweight="bold", transform=ax.transAxes,
                family="sans-serif")
        ax.text(0.12, 0.25, value, fontsize=22, color=NAVY_DARK,
                fontweight="bold", transform=ax.transAxes,
                family="serif")

    # ---- Row 2: Monthly equity curve (full width) ----
    ax_eq = fig.add_subplot(gs[1, :])
    ax_eq.plot(df_monthly["date"], df_monthly["value_eur"],
               linewidth=2.2, color=NAVY)
    ax_eq.fill_between(df_monthly["date"], df_monthly["value_eur"], 0,
                       color=NAVY, alpha=0.08)

    # Mark peak before max DD and the trough
    peak_idx = df_monthly["value_eur"].idxmax()
    peak_date = df_monthly["date"].iloc[peak_idx]
    peak_value = df_monthly["value_eur"].iloc[peak_idx]

    # The "max DD peak" is the highest point before the worst drawdown
    worst_dd_idx = df_monthly["drawdown_pct"].idxmin()
    pre_dd = df_monthly.iloc[:worst_dd_idx + 1]
    dd_peak_idx = pre_dd["value_eur"].idxmax()
    dd_peak_date = df_monthly["date"].iloc[dd_peak_idx]
    dd_peak_value = df_monthly["value_eur"].iloc[dd_peak_idx]

    worst_dd_date = df_monthly["date"].iloc[worst_dd_idx]
    worst_dd_value = df_monthly["value_eur"].iloc[worst_dd_idx]

    # Annotate the crash
    ax_eq.plot([dd_peak_date, worst_dd_date], [dd_peak_value, worst_dd_value],
               "o", markersize=8, color=RED, markeredgecolor=WHITE,
               markeredgewidth=1.5, zorder=5)
    ax_eq.annotate(
        f"Pre-crash peak\n{dd_peak_date.strftime('%b %Y')}\n{dd_peak_value:,.0f} €",
        xy=(dd_peak_date, dd_peak_value),
        xytext=(dd_peak_date, dd_peak_value + 8000),
        fontsize=8.5, color=RED_DARK, fontweight="bold",
        ha="center", va="bottom",
        arrowprops=dict(arrowstyle="->", color=RED, lw=1),
    )
    ax_eq.annotate(
        f"Crash trough\n{worst_dd_date.strftime('%b %Y')}\n{worst_dd_value:,.0f} €",
        xy=(worst_dd_date, worst_dd_value),
        xytext=(worst_dd_date, worst_dd_value - 10000),
        fontsize=8.5, color=RED_DARK, fontweight="bold",
        ha="center", va="top",
        arrowprops=dict(arrowstyle="->", color=RED, lw=1),
    )

    ax_eq.set_title("Monthly portfolio trajectory (84 points, net of taxes)",
                    fontsize=12, fontweight="bold", color=NAVY_DARK, pad=10)
    ax_eq.set_ylabel("EUR", fontsize=10, color=GREY_TEXT)
    ax_eq.set_facecolor(WHITE)
    ax_eq.spines["top"].set_visible(False)
    ax_eq.spines["right"].set_visible(False)
    ax_eq.spines["left"].set_color(GREY_TEXT)
    ax_eq.spines["bottom"].set_color(GREY_TEXT)
    ax_eq.tick_params(colors=GREY_TEXT, labelsize=9)
    ax_eq.grid(axis="y", color=ICE, linewidth=0.6)
    ax_eq.set_axisbelow(True)
    ax_eq.xaxis.set_major_locator(mdates.YearLocator())
    ax_eq.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax_eq.set_ylim(0, df_monthly["value_eur"].max() * 1.15)

    # ---- Row 3: Drawdown chart (full width, smaller) ----
    ax_dd = fig.add_subplot(gs[2, :])
    ax_dd.fill_between(df_monthly["date"], df_monthly["drawdown_pct"], 0,
                       color=RED, alpha=0.25)
    ax_dd.plot(df_monthly["date"], df_monthly["drawdown_pct"],
               linewidth=1.5, color=RED_DARK)
    ax_dd.axhline(0, color=GREY_TEXT, linewidth=0.6, alpha=0.5)
    ax_dd.axhline(metrics["max_drawdown"] * 100, color=RED_DARK,
                  linewidth=0.6, linestyle="--", alpha=0.5)
    ax_dd.text(df_monthly["date"].iloc[-1], metrics["max_drawdown"] * 100,
               f"  Max DD: {metrics['max_drawdown']*100:.2f}%",
               fontsize=8.5, color=RED_DARK, va="center", fontweight="bold")

    ax_dd.set_title("Drawdown: how far the portfolio is below its all-time peak",
                    fontsize=11, fontweight="bold", color=NAVY_DARK, pad=10)
    ax_dd.set_ylabel("Drawdown (%)", fontsize=10, color=GREY_TEXT)
    ax_dd.set_facecolor(WHITE)
    ax_dd.spines["top"].set_visible(False)
    ax_dd.spines["right"].set_visible(False)
    ax_dd.spines["left"].set_color(GREY_TEXT)
    ax_dd.spines["bottom"].set_color(GREY_TEXT)
    ax_dd.tick_params(colors=GREY_TEXT, labelsize=9)
    ax_dd.grid(axis="y", color=ICE, linewidth=0.6)
    ax_dd.set_axisbelow(True)
    ax_dd.xaxis.set_major_locator(mdates.YearLocator())
    ax_dd.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax_dd.set_ylim(metrics["max_drawdown"] * 100 * 1.15, 5)

    # ---- Row 4 left: Year-by-year return bars ----
    ax_yr = fig.add_subplot(gs[3, :2])
    yearly = metrics["yearly_summary"]
    years = [s["year"] for s in yearly]
    returns = [s["return_net"] * 100 for s in yearly]
    colors = [GREEN if r >= 0 else RED for r in returns]
    bars = ax_yr.bar(years, returns, color=colors, edgecolor="none", width=0.7)
    for bar, r in zip(bars, returns):
        ax_yr.text(
            bar.get_x() + bar.get_width()/2,
            r + (3 if r >= 0 else -7),
            f"{r:+.1f}%",
            ha="center", fontsize=9, color=NAVY_DARK, fontweight="bold",
        )
    ax_yr.axhline(0, color=GREY_TEXT, linewidth=0.8)
    ax_yr.set_title("Net annual return %", fontsize=11, fontweight="bold",
                    color=NAVY_DARK, pad=10)
    ax_yr.set_facecolor(WHITE)
    ax_yr.spines["top"].set_visible(False)
    ax_yr.spines["right"].set_visible(False)
    ax_yr.spines["left"].set_color(GREY_TEXT)
    ax_yr.spines["bottom"].set_color(GREY_TEXT)
    ax_yr.tick_params(colors=GREY_TEXT, labelsize=9)
    ax_yr.grid(axis="y", color=ICE, linewidth=0.6)
    ax_yr.set_axisbelow(True)
    ax_yr.set_ylim(min(returns) - 25, max(returns) + 30)

    # ---- Row 4 right: Top stocks by selection frequency ----
    ax4 = fig.add_subplot(gs[3, 2:])
    buys = trades[trades["action"] == "BUY"]
    top_picks = buys["ticker"].value_counts().head(12)
    ax4.barh(top_picks.index[::-1], top_picks.values[::-1],
             color=NAVY, edgecolor="none", height=0.7)
    for i, (ticker, count) in enumerate(zip(top_picks.index[::-1], top_picks.values[::-1])):
        ax4.text(count + 0.05, i, str(count), va="center",
                 fontsize=9, color=NAVY_DARK, fontweight="bold")
    ax4.set_title(f"Most selected stocks (across {metrics['n_rebalances']} rebalances)",
                  fontsize=11, fontweight="bold", color=NAVY_DARK, pad=10)
    ax4.set_facecolor(WHITE)
    ax4.spines["top"].set_visible(False)
    ax4.spines["right"].set_visible(False)
    ax4.spines["left"].set_color(GREY_TEXT)
    ax4.spines["bottom"].set_color(GREY_TEXT)
    ax4.tick_params(colors=GREY_TEXT, labelsize=9)
    ax4.grid(axis="x", color=ICE, linewidth=0.6)
    ax4.set_axisbelow(True)
    ax4.set_xlim(0, max(top_picks.values) * 1.18)

    # Footer
    fig.text(
        0.5, 0.015,
        f"Backtest scope: {metrics['n_rebalances']} quarterly rebalances  ·  "
        f"{metrics['n_trades']} total trades  ·  "
        f"Universe: {metrics.get('us_universe_size', '?')} US + "
        f"{metrics.get('ibex_universe_size', '?')} IBEX stocks  ·  "
        f"All values net of Spanish IRPF",
        ha="center", fontsize=8.5, color=GREY_TEXT, style="italic",
    )

    plt.savefig(DASHBOARD_FILE, dpi=130, bbox_inches="tight", facecolor=WHITE)
    print(f"Wrote {DASHBOARD_FILE}")


if __name__ == "__main__":
    build_dashboard()
