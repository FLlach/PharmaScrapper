import unittest
from salcobrand import map_salcobrand_product

class TestSalcobrandScraper(unittest.TestCase):
    def test_map_salcobrand_product_ribbon_price_value_error(self):
        """
        Test that map_salcobrand_product correctly handles a ValueError when parsing
        an invalid price string from ribbon_info.
        """
        # Create a raw_item with malformed ribbon_info["price"]
        raw_item = {
            "sku": "12345",
            "name": "Test Product",
            "normal_price": 1000,
            "ribbon_info": {
                "price": "not-a-number"
            }
        }

        # This should not raise an exception, and the price_offer should remain None
        product = map_salcobrand_product(raw_item)

        # Assertions
        self.assertEqual(product.sku, "12345")
        self.assertEqual(product.price_regular, 1000)
        self.assertIsNone(product.price_offer)

    def test_map_salcobrand_product_direct_discount_value_error(self):
        """
        Test that map_salcobrand_product correctly handles a ValueError when parsing
        an invalid direct_discount.
        """
        # Create a raw_item with malformed direct_discount
        raw_item = {
            "sku": "12345",
            "name": "Test Product",
            "normal_price": 1000,
            "direct_discount": "not-a-number"
        }

        # This should not raise an exception, and the price_offer should remain None
        product = map_salcobrand_product(raw_item)

        # Assertions
        self.assertEqual(product.sku, "12345")
        self.assertEqual(product.price_regular, 1000)
        self.assertIsNone(product.price_offer)

if __name__ == '__main__':
    unittest.main()
