from binance.client import Client

def get_all_binance_symbols():
    """
    Récupère la liste de tous les symboles de trading disponibles sur Binance Spot.
    """
    # Initialiser le client. Pas besoin de clé API pour les points de terminaison publics.
    client = Client()

    try:
        # Appeler le point de terminaison exchange_info pour obtenir les détails
        exchange_info = client.get_exchange_info()

        # Extraire la liste des symboles du dictionnaire de réponse
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
    client = Client()

    try:
        exchange_info = client.get_exchange_info()

        usdc_symbols = []
        for s in exchange_info['symbols']:
            # On filtre pour ne garder que les paires contre USDC et qui sont tradables
            if s['quoteAsset'] == 'USDC' and s['status'] == 'TRADING':
                usdc_symbols.append(s['symbol'])

        return usdc_symbols

    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        return None