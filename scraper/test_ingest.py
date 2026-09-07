import unittest
from ingest import normalize_text

class TestNormalizeText(unittest.TestCase):
    def test_empty_input(self):
        """Test with empty string and None."""
        self.assertEqual(normalize_text(""), "")
        self.assertEqual(normalize_text(None), "")

    def test_accents(self):
        """Test that accents and diacritics are removed."""
        self.assertEqual(normalize_text("Áéíóú"), "aeiou")
        self.assertEqual(normalize_text("ñandú"), "nandu")
        self.assertEqual(normalize_text("CANCER"), "cancer")

    def test_special_characters(self):
        """Test that special characters and punctuation are removed."""
        self.assertEqual(normalize_text("hello, world!"), "hello world")
        self.assertEqual(normalize_text("price: $100.50"), "price 10050")
        self.assertEqual(normalize_text("product-name_here"), "productnamehere")

    def test_mixed_case(self):
        """Test that all characters are converted to lowercase."""
        self.assertEqual(normalize_text("ParaCetamol"), "paracetamol")
        self.assertEqual(normalize_text("IBUPROFENO"), "ibuprofeno")

    def test_extra_spaces(self):
        """Test that extra spaces are collapsed and stripped."""
        self.assertEqual(normalize_text("  hello   world  "), "hello world")
        self.assertEqual(normalize_text("\nhello\tworld\r"), "hello world")
        self.assertEqual(normalize_text("  single  "), "single")

    def test_combined(self):
        """Test a combination of all cases."""
        self.assertEqual(normalize_text("  ¡Paracetamol 500mg,  con/sin receta!  "), "paracetamol 500mg consin receta")

if __name__ == '__main__':
    unittest.main()
