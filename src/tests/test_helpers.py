import unittest
from unittest.mock import patch
from src.helpers import calculate_discounted_price, validate_price_input, generate_price_suggestions

class TestHelpers(unittest.TestCase):
    def test_calculate_discounted_price(self):
        # Test with valid inputs
        self.assertEqual(calculate_discounted_price(100, 20), 80)
        self.assertEqual(calculate_discounted_price(200, 50), 100)
        
        # Test with edge cases
        self.assertEqual(calculate_discounted_price(0, 20), 0)
        self.assertEqual(calculate_discounted_price(100, 0), 100)
        self.assertEqual(calculate_discounted_price(100, 100), 0)
        
        # Test with invalid inputs
        with self.assertRaises(ValueError):
            calculate_discounted_price(-100, 20)
        with self.assertRaises(ValueError):
            calculate_discounted_price(100, -20)
        with self.assertRaises(ValueError):
            calculate_discounted_price(100, 120)

    def test_validate_price_input(self):
        # Test valid inputs
        self.assertTrue(validate_price_input(100))
        self.assertTrue(validate_price_input(0))
        self.assertTrue(validate_price_input(9999.99))
        
        # Test invalid inputs
        self.assertFalse(validate_price_input(-100))
        self.assertFalse(validate_price_input("100"))
        self.assertFalse(validate_price_input(None))
        self.assertFalse(validate_price_input(100000))  # Assuming max price limit is 9999.99

    @patch('src.helpers.external_price_api')
    def test_generate_price_suggestions(self, mock_external_price_api):
        # Mock realistic large dataset
        mock_external_price_api.return_value = [
            {"price": 95.0, "confidence": 0.9},
            {"price": 90.0, "confidence": 0.85},
            {"price": 85.0, "confidence": 0.8},
        ]
        
        # Test with valid input
        suggestions = generate_price_suggestions(100)
        self.assertEqual(len(suggestions), 3)
        self.assertEqual(suggestions[0]["price"], 95.0)
        self.assertEqual(suggestions[0]["confidence"], 0.9)
        
        # Test with edge case input
        suggestions = generate_price_suggestions(0)
        self.assertEqual(len(suggestions), 3)
        self.assertTrue(all(s["price"] < 1 for s in suggestions))
        
        # Test with invalid input
        with self.assertRaises(ValueError):
            generate_price_suggestions(-100)

if __name__ == '__main__':
    unittest.main()