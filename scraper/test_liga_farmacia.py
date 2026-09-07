import unittest
from liga_farmacia import clean_price

class TestLigaFarmacia(unittest.TestCase):
    def test_clean_price(self):
        # Standard format
        self.assertEqual(clean_price("$ 1.200"), 1200)

        # Empty and None inputs
        self.assertEqual(clean_price(""), 0)
        self.assertEqual(clean_price(None), 0)

        # Numbers only
        self.assertEqual(clean_price("1500"), 1500)

        # Numbers with $ but no space
        self.assertEqual(clean_price("$1.500"), 1500)

        # Numbers with extra spaces
        self.assertEqual(clean_price("  $ 1.500  "), 1500)

        # Strings with extra text
        self.assertEqual(clean_price("Precio: $1.500 CLP"), 1500)

        # Strings with no numbers
        self.assertEqual(clean_price("no numbers here"), 0)

if __name__ == '__main__':
    unittest.main()
