"""
Basic unit tests for the momentum strategy.

Run with: python -m pytest tests/
Or: python tests/test_momentum.py
"""
import os
import sys
import unittest
import numpy as np
import pandas as pd

# Add src/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

<<<<<<< HEAD
from universe import IBEX_TOP20, SP500_TOP20, CONFIG
=======
from universe import IBEX_35, SP500_LARGE_CAP, CONFIG
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)


class TestUniverse(unittest.TestCase):
    """Tests on the universe configuration."""

<<<<<<< HEAD
    def test_ibex_has_20_stocks(self):
        self.assertEqual(len(IBEX_TOP20), 20)

    def test_sp500_has_20_stocks(self):
        self.assertEqual(len(SP500_TOP20), 20)

    def test_ibex_tickers_have_mc_suffix(self):
        """All IBEX tickers should end with .MC for Yahoo Finance."""
        for short, yahoo in IBEX_TOP20.items():
=======
    def test_ibex_has_35_stocks(self):
        """IBEX 35 should contain exactly 35 stocks (or close to it after BME reviews)."""
        self.assertEqual(len(IBEX_35), 35,
                         f"IBEX_35 has {len(IBEX_35)} stocks, expected 35. "
                         f"Check if BME has changed composition.")

    def test_sp500_has_meaningful_size(self):
        """SP500 universe should be reasonably large to capture momentum signal."""
        self.assertGreaterEqual(len(SP500_LARGE_CAP), 50,
                                f"SP500_LARGE_CAP has only {len(SP500_LARGE_CAP)} stocks; "
                                f"too small for dynamic momentum selection")
        self.assertLessEqual(len(SP500_LARGE_CAP), 200,
                             f"SP500_LARGE_CAP has {len(SP500_LARGE_CAP)} stocks; "
                             f"larger than intended (we target ~100)")

    def test_ibex_tickers_have_mc_suffix(self):
        """All IBEX tickers should end with .MC for Yahoo Finance."""
        for short, yahoo in IBEX_35.items():
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
            self.assertTrue(yahoo.endswith(".MC"),
                            f"{yahoo} does not end with .MC")

    def test_sp500_tickers_no_suffix(self):
        """SP500 tickers should not have exchange suffixes."""
<<<<<<< HEAD
        for short, yahoo in SP500_TOP20.items():
=======
        for short, yahoo in SP500_LARGE_CAP.items():
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
            self.assertFalse(yahoo.endswith(".MC"),
                             f"{yahoo} unexpectedly ends with .MC")

    def test_no_overlap_between_universes(self):
        """A stock should not appear in both lists."""
<<<<<<< HEAD
        ibex_set = set(IBEX_TOP20.keys())
        sp_set = set(SP500_TOP20.keys())
=======
        ibex_set = set(IBEX_35.keys())
        sp_set = set(SP500_LARGE_CAP.keys())
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
        self.assertEqual(len(ibex_set & sp_set), 0,
                         "Stocks appearing in both universes")


class TestConfig(unittest.TestCase):
    """Tests on strategy configuration sanity."""

    def test_weights_sum_to_one(self):
        total = CONFIG["WEIGHT_SP500"] + CONFIG["WEIGHT_IBEX"]
        self.assertAlmostEqual(total, 1.0, places=2,
                               msg=f"Weights sum to {total}, not 1.0")

    def test_position_counts_reasonable(self):
        self.assertGreater(CONFIG["N_SP500_POSITIONS"], 0)
        self.assertGreater(CONFIG["N_IBEX_POSITIONS"], 0)
        self.assertLessEqual(CONFIG["N_SP500_POSITIONS"], 20)
        self.assertLessEqual(CONFIG["N_IBEX_POSITIONS"], 20)

    def test_lookback_makes_sense(self):
        self.assertEqual(CONFIG["LOOKBACK_MONTHS"], 12)
        self.assertEqual(CONFIG["SKIP_MONTHS"], 1)

<<<<<<< HEAD
    def test_commissions_positive(self):
        self.assertGreater(CONFIG["COMMISSION_IBEX_EUR"], 0)
        self.assertGreater(CONFIG["COMMISSION_SP500_USD"], 0)
=======
    def test_fractional_shares_flag_exists(self):
        """The fractional shares flag must be defined (boolean)."""
        self.assertIn("ALLOW_FRACTIONAL_SHARES", CONFIG)
        self.assertIsInstance(CONFIG["ALLOW_FRACTIONAL_SHARES"], bool)

    def test_eur_usd_reference_reasonable(self):
        """EUR/USD reference rate should be in a reasonable range."""
        rate = CONFIG["EUR_USD_REFERENCE"]
        self.assertGreater(rate, 0.5)
        self.assertLess(rate, 2.0)
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)


class TestMomentumCalculation(unittest.TestCase):
    """Tests on the core momentum 12-1 formula."""

    def test_momentum_known_values(self):
        """If prices double from t-12 to t-1, momentum should be +100%."""
        # Build a fake price series of 14 months where the value
        # 12 months before the last one is 100 and the value 1 month before is 200.
        dates = pd.date_range("2024-01-31", periods=14, freq="ME")
        prices = pd.DataFrame({
            "FAKE": [100, 110, 115, 120, 125, 130, 140, 150, 160, 170, 180, 190, 200, 250]
        }, index=dates)
        # P_{t-12} = prices.iloc[-13] = 110 (second row)
        # Wait: -13 means 13 from the end = first element
        # Let's recompute: array of 14, indexes 0..13. iloc[-2] is index 12, iloc[-13] is index 1.
        # prices: [100, 110, 115, ..., 200, 250]
        # iloc[-2] = 200 (second to last)
        # iloc[-13] = 110 (second)
        # momentum = 200/110 - 1 = 0.818
        momentum = prices.shift(1) / prices.shift(12) - 1
        last_mom = momentum["FAKE"].iloc[-1]
        # Last momentum uses P(t-1)/P(t-12) where t is last row.
        # P(t-1) = prices.iloc[-2] = 200
        # P(t-12) = prices.iloc[-13] = 110
        expected = 200 / 110 - 1
        self.assertAlmostEqual(last_mom, expected, places=5)

    def test_momentum_requires_13_months(self):
        """With only 12 months we cannot compute momentum 12-1 yet."""
        dates = pd.date_range("2024-01-31", periods=12, freq="ME")
        prices = pd.DataFrame({"FAKE": range(100, 112)}, index=dates)
        momentum = prices.shift(1) / prices.shift(12) - 1
        # The last value should be NaN because shift(12) at the last row needs row -12,
        # which doesn't exist with only 12 rows (indexes 0..11; row -12 = row 0 - 12 = invalid)
        # Actually shift(12) on row 11 gives row -1 which is NaN.
        self.assertTrue(pd.isna(momentum["FAKE"].iloc[-1]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
