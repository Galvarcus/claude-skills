import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from shop.inventory import in_stock


class InventoryTest(unittest.TestCase):
    def test_in_stock(self):
        self.assertTrue(in_stock({"a": 2}, "a"))
        self.assertFalse(in_stock({"a": 0}, "a"))
