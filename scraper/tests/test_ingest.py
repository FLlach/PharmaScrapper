import unittest
import sys
import os

# Ensure we can import ingest from the parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingest import sanitize_price

class TestSanitizePrice(unittest.TestCase):
    def test_valid_prices(self):
        self.assertEqual(sanitize_price(100), 100)
        self.assertEqual(sanitize_price("100"), 100)
        self.assertEqual(sanitize_price(0), 0)
        self.assertEqual(sanitize_price("0"), 0)
        self.assertEqual(sanitize_price(2147483647), 2147483647)
        self.assertEqual(sanitize_price("2147483647"), 2147483647)

    def test_none_value(self):
        self.assertIsNone(sanitize_price(None))

    def test_out_of_bounds_prices(self):
        self.assertIsNone(sanitize_price(-1))
        self.assertIsNone(sanitize_price("-1"))
        self.assertIsNone(sanitize_price(2147483648))
        self.assertIsNone(sanitize_price("2147483648"))

    def test_invalid_types_and_values(self):
        # ValueError cases
        self.assertIsNone(sanitize_price("invalid_string"))
        self.assertIsNone(sanitize_price("100.5"))
        self.assertIsNone(sanitize_price("100,5"))
        self.assertIsNone(sanitize_price(""))

        # TypeError cases
        self.assertIsNone(sanitize_price([100]))
        self.assertIsNone(sanitize_price({"price": 100}))
        self.assertIsNone(sanitize_price((100,)))

if __name__ == '__main__':
    unittest.main()
