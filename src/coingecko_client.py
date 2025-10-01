import httpx
from typing import Optional

async def get_price_from_coingecko(coin_id: str) -> Optional[float]:
    """
    Asynchronously fetches the latest price for a specific cryptocurrency from CoinGecko.
    Args:
        coin_id (str): The CoinGecko ID of the cryptocurrency (e.g., 'bitcoin').
    Returns:
        Optional[float]: The price in USD, or None if not found.
    """
    # Public API endpoint for simple price lookup
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"

    async with httpx.AsyncClient() as client:
        try:
            # CoinGecko has a rate limit, so a slightly longer timeout is reasonable.
            response = await client.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()

            # The response format is {'bitcoin': {'usd': 60000}}.
            # We need to access the price via the coin_id key.
            if coin_id in data and 'usd' in data[coin_id]:
                return data[coin_id]['usd']
            else:
                # This case handles a valid response that doesn't contain the expected price data.
                print(f"Price data for '{coin_id}' not found in CoinGecko response.")
                return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching {coin_id} from CoinGecko: {e.response.status_code}")
            return None
        except (httpx.RequestError, ValueError, KeyError) as e:
            # Catches network errors, JSON parsing issues, or unexpected response structure.
            print(f"Failed to get price for {coin_id} from CoinGecko: {e}")
            return None