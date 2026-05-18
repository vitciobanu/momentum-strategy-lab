"""
================================================================================
CAGR / Return calculation for portfolios with capital additions/withdrawals
================================================================================

Closes GitHub issue #3: Implement time-weighted return calculation for added
capital scenarios.

PROBLEM
-------
The naive return formula `(current_value - initial_capital) / initial_capital`
breaks as soon as you add or withdraw capital, because it conflates investment
performance with new money flows.

This module provides TWO complementary metrics:

  1. Money-weighted return (MWR / XIRR)
     The internal rate of return that accounts for every cash flow's TIMING
     and SIZE. Same metric professional fund managers use. Answers:
     "What annualized return did MY MONEY actually experience?"

  2. Time-weighted return (TWR)
     The compounding of period returns, ignoring the size of cash flows.
     This is the metric used to evaluate the STRATEGY, independent of when
     the investor chose to add or withdraw money. Answers:
     "How well did the strategy perform regardless of my deposit timing?"

Both metrics agree when there are no cash flows after the initial deposit.
When there are mid-stream contributions or withdrawals, they can differ.

USAGE
-----
    from cagr import compute_returns_from_files

    # Reads data/portfolio.json + data/history.json
    summary = compute_returns_from_files()
    print(summary)

Or programmatically:

    from cagr import compute_xirr, compute_twr
    from datetime import date

    cashflows = [
        (date(2026, 5, 13), -2000.00),   # initial deposit (negative = outflow from you)
        (date(2027, 4, 7),  -1000.00),   # added capital
        (date(2028, 1, 6),    500.00),   # partial withdrawal
        (date(2028, 5, 13),  5800.00),   # current portfolio value (positive = inflow to you)
    ]
    mwr = compute_xirr(cashflows)
    print(f"Money-weighted annualized return: {mwr*100:+.2f}%")

NOTES
-----
- All amounts are in EUR.
- Cash flow sign convention: from the INVESTOR's perspective.
    Negative = money leaves your wallet (deposits to the strategy)
    Positive = money returns to your wallet (withdrawals, final value)
- This module has NO dependency on yfinance, pyxirr, or any other external
  package beyond the standard library. The XIRR is computed with a
  Newton-Raphson root finder.
================================================================================
"""

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Tuple, Optional
import json

ROOT = Path(__file__).parent.parent
PORTFOLIO_FILE = ROOT / "data" / "portfolio.json"
HISTORY_FILE = ROOT / "data" / "history.json"


# ============================================================================
# XIRR (Money-weighted return)
# ============================================================================

def _xnpv(rate: float, cashflows: List[Tuple[date, float]]) -> float:
    """Net present value of irregular cash flows at given annualized rate."""
    if rate <= -1.0:
        return float("inf")
    t0 = cashflows[0][0]
    total = 0.0
    for d, amount in cashflows:
        days = (d - t0).days
        total += amount / (1.0 + rate) ** (days / 365.0)
    return total


def _xnpv_derivative(rate: float, cashflows: List[Tuple[date, float]]) -> float:
    """Derivative of XNPV with respect to rate (used by Newton-Raphson)."""
    if rate <= -1.0:
        return float("inf")
    t0 = cashflows[0][0]
    total = 0.0
    for d, amount in cashflows:
        days = (d - t0).days
        years = days / 365.0
        total += -years * amount / (1.0 + rate) ** (years + 1.0)
    return total


def compute_xirr(cashflows: List[Tuple[date, float]],
                 guess: float = 0.10,
                 max_iter: int = 100,
                 tol: float = 1e-6) -> Optional[float]:
    """Compute internal rate of return (XIRR) for irregular cash flows.

    cashflows: list of (date, amount) tuples
        Convention (from the investor's perspective):
            Negative amounts = deposits (money out of your wallet)
            Positive amounts = withdrawals / final value (money to your wallet)
        Must contain at least one positive and one negative cash flow.

    Returns the annualized rate, or None if it does not converge.
    """
    if len(cashflows) < 2:
        return None
    has_pos = any(a > 0 for _, a in cashflows)
    has_neg = any(a < 0 for _, a in cashflows)
    if not (has_pos and has_neg):
        return None  # XIRR is undefined without sign change

    # Sort by date to make _xnpv consistent
    cashflows = sorted(cashflows, key=lambda x: x[0])

    rate = guess
    for _ in range(max_iter):
        f = _xnpv(rate, cashflows)
        if abs(f) < tol:
            return rate
        d_f = _xnpv_derivative(rate, cashflows)
        if d_f == 0 or not _is_finite(d_f):
            # Fall back to bisection
            return _xirr_bisection(cashflows)
        new_rate = rate - f / d_f
        if new_rate <= -1.0:
            new_rate = (rate - 1.0) / 2.0  # Shrink towards -1 from above
        if abs(new_rate - rate) < tol:
            return new_rate
        rate = new_rate
    # If Newton didn't converge, try bisection
    return _xirr_bisection(cashflows)


def _is_finite(x: float) -> bool:
    return not (x != x or x in (float("inf"), float("-inf")))


def _xirr_bisection(cashflows: List[Tuple[date, float]],
                    lo: float = -0.99, hi: float = 10.0,
                    tol: float = 1e-6, max_iter: int = 200) -> Optional[float]:
    """Robust fallback root-finder for XIRR via bisection."""
    f_lo = _xnpv(lo, cashflows)
    f_hi = _xnpv(hi, cashflows)
    if f_lo * f_hi > 0:
        # Try wider range
        hi = 100.0
        f_hi = _xnpv(hi, cashflows)
        if f_lo * f_hi > 0:
            return None  # Root not bracketed
    for _ in range(max_iter):
        mid = (lo + hi) / 2.0
        f_mid = _xnpv(mid, cashflows)
        if abs(f_mid) < tol or (hi - lo) / 2.0 < tol:
            return mid
        if f_lo * f_mid < 0:
            hi = mid
            f_hi = f_mid
        else:
            lo = mid
            f_lo = f_mid
    return (lo + hi) / 2.0


# ============================================================================
# Time-weighted return (TWR)
# ============================================================================

def compute_twr(period_values: List[Tuple[date, float, float]]) -> Optional[float]:
    """Compute annualized time-weighted return.

    period_values: list of tuples (date, portfolio_value_before_cashflow, net_cashflow_in)
        For each measurement date:
            portfolio_value_before_cashflow = portfolio value JUST BEFORE the
                cashflow on that date (i.e., the result of the previous sub-period)
            net_cashflow_in = positive if money was added that day, negative
                if withdrawn. Zero for normal valuations.

        The FIRST entry is the inception (cash deposited, portfolio empty
        before the cashflow → use 0.0 as portfolio_value_before_cashflow).
        The LAST entry is the current valuation (use 0.0 as net_cashflow_in).

    Method:
        For each sub-period i:
            period_return_i = (V_{i,before} - V_{i-1,after}) / V_{i-1,after}
            where V_{i-1,after} = V_{i-1,before} + cashflow_{i-1}
        TWR_total = product(1 + period_return_i) - 1
        Annualized = (1 + TWR_total) ** (365 / total_days) - 1

    Returns None if input is insufficient or invalid.
    """
    if len(period_values) < 2:
        return None
    period_values = sorted(period_values, key=lambda x: x[0])
    growth_factors = []
    for i in range(1, len(period_values)):
        d_prev, v_prev_before, cf_prev = period_values[i - 1]
        d_curr, v_curr_before, _ = period_values[i]
        v_prev_after = v_prev_before + cf_prev  # End-of-period value after CF
        if v_prev_after <= 0:
            continue  # Skip degenerate sub-period
        gf = v_curr_before / v_prev_after
        growth_factors.append(gf)
    if not growth_factors:
        return None

    cum_growth = 1.0
    for gf in growth_factors:
        cum_growth *= gf
    twr_total = cum_growth - 1.0

    start_date = period_values[0][0]
    end_date = period_values[-1][0]
    days = (end_date - start_date).days
    if days <= 0:
        return None
    years = days / 365.0
    if years < 1e-9:
        return twr_total
    twr_annualized = (1.0 + twr_total) ** (1.0 / years) - 1.0
    return twr_annualized


# ============================================================================
# Reading cashflows from portfolio + history JSON files
# ============================================================================

def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def _load_json(path: Path):
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)


def extract_cashflows_from_history(portfolio: dict,
                                   history: list,
                                   today_value_eur: Optional[float] = None
                                   ) -> Tuple[List[Tuple[date, float]],
                                              List[Tuple[date, float, float]]]:
    """Extract MWR-style cashflows and TWR-style period valuations.

    portfolio: contents of data/portfolio.json
    history: contents of data/history.json (list of entries)
    today_value_eur: optional override for current portfolio value.
        If None, uses portfolio["_current_value_eur"] if present, otherwise
        falls back to portfolio_value_eur_before from the last history entry
        plus current cash_eur (a rough approximation).

    Returns:
        cashflows_for_xirr: list of (date, signed_amount) for compute_xirr()
        period_values_for_twr: list of (date, value_before_cf, cashflow_in)
            for compute_twr()
    """
    # ----- Reconstruct the capital-flow timeline -----
    # The portfolio file holds initial_capital_eur and net_capital_contributed_eur,
    # but not always the explicit list of additions/withdrawals. We try to
    # reconstruct from history entries with event = "CAPITAL_INJECTION" or
    # "CAPITAL_WITHDRAWAL". If absent, we assume the initial deposit only.

    initial = float(portfolio.get("initial_capital_eur", 2000.0))
    # If there is a clear inception date, use it; else use first history entry
    inception_date = portfolio.get("inception_date")
    if inception_date:
        inception = _parse_date(inception_date)
    elif history:
        first_entry = min(history, key=lambda h: h.get("date", "9999-99-99"))
        inception = _parse_date(first_entry["date"])
    else:
        # No inception_date and no history: the strategy hasn't really started.
        # MWR/TWR are not meaningful in this case. We use a sentinel that
        # makes the downstream calculator return None (deposit and final value
        # on the same day yields an undefined IRR).
        inception = date.today()

    # Initial deposit: money out of the investor's wallet -> negative
    cashflows = [(inception, -initial)]

    # Walk history looking for capital flow events
    for h in history:
        event = h.get("event")
        if event == "CAPITAL_INJECTION":
            d = _parse_date(h["date"])
            amt = float(h.get("amount_eur", 0.0))
            cashflows.append((d, -amt))  # New deposit: outflow from wallet
        elif event == "CAPITAL_WITHDRAWAL":
            d = _parse_date(h["date"])
            amt = float(h.get("amount_eur", 0.0))
            cashflows.append((d, amt))  # Withdrawal: inflow to wallet
        # All other events (regular rebalances) are NOT cash flows from
        # the investor's perspective. They reshape the portfolio internally.

    # Append today's portfolio value as the final positive cashflow
    if today_value_eur is None:
        today_value_eur = portfolio.get("_current_value_eur")
        if today_value_eur is None and history:
            last_hist = max(history, key=lambda h: h.get("date", "0000-00-00"))
            today_value_eur = last_hist.get("portfolio_value_eur_after",
                                            last_hist.get("portfolio_value_eur_before"))
    if today_value_eur is None:
        today_value_eur = initial  # Worst-case fallback

    today = date.today()
    cashflows.append((today, float(today_value_eur)))

    # ----- TWR period values -----
    # For TWR we need (date, value_before_cf, cashflow_in) at each cashflow
    # date and at the final date.
    period_values = []
    period_values.append((inception, 0.0, initial))  # inception: empty -> initial

    # Iterate through history sorted by date. For CAPITAL_INJECTION /
    # CAPITAL_WITHDRAWAL events we need the portfolio value JUST BEFORE the
    # event. If the event entry doesn't carry it, we take the last known
    # portfolio_value_eur_after (or _before of the most recent rebalance).
    sorted_history = sorted(history, key=lambda h: h.get("date", ""))
    last_known_value = initial  # value after inception
    for h in sorted_history:
        d = _parse_date(h["date"])
        event = h.get("event")
        explicit_value = h.get("portfolio_value_eur_before")
        if event == "CAPITAL_INJECTION":
            cf = float(h.get("amount_eur", 0.0))
            # Value just before the injection: use explicit if provided,
            # else fall back to last known value
            v_before = (float(explicit_value) if explicit_value
                        else last_known_value)
            period_values.append((d, v_before, cf))
            last_known_value = v_before + cf
        elif event == "CAPITAL_WITHDRAWAL":
            cf = -float(h.get("amount_eur", 0.0))
            v_before = (float(explicit_value) if explicit_value
                        else last_known_value)
            period_values.append((d, v_before, cf))
            last_known_value = v_before + cf
        else:
            # Regular rebalance entry: no cashflow, but updates the running value
            if explicit_value is not None:
                period_values.append((d, float(explicit_value), 0.0))
                last_known_value = float(
                    h.get("portfolio_value_eur_after", explicit_value)
                )

    period_values.append((today, today_value_eur, 0.0))
    return cashflows, period_values


# ============================================================================
# High-level API
# ============================================================================

def compute_returns_from_files(today_value_eur: Optional[float] = None) -> dict:
    """Read data/portfolio.json + data/history.json and compute MWR and TWR.

    Returns a dict with the metrics, ready to print or save to JSON.
    """
    portfolio = _load_json(PORTFOLIO_FILE) or {}
    history = _load_json(HISTORY_FILE) or []
    cashflows, period_values = extract_cashflows_from_history(
        portfolio, history, today_value_eur=today_value_eur
    )

    mwr = compute_xirr(cashflows)
    twr = compute_twr(period_values)

    # Also compute the simple "return on contributions" as a reference
    net_contributed = float(portfolio.get(
        "net_capital_contributed_eur",
        portfolio.get("initial_capital_eur", 2000.0)
    ))
    current = cashflows[-1][1]
    simple_return = (current / net_contributed - 1.0) if net_contributed > 0 else None

    return {
        "current_portfolio_value_eur": current,
        "net_capital_contributed_eur": net_contributed,
        "simple_return_on_contributions": simple_return,
        "money_weighted_annualized_return": mwr,  # XIRR equivalent
        "time_weighted_annualized_return": twr,   # TWR equivalent
        "cashflows": [(str(d), round(a, 2)) for d, a in cashflows],
        "n_cashflows": len(cashflows),
    }


def format_summary(summary: dict) -> str:
    """Pretty-print the summary dict for the terminal."""
    lines = []
    lines.append("=" * 72)
    lines.append("RETURN SUMMARY")
    lines.append("=" * 72)
    lines.append(f"  Current value:                   "
                 f"{summary['current_portfolio_value_eur']:>12,.2f} EUR")
    lines.append(f"  Net capital contributed:         "
                 f"{summary['net_capital_contributed_eur']:>12,.2f} EUR")

    simple = summary["simple_return_on_contributions"]
    if simple is not None:
        lines.append(f"  Simple return on contributions:  "
                     f"{simple*100:>+11.2f}%")

    mwr = summary["money_weighted_annualized_return"]
    if mwr is not None:
        lines.append("")
        lines.append(f"  Money-weighted CAGR (XIRR):      "
                     f"{mwr*100:>+11.2f}%   <-- what YOUR MONEY experienced")
    else:
        lines.append("")
        lines.append(f"  Money-weighted CAGR (XIRR):      [not yet — needs at least one")
        lines.append(f"                                    rebalance after inception]")

    twr = summary["time_weighted_annualized_return"]
    if twr is not None:
        lines.append(f"  Time-weighted CAGR (TWR):        "
                     f"{twr*100:>+11.2f}%   <-- pure strategy performance")
    else:
        lines.append(f"  Time-weighted CAGR (TWR):        [not yet — needs at least one")
        lines.append(f"                                    rebalance after inception]")

    lines.append("")
    lines.append(f"  Based on {summary['n_cashflows']} cash flows total.")
    lines.append("=" * 72)
    return "\n".join(lines)


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import sys
    today_value = None
    if len(sys.argv) > 1:
        try:
            today_value = float(sys.argv[1])
            print(f"Using provided current value: {today_value:,.2f} EUR")
        except ValueError:
            print(f"Ignoring argument {sys.argv[1]!r} (could not parse as number)")

    s = compute_returns_from_files(today_value_eur=today_value)
    print(format_summary(s))
