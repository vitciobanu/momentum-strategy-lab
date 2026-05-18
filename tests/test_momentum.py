"""
Basic unit tests for the momentum strategy.

Run with: python -m pytest tests/
Or:       python tests/test_momentum.py

Companion test suite: tests/test_cagr.py covers the XIRR/TWR module.
"""
import os
import sys
import unittest
import numpy as np
import pandas as pd

# Add src/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from universe import IBEX_35, US_LARGE_CAP, SP500_LARGE_CAP, CONFIG


class TestUniverse(unittest.TestCase):
    """Tests on the universe configuration."""

    def test_ibex_has_35_stocks(self):
        """IBEX 35 should contain exactly 35 stocks (or close to it after BME reviews)."""
        self.assertEqual(len(IBEX_35), 35,
                         f"IBEX_35 has {len(IBEX_35)} stocks, expected 35. "
                         f"Check if BME has changed composition.")

    def test_us_universe_has_meaningful_size(self):
        """The US universe should be reasonably large to capture momentum signal."""
        self.assertGreaterEqual(len(US_LARGE_CAP), 50,
                                f"US_LARGE_CAP has only {len(US_LARGE_CAP)} stocks; "
                                f"too small for dynamic momentum selection")
        self.assertLessEqual(len(US_LARGE_CAP), 300,
                             f"US_LARGE_CAP has {len(US_LARGE_CAP)} stocks; "
                             f"larger than intended (we target ~150-200)")

    def test_sp500_alias_points_to_us_universe(self):
        """The SP500_LARGE_CAP alias must point to the same object as US_LARGE_CAP
        (backwards compatibility for external code that may still use the old name)."""
        self.assertIs(SP500_LARGE_CAP, US_LARGE_CAP,
                      "SP500_LARGE_CAP should be an alias for US_LARGE_CAP")

    def test_ibex_tickers_have_mc_suffix(self):
        """All IBEX tickers should end with .MC for Yahoo Finance."""
        for short, yahoo in IBEX_35.items():
            self.assertTrue(yahoo.endswith(".MC"),
                            f"{yahoo} does not end with .MC")

    def test_us_tickers_no_mc_suffix(self):
        """US tickers should not have a .MC exchange suffix."""
        for short, yahoo in US_LARGE_CAP.items():
            self.assertFalse(yahoo.endswith(".MC"),
                             f"{yahoo} unexpectedly ends with .MC")

    def test_no_overlap_between_universes(self):
        """A stock should not appear in both lists."""
        ibex_set = set(IBEX_35.keys())
        us_set = set(US_LARGE_CAP.keys())
        self.assertEqual(len(ibex_set & us_set), 0,
                         f"Stocks appearing in both universes: {ibex_set & us_set}")


class TestConfig(unittest.TestCase):
    """Tests on strategy configuration sanity."""

    def test_weights_sum_reasonable(self):
        """Weights should sum to at most 1.0 (invested fraction).

        A sum below 1.0 is valid: it represents an intentional cash buffer.
        For example, 0.65 + 0.30 = 0.95 keeps 5% in cash for commissions,
        dividends, or operational safety.
        A sum above 1.0 would mean leverage, which this strategy does NOT use.
        """
        total = CONFIG["WEIGHT_SP500"] + CONFIG["WEIGHT_IBEX"]
        # Include cash reserve if present
        cash_reserve = CONFIG.get("CASH_RESERVE", 0)
        grand_total = total + cash_reserve

        self.assertLessEqual(total, 1.0,
                             f"Invested weights sum to {total} > 1.0 — "
                             f"strategy is not designed for leverage")
        self.assertGreaterEqual(total, 0.5,
                                f"Invested weights sum to {total} < 0.5 — "
                                f"too much cash for a momentum strategy")
        # Sanity check: total invested + cash reserve should equal ~1.0
        self.assertAlmostEqual(grand_total, 1.0, places=2,
                               msg=f"WEIGHT_SP500 + WEIGHT_IBEX + CASH_RESERVE = "
                                   f"{grand_total}, expected ~1.0")

    def test_position_counts_reasonable(self):
        self.assertGreater(CONFIG["N_SP500_POSITIONS"], 0)
        self.assertGreater(CONFIG["N_IBEX_POSITIONS"], 0)
        self.assertLessEqual(CONFIG["N_SP500_POSITIONS"], 20)
        self.assertLessEqual(CONFIG["N_IBEX_POSITIONS"], 20)

    def test_lookback_makes_sense(self):
        self.assertEqual(CONFIG["LOOKBACK_MONTHS"], 12)
        self.assertEqual(CONFIG["SKIP_MONTHS"], 1)

    def test_fractional_shares_flag_exists(self):
        """The fractional shares flag must be defined (boolean)."""
        self.assertIn("ALLOW_FRACTIONAL_SHARES", CONFIG)
        self.assertIsInstance(CONFIG["ALLOW_FRACTIONAL_SHARES"], bool)

    def test_eur_usd_reference_reasonable(self):
        """EUR/USD reference rate should be in a reasonable range."""
        rate = CONFIG["EUR_USD_REFERENCE"]
        self.assertGreater(rate, 0.5)
        self.assertLess(rate, 2.0)


class TestMomentumCalculation(unittest.TestCase):
    """Tests on the core momentum 12-1 formula."""

    def test_momentum_known_values(self):
        """If prices go from 110 (t-12) to 200 (t-1), momentum should be ~81.8%."""
        dates = pd.date_range("2024-01-31", periods=14, freq="ME")
        prices = pd.DataFrame({
            "FAKE": [100, 110, 115, 120, 125, 130, 140, 150, 160, 170, 180, 190, 200, 250]
        }, index=dates)
        # Momentum at the last row: P(t-1)/P(t-12) - 1
        # P(t-1) = prices.iloc[-2] = 200
        # P(t-12) = prices.iloc[-13] = 110
        momentum = prices.shift(1) / prices.shift(12) - 1
        last_mom = momentum["FAKE"].iloc[-1]
        expected = 200 / 110 - 1
        self.assertAlmostEqual(last_mom, expected, places=5)

    def test_momentum_requires_13_months(self):
        """With only 12 months of data, momentum at the last row is NaN."""
        dates = pd.date_range("2024-01-31", periods=12, freq="ME")
        prices = pd.DataFrame({"FAKE": range(100, 112)}, index=dates)
        momentum = prices.shift(1) / prices.shift(12) - 1
        # shift(12) on a 12-row series produces all NaN
        self.assertTrue(pd.isna(momentum["FAKE"].iloc[-1]))

    def test_momentum_flat_prices(self):
        """If prices are flat across the lookback window, momentum is 0."""
        dates = pd.date_range("2024-01-31", periods=14, freq="ME")
        prices = pd.DataFrame({"FAKE": [100] * 14}, index=dates)
        momentum = prices.shift(1) / prices.shift(12) - 1
        self.assertAlmostEqual(momentum["FAKE"].iloc[-1], 0.0, places=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
