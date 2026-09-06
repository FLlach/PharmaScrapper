import unittest
from ahumada import parse_price

class TestAhumada(unittest.TestCase):
    def test_parse_price_happy_path(self):
        self.assertEqual(parse_price("$12.345"), 12345)
        self.assertEqual(parse_price("12345"), 12345)
        self.assertEqual(parse_price("Precio: $ 1.234"), 1234)
        self.assertEqual(parse_price("  $ 990  "), 990)
        self.assertEqual(parse_price("1"), 1)
        self.assertEqual(parse_price("0"), 0)

    def test_parse_price_edge_cases(self):
        self.assertIsNone(parse_price(None))
        self.assertIsNone(parse_price(""))
        self.assertIsNone(parse_price("   "))

    def test_parse_price_error_conditions(self):
        self.assertIsNone(parse_price("abc"))
        self.assertIsNone(parse_price("$ ."))
        self.assertIsNone(parse_price("Gratis"))

if __name__ == '__main__':
    unittest.main()
