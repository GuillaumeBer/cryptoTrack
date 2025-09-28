# -*- coding: utf-8 -*-

"""
Ce script récupère les données des 300 premières cryptomonnaies par capitalisation
boursière depuis l'API CoinGecko. Pour chaque crypto, il vérifie si elle est
échangeable contre de l'USDC sur Binance en se basant sur la liste des paires
de trading de Binance.

Les informations (nom, symbole, et un booléen pour la tradabilité) sont
sauvegardées dans un fichier JSON horodaté.

Prérequis :
- Python 3
- Bibliothèques : pycoingecko, python-binance
  pip install pycoingecko python-binance
"""

import json
import os
from datetime import datetime, timezone
from pycoingecko import CoinGeckoAPI
from binance.client import Client

def get_binance_client():
    """
    Initialise et retourne le client de l'API Binance.
    Utilise les clés API depuis les variables d'environnement si disponibles,
    mais elles ne sont pas requises pour les points d'accès publics.
    """
    api_key = os.environ.get('BINANCE_API_KEY')
    api_secret = os.environ.get('BINANCE_API_SECRET')
    return Client(api_key, api_secret)

def get_binance_tradable_symbols(client):
    """
    Récupère l'ensemble des symboles de paires de trading sur Binance.

    Args:
        client (binance.client.Client): Le client de l'API Binance.

    Returns:
        set: Un ensemble de tous les symboles (ex: {'BTCUSDT', 'ETHUSDC'}).
             Retourne un ensemble vide en cas d'erreur.
    """
    print("Récupération des paires de trading sur Binance...")
    try:
        exchange_info = client.get_exchange_info()
        symbols = {s['symbol'] for s in exchange_info['symbols']}
        print(f"{len(symbols)} paires de trading trouvées sur Binance.")
        return symbols
    except Exception as e:
        print(f"Erreur lors de la récupération des symboles Binance : {e}")
        # En cas d'erreur (ex: blocage géographique), le script s'arrêtera.
        # Vous pouvez modifier pour retourner un set() vide si vous préférez
        # générer un fichier JSON même en cas d'échec partiel.
        raise

def get_top_300_crypto_data():
    """
    Récupère les données de marché pour les 300 premières cryptomonnaies
    classées par capitalisation boursière depuis l'API CoinGecko.
    """
    print("Initialisation du client CoinGecko...")
    try:
        cg = CoinGeckoAPI()

        print("Récupération de la première page de résultats (1-250)...")
        coins_page1 = cg.get_coins_markets(
            vs_currency='usd',
            order='market_cap_desc',
            per_page=250,
            page=1
        )

        print("Récupération de la deuxième page de résultats (251-300)...")
        coins_page2 = cg.get_coins_markets(
            vs_currency='usd',
            order='market_cap_desc',
            per_page=50,
            page=2
        )

        all_coins = coins_page1 + coins_page2
        print(f"Total de {len(all_coins)} cryptomonnaies récupérées depuis CoinGecko.")
        return all_coins

    except Exception as e:
        print(f"Une erreur est survenue lors de la communication avec l'API CoinGecko : {e}")
        return None

def process_and_save_data(coins_data, binance_symbols, filename="top_300_cryptos_tradability.json"):
    """
    Traite les données des cryptos, vérifie la disponibilité sur Binance vs USDC,
    et sauvegarde le résultat dans un fichier JSON.

    Args:
        coins_data (list): La liste des données de cryptos depuis CoinGecko.
        binance_symbols (set): L'ensemble des paires de trading de Binance.
        filename (str): Le nom du fichier de sortie.
    """
    if not coins_data:
        print("Aucune donnée de CoinGecko à traiter.")
        return

    print("Traitement des données : vérification de la tradabilité sur Binance vs USDC...")
    processed_data = []
    for coin in coins_data:
        symbol = coin.get('symbol', '').upper()
        name = coin.get('name')

        if not symbol or not name:
            continue

        binance_usdc_symbol = f"{symbol}USDC"

        is_tradable = binance_usdc_symbol in binance_symbols

        coin_details = {
            'name': name,
            'symbol': symbol,
            'is_tradable_on_binance_vs_usdc': is_tradable
        }

        if is_tradable:
            print(f"  > {name} ({symbol}) est échangeable contre USDC sur Binance.")
        else:
            print(f"  > {name} ({symbol}) n'est PAS échangeable contre USDC sur Binance.")

        processed_data.append(coin_details)

    data_to_save = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'count': len(processed_data),
        'coins': processed_data
    }

    print(f"Sauvegarde des données de tradabilité dans le fichier '{filename}'...")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        print(f"Les données ont été sauvegardées avec succès dans '{filename}'.")
    except IOError as e:
        print(f"Erreur lors de l'écriture dans le fichier '{filename}': {e}")

if __name__ == "__main__":
    try:
        # Étape 1: Initialiser le client Binance
        binance_client = get_binance_client()

        # Étape 2: Récupérer les données de base
        # Cette étape échouera si l'accès à l'API Binance est bloqué.
        binance_symbols = get_binance_tradable_symbols(binance_client)
        top_300_data = get_top_300_crypto_data()

        # Étape 3: Si les données sont disponibles, les traiter et les sauvegarder
        if top_300_data:
            process_and_save_data(top_300_data, binance_symbols)
        else:
            print("Le script s'est terminé car les données de CoinGecko n'ont pas pu être récupérées.")

    except Exception as e:
        print(f"\nLe script s'est arrêté en raison d'une erreur critique : {e}")
        print("Cela est probablement dû au blocage de l'API Binance. Veuillez exécuter ce script depuis un environnement non restreint.")