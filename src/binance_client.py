from binance.client import Client
from typing import Optional

def get_all_binance_symbols():
    """
    Récupère la liste de tous les symboles de trading disponibles sur Binance Spot.
    """
    client = Client()
    try:
        exchange_info = client.get_exchange_info()
        all_symbols = [s['symbol'] for s in exchange_info['symbols']]
        return all_symbols
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        return None

def get_tradable_usdc_pairs():
    """
    Récupère une liste filtrée de symboles, ne gardant que les paires
    cotées en USDC et actuellement en statut 'TRADING'.
    """
    try:
        client = Client()
        exchange_info = client.get_exchange_info()
        usdc_symbols = []
        for s in exchange_info['symbols']:
            if s['quoteAsset'] == 'USDC' and s['status'] == 'TRADING':
                usdc_symbols.append(s['symbol'])
        return usdc_symbols
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        print("Retour d'une liste de paires mockées à des fins de développement.")
        return ["BTCUSDC", "ETHUSDC", "BNBUSDC", "XRPUSDC", "ADAUSDC", "SOLUSDC", "DOGEUSDC", "AVAXUSDC", "LTCUSDC", "DOTUSDC"]

def get_price_from_binance(symbol: str) -> Optional[float]:
    """
    Récupère le dernier prix pour une paire spécifique sur Binance.
    Le symbole doit être au format de l'API, ex: 'BTCUSDC'.
    """
    try:
        client = Client()
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except Exception as e:
        print(f"Impossible de récupérer le prix pour {symbol} sur Binance: {e}")
        return None