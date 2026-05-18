"""
================================================================================
append-rebalance.py — Helper to record an executed quarterly rebalance
================================================================================

Closes GitHub issue: "Auto-compute EUR values from native USD trade data".

PROBLEM
-------
After every quarterly rebalance, the user must update two files:
  data/portfolio.json   (current positions + cash)
  data/history.json     (append a new entry for this rebalance)

For US trades, IBKR provides the data in USD (price, commission) and applies
a specific EUR/USD rate for each order (visible in the "EUR.USD SLD" lines
of the trade log). Manually computing the EUR-equivalent values is tedious
and error-prone.

This script automates all of it:
  1. Asks for each executed trade (ticker, market, shares, price, commission,
     and for US trades the exec EUR/USD rate)
  2. Computes value_eur, commission_eur, avg_price_eur automatically
  3. Validates the math (total spent ≈ cash before - cash after)
  4. Backups the existing JSON files (.bak) and writes the new ones

USAGE
-----
    python scripts/append-rebalance.py

The script is interactive and walks you through each trade. At the end,
review the summary, type "y" to confirm, and the JSONs are saved.

You can also dry-run without saving:
    python scripts/append-rebalance.py --dry-run

You can preload selection metadata from the last rebalance.py output by
passing --plan path/to/plan.json (optional, just convenience).
================================================================================
"""

import json
import sys
import os
import shutil
import argparse
from pathlib import Path
from datetime import date, datetime

ROOT = Path(__file__).parent.parent
PORTFOLIO_FILE = ROOT / "data" / "portfolio.json"
HISTORY_FILE = ROOT / "data" / "history.json"

# ============================================================================
# Helpers
# ============================================================================

def ask(prompt, validator=None, default=None, allow_empty=False):
    """Generic prompt with optional validation and default."""
    full_prompt = prompt
    if default is not None:
        full_prompt = f"{prompt} [{default}]"
    full_prompt = full_prompt.rstrip() + ": "
    while True:
        raw = input(full_prompt).strip()
        if raw == "" and default is not None:
            raw = str(default)
        if raw == "" and allow_empty:
            return ""
        if raw == "" and not allow_empty:
            print("  [!] empty input not allowed, try again")
            continue
        if validator is None:
            return raw
        try:
            return validator(raw)
        except (ValueError, AssertionError) as e:
            print(f"  [!] invalid input: {e}")


def parse_float(raw):
    """Accept '1.234,56' or '1,234.56' or '1234.56'."""
    raw = raw.strip().replace(" ", "")
    # If both , and . present, the rightmost is the decimal separator
    if "," in raw and "." in raw:
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif "," in raw:
        # Only comma: treat as decimal separator (European)
        raw = raw.replace(",", ".")
    return float(raw)


def parse_yes_no(raw):
    raw = raw.strip().lower()
    if raw in ("y", "yes", "s", "sí", "si"):
        return True
    if raw in ("n", "no"):
        return False
    raise ValueError("answer 'y' or 'n'")


def parse_market(raw):
    raw = raw.strip().upper()
    if raw in ("IBEX", "I"):
        return "IBEX"
    if raw in ("US", "U", "SP"):
        return "US"
    raise ValueError("market must be 'IBEX' or 'US'")


def parse_date(raw):
    raw = raw.strip()
    if raw.lower() == "today":
        return date.today().isoformat()
    # Try YYYY-MM-DD
    datetime.strptime(raw, "%Y-%m-%d")
    return raw


# ============================================================================
# Trade input
# ============================================================================

def prompt_for_trade(trade_num, action):
    """Ask for one trade (BUY or SELL). Returns a fully-populated dict."""
    print(f"\n  --- {action} #{trade_num} ---")
    ticker = ask("  Ticker (e.g. SNDK, ACS)").upper()
    market = ask("  Market (IBEX or US)", validator=parse_market)
    shares = ask("  Shares (fractional ok)", validator=parse_float)

    if market == "IBEX":
        exec_price_eur = ask("  Exec price (EUR)", validator=parse_float)
        commission_eur = ask("  Commission (EUR)", validator=parse_float, default="3.00")
        value_eur = round(shares * exec_price_eur, 2)

        return {
            "ticker": ticker,
            "market": "IBEX",
            "shares": shares,
            "exec_price_eur": exec_price_eur,
            "value_eur": value_eur,
            "commission_eur": commission_eur,
            "currency": "EUR",
        }
    else:
        exec_price_usd = ask("  Exec price (USD)", validator=parse_float)
        commission_usd = ask("  Commission (USD)", validator=parse_float, default="1.00")
        exec_eur_usd_rate = ask(
            "  Exec EUR/USD rate IBKR applied (e.g. 1.16399)",
            validator=parse_float,
        )
        if exec_eur_usd_rate < 0.5 or exec_eur_usd_rate > 2.0:
            print(f"  [!] WARNING: rate {exec_eur_usd_rate} seems out of normal range")

        value_usd = round(shares * exec_price_usd, 2)
        value_eur = round(value_usd / exec_eur_usd_rate, 2)
        commission_eur = round(commission_usd / exec_eur_usd_rate, 2)

        return {
            "ticker": ticker,
            "market": "US",
            "shares": shares,
            "exec_price_usd": exec_price_usd,
            "exec_eur_usd_rate": exec_eur_usd_rate,
            "value_usd": value_usd,
            "value_eur": value_eur,
            "commission_usd": commission_usd,
            "commission_eur": commission_eur,
            "currency": "USD",
        }


# ============================================================================
# Portfolio update logic
# ============================================================================

def apply_sells(portfolio, sells):
    """Apply SELL orders: remove from positions, add proceeds to cash, return realized P&L list."""
    realized = []
    for s in sells:
        ticker = s["ticker"]
        pos = portfolio["positions"].get(ticker)
        if pos is None:
            print(f"  [!] WARNING: selling {ticker} but it's not in portfolio. Skipping.")
            continue
        proceeds_eur = s["value_eur"] - s["commission_eur"]
        cost_basis_eur = pos["shares"] * pos["avg_price_eur"]
        gain_eur = proceeds_eur - cost_basis_eur
        realized.append({
            "ticker": ticker,
            "shares_sold": s["shares"],
            "proceeds_eur": proceeds_eur,
            "cost_basis_eur": cost_basis_eur,
            "gain_eur": round(gain_eur, 2),
            "return_pct": round((proceeds_eur / cost_basis_eur - 1) * 100, 2)
                          if cost_basis_eur > 0 else 0,
        })
        portfolio["cash_eur"] = round(portfolio["cash_eur"] + proceeds_eur, 2)
        del portfolio["positions"][ticker]
    return realized


def apply_buys(portfolio, buys, exec_date):
    """Apply BUY orders: add to positions, subtract from cash.

    Raises a clear error if the result would leave cash_eur deeply negative.
    Warns (but accepts) if a ticker is already in the portfolio — this is
    valid for a top-up but rare under pure momentum rotation.
    """
    duplicates_found = []
    for b in buys:
        ticker = b["ticker"]
        if ticker in portfolio["positions"]:
            duplicates_found.append(ticker)
            # Already held — average the prices (rare for momentum but possible
            # if user manually tops up a winner)
            existing = portfolio["positions"][ticker]
            total_shares = existing["shares"] + b["shares"]
            total_cost_eur = (existing["shares"] * existing["avg_price_eur"]
                              + b["shares"] * (b["value_eur"] / b["shares"]))
            new_avg = total_cost_eur / total_shares
            existing["shares"] = round(total_shares, 6)
            existing["avg_price_eur"] = round(new_avg, 4)
        else:
            if b["market"] == "IBEX":
                portfolio["positions"][ticker] = {
                    "shares": b["shares"],
                    "avg_price_eur": b["exec_price_eur"],
                    "market": "IBEX",
                    "buy_date": exec_date,
                    "commission_paid_eur": b["commission_eur"],
                }
            else:
                # US: avg_price_eur = exec_price_usd / rate
                avg_price_eur = round(b["exec_price_usd"] / b["exec_eur_usd_rate"], 4)
                portfolio["positions"][ticker] = {
                    "shares": b["shares"],
                    "avg_price_usd": b["exec_price_usd"],
                    "avg_price_eur": avg_price_eur,
                    "exec_eur_usd_rate": b["exec_eur_usd_rate"],
                    "market": "US",
                    "buy_date": exec_date,
                    "commission_paid_eur": b["commission_eur"],
                }
        # Subtract from cash
        portfolio["cash_eur"] = round(
            portfolio["cash_eur"] - b["value_eur"] - b["commission_eur"], 2
        )
    return duplicates_found


# ============================================================================
# Validation
# ============================================================================

def validate_cash_math(portfolio_before, portfolio_after, sells, buys, tolerance=0.5):
    """Verify that cash flows balance.

    cash_after = cash_before
                 + sum(sell.value_eur - sell.commission_eur)
                 - sum(buy.value_eur + buy.commission_eur)
    """
    sells_in_eur = sum(s["value_eur"] - s["commission_eur"] for s in sells)
    buys_out_eur = sum(b["value_eur"] + b["commission_eur"] for b in buys)
    expected_cash = portfolio_before["cash_eur"] + sells_in_eur - buys_out_eur
    actual_cash = portfolio_after["cash_eur"]
    diff = abs(expected_cash - actual_cash)
    return {
        "ok": diff <= tolerance,
        "expected_cash_eur": round(expected_cash, 2),
        "actual_cash_eur": round(actual_cash, 2),
        "diff_eur": round(diff, 4),
        "tolerance_eur": tolerance,
    }


# ============================================================================
# Summary printing
# ============================================================================

def print_summary(portfolio_before, portfolio_after, sells, buys, realized, validation):
    print("\n" + "=" * 78)
    print("REVIEW BEFORE WRITING TO DISK")
    print("=" * 78)

    print(f"\n[Cash]")
    print(f"  Before:  {portfolio_before['cash_eur']:>10,.2f} EUR")
    print(f"  After:   {portfolio_after['cash_eur']:>10,.2f} EUR")
    print(f"  Change:  {portfolio_after['cash_eur'] - portfolio_before['cash_eur']:>+10,.2f} EUR")

    if sells:
        print(f"\n[Sold: {len(sells)} orders]")
        for s, r in zip(sells, realized):
            print(f"  {s['ticker']:<6} {s['shares']:>10.4f} shares "
                  f"@ {s.get('exec_price_eur', s.get('exec_price_usd', 0)):>10.2f} "
                  f"{s['currency']} = {s['value_eur']:>8.2f} EUR  "
                  f"(P&L: {r['gain_eur']:+.2f} EUR, {r['return_pct']:+.2f}%)")
        total_realized = sum(r["gain_eur"] for r in realized)
        print(f"  TOTAL REALIZED P&L: {total_realized:+.2f} EUR")

    if buys:
        print(f"\n[Bought: {len(buys)} orders]")
        for b in buys:
            if b["market"] == "IBEX":
                print(f"  {b['ticker']:<6} {b['shares']:>10.4f} sh "
                      f"@ {b['exec_price_eur']:>10.2f} EUR  "
                      f"= {b['value_eur']:>8.2f} EUR  (+ {b['commission_eur']:.2f} EUR comm)")
            else:
                print(f"  {b['ticker']:<6} {b['shares']:>10.4f} sh "
                      f"@ {b['exec_price_usd']:>10.2f} USD  "
                      f"rate={b['exec_eur_usd_rate']:.5f}  "
                      f"= {b['value_eur']:>8.2f} EUR  (+ {b['commission_eur']:.2f} EUR comm)")

    print(f"\n[Portfolio after]")
    print(f"  Positions: {len(portfolio_after['positions'])}")
    for t, p in portfolio_after["positions"].items():
        val_eur = p["shares"] * p["avg_price_eur"]
        print(f"    {t:<6} {p['shares']:>10.4f} sh @ avg {p['avg_price_eur']:>10.2f} EUR  = {val_eur:>8.2f} EUR")
    total_invested = sum(p["shares"] * p["avg_price_eur"]
                         for p in portfolio_after["positions"].values())
    total = total_invested + portfolio_after["cash_eur"]
    print(f"  Total invested: {total_invested:>10,.2f} EUR")
    print(f"  Cash:           {portfolio_after['cash_eur']:>10,.2f} EUR")
    print(f"  GRAND TOTAL:    {total:>10,.2f} EUR")

    print(f"\n[Cash flow validation]")
    if validation["ok"]:
        print(f"  OK: cash math balances (diff {validation['diff_eur']:.4f} EUR <= "
              f"tolerance {validation['tolerance_eur']} EUR)")
    else:
        print(f"  [!] WARNING: cash math does NOT balance")
        print(f"     Expected cash: {validation['expected_cash_eur']:.2f} EUR")
        print(f"     Actual cash:   {validation['actual_cash_eur']:.2f} EUR")
        print(f"     Diff:          {validation['diff_eur']:.4f} EUR (tolerance {validation['tolerance_eur']})")
        print(f"     Check your inputs before saving.")


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Append a rebalance entry interactively.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Compute everything but don't write to disk")
    args = parser.parse_args()

    # ----- Load existing files -----
    if not PORTFOLIO_FILE.exists():
        print(f"[!] {PORTFOLIO_FILE} not found. Create it first.")
        sys.exit(1)
    with open(PORTFOLIO_FILE) as f:
        portfolio = json.load(f)

    history = []
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            history = json.load(f)

    # Snapshot for validation later
    cash_before_eur = portfolio["cash_eur"]
    value_eur_before = portfolio["cash_eur"] + sum(
        p["shares"] * p["avg_price_eur"]
        for p in portfolio["positions"].values()
    )

    print("=" * 78)
    print("APPEND REBALANCE — Interactive helper")
    print("=" * 78)
    print(f"\nCurrent portfolio (loaded from {PORTFOLIO_FILE}):")
    print(f"  Cash:      {portfolio['cash_eur']:>10,.2f} EUR")
    print(f"  Positions: {len(portfolio['positions'])}")
    for t, p in portfolio["positions"].items():
        val = p["shares"] * p["avg_price_eur"]
        print(f"    {t:<6} {p['shares']:>10.4f} sh @ {p['avg_price_eur']:.2f} EUR = {val:.2f} EUR")
    print(f"  TOTAL:     {value_eur_before:>10,.2f} EUR")
    last_rb = portfolio.get("last_rebalance")
    if last_rb:
        print(f"  Last rebalance recorded: {last_rb}")

    # ----- Rebalance metadata -----
    print("\n[1/3] Rebalance metadata")
    exec_date = ask("  Execution date (YYYY-MM-DD or 'today')",
                    validator=parse_date, default="today")

    # PROTECTION: warn if this date matches the last_rebalance — the user
    # probably ran the helper twice for the same rebalance by mistake
    if last_rb and last_rb == exec_date:
        print(f"\n  [!] WARNING: portfolio.json already shows last_rebalance == {exec_date}.")
        print(f"      Running the helper twice for the same date will DUPLICATE trades")
        print(f"      and corrupt your portfolio (negative cash, doubled shares).")
        print(f"      If you ran this script earlier today by accident, abort now and")
        print(f"      restore from data/portfolio.json.bak before continuing.")
        confirm_dup = ask("      Continue anyway? (y/n)",
                          validator=parse_yes_no, default="n")
        if not confirm_dup:
            print("Aborted. To restore the pre-script state:")
            print(f"      copy {PORTFOLIO_FILE}.bak  {PORTFOLIO_FILE}")
            print(f"      copy {HISTORY_FILE}.bak   {HISTORY_FILE}")
            sys.exit(0)

    # ----- SELL orders -----
    print("\n[2/3] SELL orders")
    sells = []
    n_sells = ask("  How many SELL orders this rebalance? (0 for first run)",
                  validator=lambda x: int(x), default="0")
    n_sells = int(n_sells)
    for i in range(n_sells):
        trade = prompt_for_trade(i + 1, "SELL")
        sells.append(trade)

    # ----- BUY orders -----
    print("\n[3/3] BUY orders")
    n_buys = ask("  How many BUY orders this rebalance?",
                 validator=lambda x: int(x))
    n_buys = int(n_buys)
    buys = []
    for i in range(n_buys):
        trade = prompt_for_trade(i + 1, "BUY")
        buys.append(trade)

    # ----- Apply changes to a copy of portfolio -----
    portfolio_before_copy = json.loads(json.dumps(portfolio))  # deep copy
    realized = apply_sells(portfolio, sells)
    duplicates = apply_buys(portfolio, buys, exec_date)
    portfolio["last_rebalance"] = exec_date

    # PROTECTION: hard fail if cash went negative — this means the user is
    # trying to spend money they don't have, which usually indicates a
    # duplicate-run mistake or wrong input numbers
    if portfolio["cash_eur"] < -1.0:  # allow 1 EUR tolerance for rounding
        print(f"\n  [!] ERROR: cash_eur would become {portfolio['cash_eur']:.2f} EUR (negative).")
        print(f"      You're trying to spend more than is available.")
        print(f"      Likely causes:")
        print(f"        - You already ran this script for this rebalance "
              f"(duplicates trades).")
        print(f"        - One of the BUY amounts is too large.")
        print(f"        - You missed entering SELL orders that would have freed cash.")
        print(f"      Aborting without writing. To restore the original state, see")
        print(f"      data/portfolio.json.bak and data/history.json.bak (if present).")
        sys.exit(2)

    # PROTECTION: warn about duplicate positions (top-ups) — valid but rare
    if duplicates:
        print(f"\n  [!] NOTE: these BUY orders added shares to existing positions: "
              f"{', '.join(duplicates)}")
        print(f"      The script averaged the prices. If this was unintentional,")
        print(f"      abort and restore from .bak files.")
        confirm_dup = ask("      Continue? (y/n)",
                          validator=parse_yes_no, default="n")
        if not confirm_dup:
            print("Aborted.")
            sys.exit(0)

    # ----- Validate -----
    validation = validate_cash_math(portfolio_before_copy, portfolio, sells, buys)

    # ----- Print summary -----
    print_summary(portfolio_before_copy, portfolio, sells, buys, realized, validation)

    # ----- Build the new history entry -----
    selected_us = [b["ticker"] for b in buys if b["market"] == "US"]
    selected_ibex = [b["ticker"] for b in buys if b["market"] == "IBEX"]

    portfolio_value_after = portfolio["cash_eur"] + sum(
        p["shares"] * p["avg_price_eur"]
        for p in portfolio["positions"].values()
    )

    # NOTE on momentum values:
    # Momentum 12-1 readings are recorded in the PLAN entry that rebalance.py
    # appended to history.json earlier today (search the file for the entry
    # with the same date and "type": "PLAN"). They are NOT repeated here to
    # avoid asking the user to retype numbers the system already knows.
    new_history_entry = {
        "type": "EXECUTION",
        "date": exec_date,
        "portfolio_value_eur_before": round(value_eur_before, 2),
        "portfolio_value_eur_after": round(portfolio_value_after, 2),
        "cash_before_eur": round(cash_before_eur, 2),
        "cash_after_eur": round(portfolio["cash_eur"], 2),
        "selected_us": selected_us,
        "selected_ibex": selected_ibex,
        "orders_to_sell": sells,
        "orders_to_buy": buys,
        "realized_pnl": realized,
        "_note": (f"EXECUTION entry generated by append-rebalance.py on "
                  f"{date.today().isoformat()}. Each US trade carries its own "
                  f"exec_eur_usd_rate (the rate IBKR applied to that specific "
                  f"order). Momentum values for this rebalance are in the "
                  f"PLAN entry with the same date."),
    }

    # ----- Confirm and save -----
    if args.dry_run:
        print("\n[DRY-RUN] No files written. Run without --dry-run to save.")
        return

    if not validation["ok"]:
        print("\n[!] WARNING: validation failed. Proceeding will save inconsistent data.")
    confirm = ask("\nSave changes to disk? (y/n)", validator=parse_yes_no, default="n")
    if not confirm:
        print("Aborted. No files written.")
        return

    # Backup
    if PORTFOLIO_FILE.exists():
        shutil.copy2(PORTFOLIO_FILE, str(PORTFOLIO_FILE) + ".bak")
        print(f"  Backed up {PORTFOLIO_FILE.name} -> {PORTFOLIO_FILE.name}.bak")
    if HISTORY_FILE.exists():
        shutil.copy2(HISTORY_FILE, str(HISTORY_FILE) + ".bak")
        print(f"  Backed up {HISTORY_FILE.name} -> {HISTORY_FILE.name}.bak")

    # Append history entry
    history.append(new_history_entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, default=str)
    print(f"  Wrote {HISTORY_FILE} ({len(history)} entries)")

    # Overwrite portfolio
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=2, default=str)
    print(f"  Wrote {PORTFOLIO_FILE}")

    # Compute weighted-average EUR/USD rate across US trades (for the
    # commit-rebalance.ps1 -EurUsd parameter, which is informational only)
    us_trades = [t for t in (sells + buys) if t["market"] == "US"]
    if us_trades:
        total_usd = sum(t["value_usd"] for t in us_trades)
        total_eur_from_usd = sum(t["value_eur"] for t in us_trades)
        avg_rate = total_usd / total_eur_from_usd if total_eur_from_usd > 0 else 0
        eur_usd_str = f"{avg_rate:.4f}"
    else:
        eur_usd_str = "N/A"

    print("\nDone. Next steps:")
    print("  1. Review the JSON files manually if you want.")
    print(f"  2. Commit with: .\\scripts\\commit-rebalance.ps1 -Quarter '...' "
          f"-Sold '{','.join([s['ticker'] for s in sells]) or ''}' "
          f"-Bought '{','.join([b['ticker'] for b in buys])}' "
          f"-ValueBefore {value_eur_before:.2f} -ValueAfter {portfolio_value_after:.2f} "
          f"-CashRemaining {portfolio['cash_eur']:.2f} -EurUsd {eur_usd_str}")


if __name__ == "__main__":
    main()
