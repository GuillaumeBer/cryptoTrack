from pycoingecko import CoinGeckoAPI
from typing import Optional, Dict, Any

def get_price_from_coingecko(coin_id: str) -> Optional[float]:
    """
    Récupère le dernier prix pour une crypto-monnaie spécifique via CoinGecko.

    Args:
        coin_id (str): L'ID de la crypto-monnaie sur CoinGecko (ex: 'bitcoin').

    Returns:
        Optional[float]: Le prix en USDC, ou None si non trouvé.
    """
    try:
        cg = CoinGeckoAPI()
        # Note: CoinGecko IDs sont généralement en minuscules, ex: "bitcoin", "ethereum"
        # Le 'id' de la liste de `get_coins_markets` est ce qu'il faut utiliser ici.
        price_data = cg.get_price(ids=coin_id, vs_currencies='usd')

        # La structure de la réponse est: {'bitcoin': {'usd': 60000}}
        if coin_id in price_data and 'usd' in price_data[coin_id]:
            return price_data[coin_id]['usd']
        else:
            return None

    except Exception as e:
        print(f"Impossible de récupérer le prix pour {coin_id} sur CoinGecko: {e}")
        return None