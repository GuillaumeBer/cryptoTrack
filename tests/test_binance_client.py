import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.binance_client import get_tradable_usdc_pairs

class TestBinanceClient(unittest.TestCase):

    @patch('src.binance_client.Client')
    def test_get_tradable_usdc_pairs(self, MockClient):
        """
        Test that get_tradable_usdc_pairs correctly filters symbols.
        """
        # Mock the exchange_info response
        mock_exchange_info = {
            'symbols': [
                {'symbol': 'BTCUSDC', 'quoteAsset': 'USDC', 'status': 'TRADING'},
                {'symbol': 'ETHUSDC', 'quoteAsset': 'USDC', 'status': 'TRADING'},
                {'symbol': 'BNBUSDT', 'quoteAsset': 'USDT', 'status': 'TRADING'},  # Should be filtered out
                {'symbol': 'SOLUSDC', 'quoteAsset': 'USDC', 'status': 'BREAK'},    # Should be filtered out
                {'symbol': 'ADAUSDC', 'quoteAsset': 'USDC', 'status': 'TRADING'},
            ]
        }

        # Configure the mock client instance
        mock_instance = MockClient.return_value
        mock_instance.get_exchange_info.return_value = mock_exchange_info

        # Call the function
        tradable_pairs = get_tradable_usdc_pairs()

        # Assert the result
        expected_pairs = ['BTCUSDC', 'ETHUSDC', 'ADAUSDC']
        self.assertEqual(tradable_pairs, expected_pairs)

if __name__ == '__main__':
    unittest.main()