# -*- coding: utf-8 -*-

"""
This module contains the logic for fetching cryptocurrency data from CoinGecko,
checking its tradability on Binance, and saving it to a JSON file.
"""

import json
import os
from datetime import datetime, timezone
from ratelimit import limits
from pycoingecko import CoinGeckoAPI
from binance.client import Client

# Shared state for tracking progress of the update
update_progress = {
    "status": "idle",  # Can be: idle, running, complete, error
    "stage": "",       # e.g., "Fetching Binance symbols", "Fetching CoinGecko page"
    "current": 0,      # Current item being processed
    "total": 0,        # Total items to process
    "error_message": None
}

def get_binance_client():
    """Initialise and return the Binance API client."""
    api_key = os.environ.get('BINANCE_API_KEY')
    api_secret = os.environ.get('BINANCE_API_SECRET')
    return Client(api_key, api_secret)

def get_binance_tradable_symbols(client):
    """
    Fetch the set of all tradable symbols from Binance.
    In case of an error (e.g., geo-blocking), it returns a mocked set of common pairs.
    """
    print("Fetching tradable pairs from Binance...")
    try:
        exchange_info = client.get_exchange_info()
        symbols = {s['symbol'] for s in exchange_info['symbols']}
        print(f"Found {len(symbols)} tradable pairs on Binance.")
        return symbols
    except Exception as e:
        print(f"Could not fetch symbols from Binance: {e}")
        print("Falling back to a mocked list of tradable symbols for testing.")
        mock_symbols = {
            'BTCUSDC', 'ETHUSDC', 'BNBUSDC', 'SOLUSDC', 'XRPUSDC', 'ADAUSDC',
            'AVAXUSDC', 'LINKUSDC', 'DOTUSDC', 'DOGEUSDC', 'MATICUSDC', 'LTCUSDC',
            'WBTCUSDC', 'BCHUSDC', 'TRXUSDC', 'SHIBUSDC', 'UNIUSDC'
        }
        return mock_symbols

# CoinGecko's public API rate limit is around 10-30 calls per minute.
# We'll set a conservative limit of 10 calls per minute.
TEN_CALLS_PER_MINUTE = 10
ONE_MINUTE = 60

@limits(calls=TEN_CALLS_PER_MINUTE, period=ONE_MINUTE)
def get_coins_markets_with_rate_limit(cg_client, **kwargs):
    """
    A rate-limited wrapper for the PyCoinGecko get_coins_markets method.
    """
    return cg_client.get_coins_markets(**kwargs)

def get_top_3000_crypto_data():
    """Fetch market data for the top 3000 cryptocurrencies from CoinGecko."""
    global update_progress
    print("Initializing CoinGecko client...")
    try:
        cg = CoinGeckoAPI()
        all_coins = []
        total_pages = 12
        update_progress['total'] = total_pages

        # 12 pages * 250 results per page = 3000
        for i in range(1, total_pages + 1):
            update_progress['stage'] = f"Fetching CoinGecko page {i}/{total_pages}"
            update_progress['current'] = i
            print(f"Fetching page {i}/{total_pages} of crypto data (coins {(i-1)*250+1}-{i*250})...")
            coins_page = get_coins_markets_with_rate_limit(
                cg, vs_currency='usd', order='market_cap_desc', per_page=250, page=i
            )
            if not coins_page:
                print(f"No more data from CoinGecko on page {i}. Stopping.")
                break
            all_coins.extend(coins_page)

        print(f"Total of {len(all_coins)} cryptocurrencies fetched from CoinGecko.")
        return all_coins
    except Exception as e:
        print(f"An error occurred while communicating with the CoinGecko API: {e}")
        update_progress['status'] = 'error'
        update_progress['error_message'] = str(e)
        return None

def process_and_save_data(coins_data, binance_symbols, filename="top_3000_cryptos_tradability.json"):
    """Process crypto data and save the result to a JSON file."""
    global update_progress
    if not coins_data:
        print("No data from CoinGecko to process.")
        return

    project_root = os.path.dirname(os.path.dirname(__file__))
    output_path = os.path.join(project_root, filename)

    print("Processing data: checking tradability on Binance vs USDC...")
    processed_data = []
    total_coins = len(coins_data)
    update_progress['stage'] = "Processing and saving data"
    update_progress['total'] = total_coins

    for i, coin in enumerate(coins_data):
        update_progress['current'] = i + 1
        symbol = coin.get('symbol', '').upper()
        name = coin.get('name')
        coin_id = coin.get('id')

        if not symbol or not name or not coin_id:
            continue

        is_tradable = f"{symbol}USDC" in binance_symbols
        coin_details = {'id': coin_id, 'name': name, 'symbol': symbol, 'is_tradable_on_binance_vs_usdc': is_tradable}
        processed_data.append(coin_details)

    data_to_save = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'count': len(processed_data),
        'coins': processed_data
    }

    print(f"Saving data to '{output_path}'...")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        print(f"Data has been successfully saved to '{output_path}'.")
    except IOError as e:
        print(f"Error writing to file '{output_path}': {e}")
        update_progress['status'] = 'error'
        update_progress['error_message'] = str(e)

def run_update():
    """Main function to orchestrate the data update process."""
    global update_progress
    update_progress['status'] = 'running'
    update_progress['error_message'] = None
    update_progress['current'] = 0
    update_progress['total'] = 0

    binance_symbols = set()
    try:
        update_progress['stage'] = "Fetching Binance symbols"
        print("Initializing Binance client...")
        binance_client = get_binance_client()
        binance_symbols = get_binance_tradable_symbols(binance_client)
        print("Binance symbol fetch complete.")
    except Exception as e:
        print(f"\nA Binance-related error occurred: {e}")
        print("Continuing with a mocked list of Binance symbols.")
        binance_symbols = {
            'BTCUSDC', 'ETHUSDC', 'BNBUSDC', 'SOLUSDC', 'XRPUSDC', 'ADAUSDC',
            'AVAXUSDC', 'LINKUSDC', 'DOTUSDC', 'DOGEUSDC', 'MATICUSDC', 'LTCUSDC',
            'WBTCUSDC', 'BCHUSDC', 'TRXUSDC', 'SHIBUSDC', 'UNIUSDC'
        }

    try:
        top_3000_data = get_top_3000_crypto_data()
        if top_3000_data:
            process_and_save_data(top_3000_data, binance_symbols)
            if update_progress['status'] != 'error':
                update_progress['status'] = 'complete'
                update_progress['stage'] = 'Done'
        else:
            print("Script finished early as no data could be fetched from CoinGecko.")
            if update_progress['status'] != 'error':
                 update_progress['status'] = 'complete'
                 update_progress['stage'] = 'No data fetched'

    except Exception as e:
        print(f"\nAn unexpected critical error occurred: {e}")
        update_progress['status'] = 'error'
        update_progress['error_message'] = str(e)