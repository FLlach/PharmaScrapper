import unittest
import sys
import os

# Add scraper path to sys.path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dr_simi import map_dr_simi_product
from schema import PharmacyProduct

class TestDrSimiMapper(unittest.TestCase):
    def test_minimal_product(self):
        """Test with an empty dictionary to ensure fallback values are applied correctly."""
        raw_item = {}
        product = map_dr_simi_product(raw_item)

        self.assertEqual(product.sku, "")
        self.assertEqual(product.name, "")
        self.assertEqual(product.brand, "Desconocido")
        self.assertEqual(product.bioequivalent, False)
        self.assertEqual(product.prescription_required, False)
        self.assertEqual(product.price_regular, 0)
        self.assertIsNone(product.price_offer)
        self.assertEqual(product.in_stock, False)
        self.assertIsNone(product.active_ingredient)
        self.assertIsNone(product.presentation)
        self.assertIsNone(product.unit_price_description)
        self.assertIsNone(product.image_url)
        self.assertEqual(product.product_url, "")
        self.assertIsNone(product.category)

    def test_full_product(self):
        """Test with a completely filled mock item."""
        raw_item = {
            "productId": "12345",
            "productTitle": "Simi Paracetamol 500mg",
            "brand": "Simi Labs",
            "allSpecifications": [
                "Tipo de Producto",
                "Principio Activo",
                "Condición de Venta",
                "Forma farmacéutica",
                "Precio unitario"
            ],
            "Tipo de Producto": ["Medicamento BIOEQUIVALENTE"],
            "Principio Activo": ["Paracetamol", "Cafeína"],
            "Condición de Venta": ["Venta con RECETA médica"],
            "Forma farmacéutica": ["Comprimido"],
            "Precio unitario": ["$10 por comprimido"],
            "items": [
                {
                    "sellers": [
                        {
                            "commertialOffer": {
                                "ListPrice": 1500,
                                "Price": 1000,
                                "AvailableQuantity": 50
                            }
                        }
                    ],
                    "images": [
                        {"imageUrl": "http://example.com/image.jpg"}
                    ]
                }
            ],
            "link": "https://www.drsimi.cl/simi-paracetamol",
            "categories": ["/Medicamentos/Analgésicos/"]
        }

        product = map_dr_simi_product(raw_item)

        self.assertEqual(product.sku, "12345")
        self.assertEqual(product.name, "Simi Paracetamol 500mg")
        self.assertEqual(product.brand, "Simi Labs")
        self.assertEqual(product.bioequivalent, True)
        self.assertEqual(product.active_ingredient, "Paracetamol, Cafeína")
        self.assertEqual(product.prescription_required, True)
        self.assertEqual(product.presentation, "Comprimido")
        self.assertEqual(product.unit_price_description, "$10 por comprimido")
        self.assertEqual(product.price_regular, 1500)
        self.assertEqual(product.price_offer, 1000)
        self.assertEqual(product.in_stock, True)
        self.assertEqual(product.image_url, "http://example.com/image.jpg")
        self.assertEqual(product.product_url, "https://www.drsimi.cl/simi-paracetamol")
        self.assertEqual(product.category, "Medicamentos/Analgésicos")

    def test_bioequivalence_true(self):
        """Test that bioequivalence logic properly parses string values."""
        raw_item = {
            "allSpecifications": ["Tipo de Producto"],
            "Tipo de Producto": ["BIOEQUIVALENTE"]
        }
        product = map_dr_simi_product(raw_item)
        self.assertTrue(product.bioequivalent)

    def test_bioequivalence_false(self):
        """Test that bioequivalence logic fails safely without BIOEQUIVALENTE."""
        raw_item = {
            "allSpecifications": ["Tipo de Producto"],
            "Tipo de Producto": ["Genérico"]
        }
        product = map_dr_simi_product(raw_item)
        self.assertFalse(product.bioequivalent)

    def test_prescription_true(self):
        """Test that prescription logic correctly identifies 'RECETA'."""
        raw_item = {
            "allSpecifications": ["Condición de Venta"],
            "Condición de Venta": ["Requiere receta simple"]
        }
        product = map_dr_simi_product(raw_item)
        self.assertTrue(product.prescription_required)

    def test_offer_price_equals_regular(self):
        """Test that price_offer is None if it equals regular price."""
        raw_item = {
            "items": [
                {
                    "sellers": [
                        {
                            "commertialOffer": {
                                "ListPrice": 1000,
                                "Price": 1000,
                            }
                        }
                    ]
                }
            ]
        }
        product = map_dr_simi_product(raw_item)
        self.assertEqual(product.price_regular, 1000)
        self.assertIsNone(product.price_offer)

    def test_stock_zero(self):
        """Test that in_stock evaluates to False when AvailableQuantity is 0."""
        raw_item = {
            "items": [
                {
                    "sellers": [
                        {
                            "commertialOffer": {
                                "AvailableQuantity": 0
                            }
                        }
                    ]
                }
            ]
        }
        product = map_dr_simi_product(raw_item)
        self.assertFalse(product.in_stock)

    def test_fallback_product_url(self):
        """Test the linkText fallback when link is missing."""
        raw_item = {
            "linkText": "mi-producto-simi"
        }
        product = map_dr_simi_product(raw_item)
        self.assertEqual(product.product_url, "https://www.drsimi.cl/mi-producto-simi/p")

if __name__ == '__main__':
    unittest.main()
