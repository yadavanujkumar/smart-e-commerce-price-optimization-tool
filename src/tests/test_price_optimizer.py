import unittest
from unittest.mock import patch
from src.price_optimizer import PriceOptimizer

class TestPriceOptimizer(unittest.TestCase):
    def setUp(self):
        # Initialize the PriceOptimizer instance
        self.optimizer = PriceOptimizer()

    def test_optimize_price_basic(self):
        # Test basic price optimization functionality
        input_data = [
            {"product_id": 1, "current_price": 100, "demand": 50},
            {"product_id": 2, "current_price": 200, "demand": 30},
        ]
        expected_output = [
            {"product_id": 1, "optimized_price": 110},
            {"product_id": 2, "optimized_price": 220},
        ]
        result = self.optimizer.optimize_price(input_data)
        self.assertEqual(result, expected_output)

    def test_optimize_price_large_dataset(self):
        # Test with a large dataset
        input_data = [
            {"product_id": i, "current_price": 100 + i, "demand": 50 + i}
            for i in range(1, 1001)
        ]
        result = self.optimizer.optimize_price(input_data)
        self.assertEqual(len(result), 1000)
        for i, item in enumerate(result):
            self.assertEqual(item["product_id"], i + 1)
            self.assertGreater(item["optimized_price"], 100 + i)

    def test_optimize_price_edge_case_zero_demand(self):
        # Test edge case where demand is zero
        input_data = [
            {"product_id": 1, "current_price": 100, "demand": 0},
        ]
        expected_output = [
            {"product_id": 1, "optimized_price": 90},  # Assuming price drops for zero demand
        ]
        result = self.optimizer.optimize_price(input_data)
        self.assertEqual(result, expected_output)

    def test_optimize_price_edge_case_high_demand(self):
        # Test edge case where demand is extremely high
        input_data = [
            {"product_id": 1, "current_price": 100, "demand": 1000},
        ]
        expected_output = [
            {"product_id": 1, "optimized_price": 150},  # Assuming price increases for high demand
        ]
        result = self.optimizer.optimize_price(input_data)
        self.assertEqual(result, expected_output)

    @patch("src.price_optimizer.PriceOptimizer._calculate_optimized_price")
    def test_mocked_calculate_optimized_price(self, mock_calculate):
        # Test with mocked _calculate_optimized_price method
        mock_calculate.return_value = 123.45
        input_data = [
            {"product_id": 1, "current_price": 100, "demand": 50},
        ]
        expected_output = [
            {"product_id": 1, "optimized_price": 123.45},
        ]
        result = self.optimizer.optimize_price(input_data)
        self.assertEqual(result, expected_output)
        mock_calculate.assert_called_once_with(100, 50)

    def test_invalid_input(self):
        # Test invalid input data
        input_data = [
            {"product_id": 1, "current_price": "invalid", "demand": 50},
        ]
        with self.assertRaises(ValueError):
            self.optimizer.optimize_price(input_data)

    def test_empty_input(self):
        # Test empty input data
        input_data = []
        expected_output = []
        result = self.optimizer.optimize_price(input_data)
        self.assertEqual(result, expected_output)

if __name__ == "__main__":
    unittest.main()