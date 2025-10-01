import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
import httpx

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.binance_client import get_price_from_binance
from src.coingecko_client import get_price_from_coingecko

class TestClients(unittest.IsolatedAsyncioTestCase):

    # --- Tests for Binance Client ---

    @patch('httpx.AsyncClient')
    async def test_get_price_from_binance_success(self, MockAsyncClient):
        """Test successful price retrieval from Binance."""
        # Mock the response from httpx
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'symbol': 'BTCUSDC', 'price': '67000.00'}

        # Configure the mock async client context manager
        mock_async_client = MockAsyncClient.return_value
        mock_async_client.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        # Call the function
        price = await get_price_from_binance('BTCUSDC')

        # Assert the result
        self.assertEqual(price, 67000.00)

    @patch('httpx.AsyncClient')
    async def test_get_price_from_binance_http_error(self, MockAsyncClient):
        """Test handling of HTTP errors from Binance."""
        # Mock an HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Symbol not found"

        mock_async_client = MockAsyncClient.return_value
        mock_async_client.__aenter__.return_value.get.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=mock_response
        )

        price = await get_price_from_binance('NONEXISTENT')
        self.assertIsNone(price)

    @patch('httpx.AsyncClient')
    async def test_get_price_from_binance_request_error(self, MockAsyncClient):
        """Test handling of network request errors from Binance."""
        mock_async_client = MockAsyncClient.return_value
        mock_async_client.__aenter__.return_value.get.side_effect = httpx.RequestError("Connection failed")

        price = await get_price_from_binance('BTCUSDC')
        self.assertIsNone(price)

    # --- Tests for CoinGecko Client ---

    @patch('httpx.AsyncClient')
    async def test_get_price_from_coingecko_success(self, MockAsyncClient):
        """Test successful price retrieval from CoinGecko."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'bitcoin': {'usd': 67000.00}}

        mock_async_client = MockAsyncClient.return_value
        mock_async_client.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        price = await get_price_from_coingecko('bitcoin')
        self.assertEqual(price, 67000.00)

    @patch('httpx.AsyncClient')
    async def test_get_price_from_coingecko_http_error(self, MockAsyncClient):
        """Test handling of HTTP errors from CoinGecko."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_async_client = MockAsyncClient.return_value
        mock_async_client.__aenter__.return_value.get.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=mock_response
        )

        price = await get_price_from_coingecko('nonexistent-coin')
        self.assertIsNone(price)

    @patch('httpx.AsyncClient')
    async def test_get_price_from_coingecko_invalid_response(self, MockAsyncClient):
        """Test handling of invalid JSON response from CoinGecko."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'bitcoin': {'eur': 62000.00}} # 'usd' key is missing

        mock_async_client = MockAsyncClient.return_value
        mock_async_client.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        price = await get_price_from_coingecko('bitcoin')
        self.assertIsNone(price)

if __name__ == '__main__':
    unittest.main()