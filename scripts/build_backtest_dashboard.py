"""
Generates an executive dashboard image (PNG) summarizing the backtest results.

USAGE:
    python scripts/build_backtest_dashboard.py

Reads from backtests/ and writes backtests/backtest-dashboard.png.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

ROOT = Path(__file__).parent.parent
BACKTESTS_DIR = ROOT / "backtests"
DASHBOARD_FILE = BACKTESTS_DIR / "backtest-dashboard.png"

# Brand palette (matches the project's "Midnight Executive" theme)
NAVY = "#1E2761"
NAVY_DARK = "#121838"
ICE = "#CADCFC"
WHITE = "#FFFFFF"
GOLD = "#F2C94C"
RED = "#EB5757"
GREEN = "#27AE60"
GREY_LIGHT = "#F5F7FA"
GREY_TEXT = "#5A6478"


def load_data():
    with open(BACKTESTS_DIR / "backtest-metrics.json") as f:
        metrics = json.load(f)
    with open(BACKTESTS_DIR / "backtest-history.json") as f:
        history = json.load(f)
    trades = pd.read_csv(BACKTESTS_DIR / "backtest-trades.csv")
    return metrics, history, trades


def build_dashboard():
    metrics, history, trades = load_data()

    fig = plt.figure(figsize=(16, 10), facecolor=WHITE)
    fig.suptitle(
        "Momentum 12-1 Strategy - Backtest Dashboard",
        fontsize=20, fontweight="bold", color=NAVY_DARK, y=0.97,
    )
    fig.text(
        0.5, 0.935,
        "2019-2025  ·  4 US + 2 IBEX  ·  65/30/5  ·  Real historical EUR/USD",
        ha="center", fontsize=11, color=GREY_TEXT, style="italic",
    )

    gs = fig.add_gridspec(
        nrows=3, ncols=4,
        height_ratios=[1, 2, 2],
        hspace=0.55, wspace=0.35,
        left=0.05, right=0.97, top=0.88, bottom=0.06,
    )

    # ---- Row 1: KPI cards ----
    kpi_data = [
        ("CAPITAL FINAL", f"{metrics['final_capital_eur']:,.0f} €", GOLD),
        ("CAGR NETO",     f"{metrics['cagr']*100:+.2f}%",          GREEN),
        ("SHARPE",        f"{metrics['sharpe']:.2f}",              NAVY),
        ("MAX DRAWDOWN",  f"{metrics['max_drawdown']*100:.2f}%",   RED),
    ]
    for i, (label, value, color) in enumerate(kpi_data):
        ax = fig.add_subplot(gs[0, i])
        ax.set_facecolor(WHITE)
        ax.axis("off")
        # Background rectangle
        rect = mpatches.FancyBboxPatch(
            (0.02, 0.05), 0.96, 0.9,
            boxstyle="round,pad=0.02,rounding_size=0.02",
            transform=ax.transAxes,
            facecolor=GREY_LIGHT, edgecolor="none",
        )
        ax.add_patch(rect)
        # Color stripe on left
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

    # ---- Row 2 left: Equity curve ----
    ax1 = fig.add_subplot(gs[1, :2])
    yearly = metrics["yearly_summary"]
    years = [s["year"] for s in yearly]
    end_net = [s["end_net"] for s in yearly]
    # Prepend initial
    plot_x = ["Start"] + [str(y) for y in years]
    plot_y = [metrics["initial_capital_eur"]] + end_net

    ax1.plot(plot_x, plot_y, linewidth=3, color=NAVY, marker="o", markersize=8,
             markerfacecolor=GOLD, markeredgecolor=NAVY, markeredgewidth=1.5)
    for i, val in enumerate(plot_y):
        ax1.annotate(
            f"{val:,.0f} €",
            (i, val), textcoords="offset points", xytext=(0, 12),
            ha="center", fontsize=8.5, color=NAVY_DARK, fontweight="bold",
        )
    ax1.set_title("Capital evolution (net of taxes)",
                  fontsize=12, fontweight="bold", color=NAVY_DARK, pad=14)
    ax1.set_facecolor(WHITE)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_color(GREY_TEXT)
    ax1.spines["bottom"].set_color(GREY_TEXT)
    ax1.tick_params(colors=GREY_TEXT, labelsize=9)
    ax1.grid(axis="y", color=ICE, linewidth=0.6)
    ax1.set_axisbelow(True)
    ax1.set_ylim(0, max(plot_y) * 1.18)

    # ---- Row 2 right: Year-by-year return bars ----
    ax2 = fig.add_subplot(gs[1, 2:])
    returns = [s["return_net"] * 100 for s in yearly]
    colors = [GREEN if r >= 0 else RED for r in returns]
    bars = ax2.bar(years, returns, color=colors, edgecolor="none", width=0.7)
    for bar, r in zip(bars, returns):
        ax2.text(
            bar.get_x() + bar.get_width()/2,
            r + (2.5 if r >= 0 else -5),
            f"{r:+.1f}%",
            ha="center", fontsize=9, color=NAVY_DARK, fontweight="bold",
        )
    ax2.axhline(0, color=GREY_TEXT, linewidth=0.8)
    ax2.set_title("Annual net return", fontsize=12, fontweight="bold",
                  color=NAVY_DARK, pad=14)
    ax2.set_facecolor(WHITE)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_color(GREY_TEXT)
    ax2.spines["bottom"].set_color(GREY_TEXT)
    ax2.tick_params(colors=GREY_TEXT, labelsize=9)
    ax2.grid(axis="y", color=ICE, linewidth=0.6)
    ax2.set_axisbelow(True)
    ax2.set_ylim(min(returns) - 15, max(returns) + 25)

    # ---- Row 3 left: EUR/USD rate trajectory ----
    ax3 = fig.add_subplot(gs[2, :2])
    rates = [(h["date"], h["eur_usd_rate"]) for h in history]
    dates = [r[0] for r in rates]
    rate_values = [r[1] for r in rates]

    ax3.plot(dates, rate_values, color=NAVY, linewidth=2.0)
    ax3.fill_between(range(len(dates)), rate_values, min(rate_values)-0.02,
                     color=NAVY, alpha=0.10)
    ax3.axhline(1.0, color=GREY_TEXT, linestyle="--", linewidth=0.7, alpha=0.6)
    ax3.text(len(dates)-1, 1.0, "  parity (1.0)", fontsize=8, color=GREY_TEXT,
             va="center")
    ax3.set_title("EUR/USD at each rebalance (real historical data)",
                  fontsize=12, fontweight="bold", color=NAVY_DARK, pad=14)
    ax3.set_facecolor(WHITE)
    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)
    ax3.spines["left"].set_color(GREY_TEXT)
    ax3.spines["bottom"].set_color(GREY_TEXT)
    ax3.tick_params(colors=GREY_TEXT, labelsize=8)
    # Show only year-Q1 labels for readability
    ax3.set_xticks([i for i, d in enumerate(dates) if d.endswith("-01-31") or d.endswith("-01-30")])
    ax3.set_xticklabels([d[:4] for d in dates if d.endswith("-01-31") or d.endswith("-01-30")])
    ax3.grid(axis="y", color=ICE, linewidth=0.6)
    ax3.set_axisbelow(True)

    # ---- Row 3 right: Top stocks by selection frequency ----
    ax4 = fig.add_subplot(gs[2, 2:])
    buys = trades[trades["action"] == "BUY"]
    top_picks = buys["ticker"].value_counts().head(8)
    ax4.barh(top_picks.index[::-1], top_picks.values[::-1],
             color=NAVY, edgecolor="none", height=0.7)
    for i, (ticker, count) in enumerate(zip(top_picks.index[::-1], top_picks.values[::-1])):
        ax4.text(count + 0.15, i, str(count), va="center",
                 fontsize=9, color=NAVY_DARK, fontweight="bold")
    ax4.set_title("Most-selected stocks (across 28 rebalances)",
                  fontsize=12, fontweight="bold", color=NAVY_DARK, pad=14)
    ax4.set_facecolor(WHITE)
    ax4.spines["top"].set_visible(False)
    ax4.spines["right"].set_visible(False)
    ax4.spines["left"].set_color(GREY_TEXT)
    ax4.spines["bottom"].set_color(GREY_TEXT)
    ax4.tick_params(colors=GREY_TEXT, labelsize=9)
    ax4.grid(axis="x", color=ICE, linewidth=0.6)
    ax4.set_axisbelow(True)
    ax4.set_xlim(0, max(top_picks.values) * 1.15)

    # Footer
    fig.text(
        0.5, 0.02,
        f"Backtest scope: {metrics['n_rebalances']} quarterly rebalances  ·  "
        f"{metrics['n_trades']} total trades  ·  "
        f"Synthetic prices calibrated to annual returns, real historical EUR/USD",
        ha="center", fontsize=8.5, color=GREY_TEXT, style="italic",
    )

    plt.savefig(DASHBOARD_FILE, dpi=130, bbox_inches="tight", facecolor=WHITE)
    print(f"Wrote {DASHBOARD_FILE}")


if __name__ == "__main__":
    build_dashboard()
