import httpx
from typing import Optional

async def get_price_from_binance(symbol: str) -> Optional[float]:
    """
    Asynchronously fetches the latest price for a specific pair from Binance API.
    The symbol must be in the API format, e.g., 'BTCUSDC'.
    """
    # Use the public, non-authenticated ticker endpoint
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            data = response.json()
            return float(data['price'])
        except httpx.HTTPStatusError as e:
            # This handles cases where the symbol doesn't exist (404) or other API errors
            print(f"HTTP error fetching {symbol} from Binance: {e.response.status_code} - {e.response.text}")
            return None
        except (httpx.RequestError, ValueError, KeyError) as e:
            # Catches network errors, JSON parsing issues, or missing 'price' key
            print(f"Failed to get price for {symbol} from Binance: {e}")
            return None