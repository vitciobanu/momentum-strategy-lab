"""
Unit tests for src/cagr.py (issue #3: time-weighted return for added capital).

USAGE:
    python tests/test_cagr.py
"""

import sys
import os
import unittest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cagr import compute_xirr, compute_twr


class TestXIRR(unittest.TestCase):

    def test_simple_one_year(self):
        """2000€ for 1 year becomes 2400€ -> 20% annualized."""
        cf = [(date(2025, 1, 1), -2000), (date(2026, 1, 1), 2400)]
        result = compute_xirr(cf)
        self.assertAlmostEqual(result, 0.20, places=3)

    def test_no_growth(self):
        """2000€ for 1 year stays 2000€ -> 0%."""
        cf = [(date(2025, 1, 1), -2000), (date(2026, 1, 1), 2000)]
        result = compute_xirr(cf)
        self.assertAlmostEqual(result, 0.0, places=4)

    def test_negative_return(self):
        """2000€ becomes 1000€ in 1 year -> -50% annualized."""
        cf = [(date(2025, 1, 1), -2000), (date(2026, 1, 1), 1000)]
        result = compute_xirr(cf)
        self.assertAlmostEqual(result, -0.50, places=3)

    def test_added_capital(self):
        """Capital injection mid-stream produces a sensible XIRR.

        Scenario: 2000 in year 0, 1000 added year 1, 5800 final year 2.
        Total contributed: 3000. The simple 'return on contributions' is +93%,
        but that's NOT annualized. XIRR gives the actual annualized rate.
        """
        cf = [
            (date(2025, 1, 1), -2000),
            (date(2026, 1, 1), -1000),
            (date(2027, 1, 1),  5800),
        ]
        result = compute_xirr(cf)
        # The 2000 was invested 2 years, the 1000 only 1 year.
        # The XIRR should be somewhere between 30% and 70%.
        self.assertGreater(result, 0.30)
        self.assertLess(result, 0.70)

    def test_withdrawal(self):
        """Withdrawal followed by growth still produces a positive XIRR."""
        cf = [
            (date(2025, 1, 1), -2000),
            (date(2026, 6, 1),   500),  # partial withdrawal
            (date(2027, 1, 1),  3000),  # final value
        ]
        result = compute_xirr(cf)
        self.assertIsNotNone(result)
        self.assertGreater(result, 0)

    def test_xirr_invalid_input(self):
        """All-positive or all-negative cash flows return None."""
        self.assertIsNone(compute_xirr([(date(2025, 1, 1), -1000),
                                        (date(2026, 1, 1), -1000)]))
        self.assertIsNone(compute_xirr([(date(2025, 1, 1),  1000),
                                        (date(2026, 1, 1),  1000)]))
        self.assertIsNone(compute_xirr([(date(2025, 1, 1), -1000)]))


class TestTWR(unittest.TestCase):

    def test_no_cashflows(self):
        """TWR with no mid-stream cashflows equals simple CAGR."""
        # 2000 -> 2400 in 1 year, no additions/withdrawals
        pv = [
            (date(2025, 1, 1), 0,     2000),
            (date(2026, 1, 1), 2400,  0),
        ]
        result = compute_twr(pv)
        self.assertAlmostEqual(result, 0.20, places=2)

    def test_twr_ignores_cashflow_size(self):
        """TWR should be the SAME regardless of how much is contributed mid-stream,
        as long as the underlying period returns are the same."""
        # Strategy returns: +10% year 1, +25% year 2
        # Compounded: 1.10 * 1.25 - 1 = 37.5% over 2 years -> ~17.3% annualized

        # Scenario A: small mid-stream contribution
        pv_A = [
            (date(2025, 1, 1), 0,     2000),  # inception
            (date(2026, 1, 1), 2200,  100),   # +10%, then add 100 (small)
            (date(2027, 1, 1), 2875,  0),     # 2300 * 1.25
        ]
        # Scenario B: large mid-stream contribution
        pv_B = [
            (date(2025, 1, 1), 0,     2000),
            (date(2026, 1, 1), 2200,  5000),  # +10%, then add 5000 (large)
            (date(2027, 1, 1), 9000,  0),     # 7200 * 1.25
        ]
        twr_A = compute_twr(pv_A)
        twr_B = compute_twr(pv_B)
        # Both should be ~17.3% (same underlying strategy performance)
        self.assertAlmostEqual(twr_A, twr_B, places=2)
        self.assertAlmostEqual(twr_A, 0.173, places=2)


if __name__ == "__main__":
    unittest.main()
