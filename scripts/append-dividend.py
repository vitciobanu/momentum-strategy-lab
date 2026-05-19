"""
================================================================================
append-dividend.py — Helper to record a dividend payment
================================================================================

Closes GitHub issue: "Add append-dividend.py helper script for recording
dividend payments".

PROBLEM
-------
When the strategy operates on a real-money account, each held position can
pay dividends quarterly. These dividends arrive as cash in the IBKR account
with three components:

  1. Gross amount (cash credited)
  2. Withholding tax in source country (15% USA with W-8BEN, 19% Spain)
  3. Optional broker fee (ADR fees on some US listings)

If the user manually edits portfolio.json after each dividend, the math is
error-prone and traceability is lost.

This script automates the bookkeeping for both EUR and USD dividends, with
DIFFERENT behaviour per currency (see below).

EUR DIVIDENDS (Spanish stocks like ELE, BBVA, ITX, ACS, etc.)
-------------------------------------------------------------
IBKR credits EUR directly to the user's EUR cash pot.

The script:
  1. Asks for ticker, date, gross amount EUR, tax EUR, optional fee EUR
  2. Computes net_amount_eur = gross - tax - fee
  3. Updates portfolio.json: cash_eur += net_amount_eur
  4. Appends a DIVIDEND entry to history.json

USD DIVIDENDS (US stocks like MSFT, NVDA, MOD, etc.)
----------------------------------------------------
IBKR credits USD to a SEPARATE USD cash pot. It does NOT auto-convert to
EUR. The user's portfolio shows e.g. "EUR: 140.09 | USD: 4.55" — these are
two pots of physical cash in different currencies, with IBKR showing a
"Total in EUR" purely informationally.

To avoid pretending the USD dividend is already in EUR (it isn't), this
script handles USD dividends as AUDIT-TRAIL ONLY:

  1. Asks for ticker, date, gross USD, tax USD, optional fee USD
  2. Computes net_amount_usd = gross - tax - fee
  3. Does NOT update cash_eur in portfolio.json
  4. Appends a DIVIDEND entry to history.json with all USD values

The USD cash stays in IBKR's USD pot. When the user converts it to EUR
(typically before a quarterly rebalance, using IBKR's "Convert All to EUR"
button or an EUR.USD trade), they MUST manually update cash_eur in
portfolio.json with the actual EUR received from that conversion. A
future scripts/add-activity.py (v2.0.0) will handle this with a
CURRENCY_CONVERSION activity type.

OPERATIONAL MODE
----------------
Batch mode, aligned with the quarterly rebalance.

BEFORE running rebalance.py on the quarterly rebalance day:
  1. Download the IBKR dividend statement for the quarter
  2. For each dividend received, run this script
  3. If any USD dividends were received: convert USD → EUR in IBKR,
     then manually update cash_eur in portfolio.json
  4. Verify cash_eur in portfolio.json now matches the EUR cash in IBKR
  5. Proceed with rebalance.py

USAGE
-----
    python scripts/append-dividend.py
    python scripts/append-dividend.py --dry-run

REVERSALS
---------
IBKR occasionally reverses a previously-paid dividend (most common with
scrip dividends like AENA in 2026). When this happens, the IBKR statement
shows three rows: the original payment, the reversal (negative), and
sometimes a re-issued payment.

This script does NOT model reversals as a separate entry type. If you see
a reversal in the statement, IGNORE the reversed lines (they cancel each
other). Enter only the NET effective payment that actually credited your
account.

For example, if AENA shows:
    2026-04-27  AENA  +65.57 EUR  (Ordinary Dividend)
    2026-04-27  AENA  -65.57 EUR  (Reversal)
    2026-04-27  AENA  +65.40 EUR  (Re-issued Ordinary Dividend)

You enter only the third line: 65.40 EUR gross.

================================================================================
"""

import json
import shutil
import argparse
from pathlib import Path
from datetime import date, datetime

ROOT = Path(__file__).parent.parent
PORTFOLIO_FILE = ROOT / "data" / "portfolio.json"
HISTORY_FILE = ROOT / "data" / "history.json"


# ============================================================================
# Helpers (same prompt/parse pattern as append-rebalance.py)
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
    if "," in raw and "." in raw:
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif "," in raw:
        raw = raw.replace(",", ".")
    return float(raw)


def parse_positive_float(raw):
    v = parse_float(raw)
    if v <= 0:
        raise ValueError("must be > 0")
    return v


def parse_nonneg_float(raw):
    v = parse_float(raw)
    if v < 0:
        raise ValueError("must be >= 0")
    return v


def parse_yes_no(raw):
    raw = raw.strip().lower()
    if raw in ("y", "yes", "s", "sí", "si"):
        return True
    if raw in ("n", "no"):
        return False
    raise ValueError("answer 'y' or 'n'")


def parse_currency(raw):
    raw = raw.strip().upper()
    if raw in ("EUR", "E"):
        return "EUR"
    if raw in ("USD", "U", "$"):
        return "USD"
    raise ValueError("currency must be 'EUR' or 'USD'")


def parse_date(raw):
    raw = raw.strip()
    if raw.lower() == "today":
        return date.today().isoformat()
    datetime.strptime(raw, "%Y-%m-%d")
    return raw


# ============================================================================
# Dividend input
# ============================================================================

def prompt_for_dividend():
    """Walk through one dividend. Returns a fully-populated entry dict."""
    print("\n  --- Dividend details ---")
    ticker = ask("  Ticker (e.g. ELE, MSFT)").upper()
    div_date = ask("  Payment date (YYYY-MM-DD or 'today')",
                   validator=parse_date, default="today")
    currency = ask("  Currency (EUR or USD)", validator=parse_currency)
    gross = ask(f"  Gross amount ({currency})",
                validator=parse_positive_float)
    tax = ask(f"  Withholding tax ({currency}, absolute positive value)",
              validator=parse_nonneg_float, default="0")

    if currency == "EUR":
        tax_code_default = "ES"
    else:
        tax_code_default = "US"
    tax_code = ask("  Tax code (ES, US, etc.)", default=tax_code_default).upper()

    # Fee question
    has_fee = ask("  Is there an associated fee? (y/n)",
                  validator=parse_yes_no, default="n")
    if has_fee:
        fee = ask(f"  Fee amount ({currency}, absolute positive value)",
                  validator=parse_positive_float)
    else:
        fee = 0.0

    if currency == "EUR":
        # EUR dividend: direct computation, will update cash_eur
        net_eur = round(gross - tax - fee, 2)
        return {
            "type": "DIVIDEND",
            "date": div_date,
            "ticker": ticker,
            "currency": "EUR",
            "gross_amount_eur": round(gross, 2),
            "tax_withheld_eur": round(tax, 2),
            "tax_code": tax_code,
            "fee_eur": round(fee, 2),
            "net_amount_eur": net_eur,
        }
    else:
        # USD dividend: audit-trail only, will NOT update cash_eur.
        # The user must manually convert USD->EUR in IBKR later and update
        # cash_eur manually (or via the future add-activity.py script).
        net_usd = round(gross - tax - fee, 2)
        return {
            "type": "DIVIDEND",
            "date": div_date,
            "ticker": ticker,
            "currency": "USD",
            "gross_amount_usd": round(gross, 2),
            "tax_withheld_usd": round(tax, 2),
            "tax_code": tax_code,
            "fee_usd": round(fee, 2),
            "net_amount_usd": net_usd,
        }


# ============================================================================
# Summary printing
# ============================================================================

def print_summary(portfolio_before, portfolio_after, entry):
    print("\n" + "=" * 78)
    print("REVIEW BEFORE WRITING TO DISK")
    print("=" * 78)

    print(f"\n[Dividend recorded]")
    print(f"  Ticker:        {entry['ticker']}")
    print(f"  Date:          {entry['date']}")
    print(f"  Currency:      {entry['currency']}")

    if entry["currency"] == "EUR":
        print(f"  Gross:         {entry['gross_amount_eur']:>10.2f} EUR")
        print(f"  Tax ({entry['tax_code']}):       "
              f"-{entry['tax_withheld_eur']:>9.2f} EUR")
        if entry["fee_eur"] > 0:
            print(f"  Fee:           -{entry['fee_eur']:>9.2f} EUR")
        print(f"  NET:           {entry['net_amount_eur']:>10.2f} EUR")
        print(f"\n[Cash impact: cash_eur will be updated]")
        print(f"  cash_eur before:  {portfolio_before['cash_eur']:>10,.2f} EUR")
        print(f"  cash_eur after:   {portfolio_after['cash_eur']:>10,.2f} EUR")
        print(f"  Change:           {portfolio_after['cash_eur'] - portfolio_before['cash_eur']:>+10,.2f} EUR")
    else:
        print(f"  Gross:         {entry['gross_amount_usd']:>10.2f} USD")
        print(f"  Tax ({entry['tax_code']}):       "
              f"-{entry['tax_withheld_usd']:>9.2f} USD")
        if entry["fee_usd"] > 0:
            print(f"  Fee:           -{entry['fee_usd']:>9.2f} USD")
        print(f"  NET:           {entry['net_amount_usd']:>10.2f} USD")
        print(f"\n[Cash impact: NONE]")
        print(f"  IBKR holds USD dividends in a separate USD cash pot.")
        print(f"  cash_eur is NOT updated by this entry.")
        print(f"  When you convert USD -> EUR in IBKR (typically before")
        print(f"  the next rebalance), manually update cash_eur to reflect")
        print(f"  the actual EUR received from that conversion.")


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Record a dividend payment interactively."
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Compute everything but don't write to disk")
    args = parser.parse_args()

    # ----- Load existing files -----
    if not PORTFOLIO_FILE.exists():
        print(f"[!] {PORTFOLIO_FILE} not found.")
        return 1
    with open(PORTFOLIO_FILE) as f:
        portfolio = json.load(f)

    history = []
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            history = json.load(f)

    print("=" * 78)
    print("APPEND DIVIDEND — Interactive helper")
    print("=" * 78)
    print(f"\nCurrent cash in {PORTFOLIO_FILE}:")
    print(f"  cash_eur: {portfolio['cash_eur']:,.2f} EUR")
    print(f"\nPositions in portfolio:")
    for ticker, pos in portfolio["positions"].items():
        print(f"  {ticker:<6} ({pos['market']})")

    print("\nReminder on reversals:")
    print("  If the IBKR statement shows a dividend that was paid, reversed,")
    print("  and re-issued (e.g. AENA scrip dividends), ignore the cancelled")
    print("  lines and enter only the NET effective amount.")

    # ----- Prompt for dividend -----
    entry = prompt_for_dividend()

    # ----- Sanity check: ticker should be (or have been) in portfolio -----
    if entry["ticker"] not in portfolio["positions"]:
        print(f"\n  [!] WARNING: {entry['ticker']} is not currently in the portfolio.")
        print(f"      This could mean: (a) you sold it in a previous rebalance")
        print(f"      and the dividend was declared while you still held it,")
        print(f"      (b) you mistyped the ticker, or (c) something else.")
        confirm = ask("      Continue anyway? (y/n)",
                      validator=parse_yes_no, default="n")
        if not confirm:
            print("Aborted.")
            return 0

    # ----- Apply to portfolio (only EUR dividends affect cash_eur) -----
    portfolio_before_copy = json.loads(json.dumps(portfolio))  # deep copy
    if entry["currency"] == "EUR":
        portfolio["cash_eur"] = round(
            portfolio["cash_eur"] + entry["net_amount_eur"], 2
        )
    # For USD: portfolio.cash_eur is unchanged. The USD sits in IBKR's
    # separate USD pot until the user converts it manually.

    # ----- Summary -----
    print_summary(portfolio_before_copy, portfolio, entry)

    # ----- Confirm and save -----
    if args.dry_run:
        print("\n[DRY-RUN] No files written. Run without --dry-run to save.")
        return 0

    confirm = ask("\nSave changes to disk? (y/n)",
                  validator=parse_yes_no, default="n")
    if not confirm:
        print("Aborted. No files written.")
        return 0

    # Backup
    if PORTFOLIO_FILE.exists():
        shutil.copy2(PORTFOLIO_FILE, str(PORTFOLIO_FILE) + ".bak")
        print(f"  Backed up {PORTFOLIO_FILE.name} -> {PORTFOLIO_FILE.name}.bak")
    if HISTORY_FILE.exists():
        shutil.copy2(HISTORY_FILE, str(HISTORY_FILE) + ".bak")
        print(f"  Backed up {HISTORY_FILE.name} -> {HISTORY_FILE.name}.bak")

    # Add note to entry
    if entry["currency"] == "EUR":
        entry["_note"] = (
            f"DIVIDEND entry generated by append-dividend.py on "
            f"{date.today().isoformat()}. Net amount added to cash_eur."
        )
    else:
        entry["_note"] = (
            f"DIVIDEND entry generated by append-dividend.py on "
            f"{date.today().isoformat()}. USD held in IBKR's USD cash pot; "
            f"cash_eur in portfolio.json NOT updated. Update cash_eur "
            f"manually after converting USD->EUR in IBKR."
        )

    # Append history
    history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, default=str)
    print(f"  Wrote {HISTORY_FILE} ({len(history)} entries)")

    # Overwrite portfolio
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=2, default=str)
    print(f"  Wrote {PORTFOLIO_FILE}")

    if entry["currency"] == "EUR":
        print(f"\nDone. New cash_eur in portfolio: "
              f"{portfolio['cash_eur']:,.2f} EUR")
    else:
        print(f"\nDone. cash_eur unchanged (USD dividend in IBKR's USD pot).")
        print(f"Remember to convert USD->EUR in IBKR before the next rebalance,")
        print(f"then manually update cash_eur in portfolio.json.")

    print(f"\nNext steps:")
    print(f"  - If more dividends to record, run this script again")
    print(f"  - When all dividends are recorded, verify cash_eur matches IBKR")
    print(f"  - Then proceed with the normal quarterly rebalance flow")
    return 0


if __name__ == "__main__":
    exit(main())
