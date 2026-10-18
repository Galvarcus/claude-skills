import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from shop.pricing import apply_discount, total


class PricingTest(unittest.TestCase):
    def test_discount(self):
        self.assertEqual(apply_discount(200, 25), 150.0)

    def test_total(self):
        self.assertEqual(total([{"price": 2.5, "qty": 4}, {"price": 1, "qty": 1}]), 11.0)
