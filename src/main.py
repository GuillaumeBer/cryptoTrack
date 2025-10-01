import os
import sys
import asyncio
import json
from functools import lru_cache
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional

import threading
import uvicorn
import httpx
from src.binance_client import get_price_from_binance
from src.coingecko_client import get_price_from_coingecko
from src.data_updater import run_update, update_progress

# On Windows, the default asyncio event loop (ProactorEventLoop) can cause
# ConnectionResetError. This is a known issue with libraries like aiohttp/uvicorn.
# Switching to SelectorEventLoop, which is the default on other platforms,
# resolves this issue by handling client disconnects more gracefully.
if sys.platform == "win32":
    print("Applying WindowsSelectorEventLoopPolicy to prevent ConnectionResetError on Windows.")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()

# Configuration CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@lru_cache(maxsize=1)
def load_crypto_data() -> List[Dict[str, Any]]:
    """
    Charge les données des cryptomonnaies depuis le fichier JSON.
    La mise en cache avec lru_cache évite de lire le fichier à chaque appel.
    """
    try:
        # Build an absolute path to the JSON file, relative to this script's location.
        # This makes the data loading independent of the current working directory.
        script_dir = os.path.dirname(__file__)  # The directory this script is in (src/)
        project_root = os.path.dirname(script_dir) # The parent directory (project root)
        json_path = os.path.join(project_root, 'top_3000_cryptos_tradability.json')

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        coins = data.get('coins', [])
        if not coins:
            raise HTTPException(status_code=404, detail="Aucune cryptomonnaie trouvée dans le fichier de données.")
        return coins

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Le fichier de données 'top_3000_cryptos_tradability.json' est introuvable.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur de décodage du fichier JSON. Le fichier est peut-être corrompu.")

@app.get("/api/pairs", response_model=List[Dict[str, Any]])
async def read_pairs(search: Optional[str] = Query(None, min_length=1)):
    """
    Retourne une liste de cryptomonnaies depuis le fichier JSON.
    Si un paramètre 'search' est fourni, filtre les cryptos dont le nom ou le symbole commence par la recherche.
    """
    all_coins = load_crypto_data()

    if not search:
        return all_coins

    search_lower = search.lower()
    filtered_coins = [
        coin for coin in all_coins
        if coin['name'].lower().startswith(search_lower) or coin['symbol'].lower().startswith(search_lower)
    ]

    return filtered_coins

@app.on_event("startup")
async def startup_event():
    """
    Vérifie l'existence du fichier de données au démarrage.
    S'il n'existe pas, lance une mise à jour initiale en arrière-plan.
    """
    script_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(script_dir)
    json_path = os.path.join(project_root, 'top_3000_cryptos_tradability.json')

    if not os.path.exists(json_path):
        print("Le fichier de données n'existe pas. Lancement de la mise à jour initiale en arrière-plan.")
        thread = threading.Thread(target=run_update)
        thread.start()

@app.post("/api/refresh-data")
async def refresh_data():
    """
    Déclenche le processus de mise à jour du fichier de données JSON en arrière-plan.
    """
    if update_progress['status'] == 'running':
        raise HTTPException(status_code=409, detail="Un rafraîchissement est déjà en cours.")

    try:
        print("Début de la mise à jour des données en arrière-plan via l'API...")

        # Lancer `run_update` dans un thread séparé
        thread = threading.Thread(target=run_update)
        thread.start()

        # Vider le cache pour que les prochaines requêtes attendent potentiellement les nouvelles données
        load_crypto_data.cache_clear()

        return {"message": "Le rafraîchissement des données a été lancé en arrière-plan."}
    except Exception as e:
        print(f"Erreur lors du lancement du rafraîchissement des données : {e}")
        raise HTTPException(status_code=500, detail="Une erreur interne est survenue lors du lancement du rafraîchissement.")

@app.get("/api/refresh-status")
async def get_refresh_status():
    """
    Retourne le statut actuel du processus de rafraîchissement des données.
    """
    return update_progress

@app.get("/api/price")
async def get_price(symbol: str, coin_id: str, is_tradable: bool):
    """
    Asynchronously retrieves the price of a cryptocurrency.
    It first tries Binance if the coin is marked as tradable,
    and falls back to CoinGecko if the Binance lookup fails or is not applicable.
    """
    price = None
    source = None
    binance_symbol = f"{symbol.upper()}USDC"

    # Log the initial attempt
    print(f"Fetching price for {symbol} (CoinID: {coin_id}, Tradable: {is_tradable})")

    if is_tradable:
        print(f"Attempting to fetch price from Binance for {binance_symbol}...")
        price = await get_price_from_binance(binance_symbol)
        if price is not None:
            source = "Binance"
            print(f"Successfully fetched price from Binance: {price}")
        else:
            print(f"Failed to fetch price from Binance for {binance_symbol}. Falling back to CoinGecko.")

    if price is None:
        # This block runs if the coin is not tradable on Binance or if the Binance API call failed.
        print(f"Attempting to fetch price from CoinGecko for coin_id: {coin_id}...")
        price = await get_price_from_coingecko(coin_id)
        if price is not None:
            # If the initial source was None, it means we came directly here.
            # Otherwise, it was a fallback.
            source = "CoinGecko" if source is None else "Binance (fallback CoinGecko)"
            print(f"Successfully fetched price from CoinGecko: {price}")
        else:
            print(f"Failed to fetch price from CoinGecko for coin_id: {coin_id}.")

    if price is None:
        # After trying all sources, if price is still None, raise an error.
        error_message = f"Could not retrieve price for {symbol} from any available source."
        print(error_message)
        raise HTTPException(status_code=404, detail=error_message)

    return {"symbol": symbol, "price": price, "source": source}


@app.get("/api/jupiter-lend-positions/{wallet_address}")
async def get_jupiter_lend_positions(wallet_address: str):
    """
    Récupère les positions d'emprunt d'un portefeuille sur Jupiter Lend.
    """
    url = f"https://lite-api.jup.ag/lend/v1/positions/{wallet_address}"
    # Utilisation de données de démonstration si l'adresse est "DEMO"
    if wallet_address.upper() == "DEMO":
        return [
            {
                "collateral": "SOL",
                "collateralValue": 1500.50,
                "borrowed": "USDC",
                "borrowValue": 750.25,
                "ratio": 50.00,
                "healthFactor": 1.7,
                "riskLevel": "safe"
            },
            {
                "collateral": "JitoSOL",
                "collateralValue": 2500.00,
                "borrowed": "USDT",
                "borrowValue": 1800.00,
                "ratio": 72.00,
                "healthFactor": 1.2,
                "riskLevel": "risky"
            }
        ]

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()  # Lève une exception pour les statuts 4xx/5xx

            data = response.json()
            # L'API peut retourner un objet vide {} si aucune position n'est trouvée.
            if not data or not isinstance(data, list):
                 return []
            return data

        except httpx.HTTPStatusError as e:
            # Gérer les erreurs HTTP spécifiques (ex: 404, 500)
            raise HTTPException(status_code=e.response.status_code, detail=f"Erreur de l'API Jupiter Lend: {e.response.text}")
        except httpx.RequestError as e:
            # Gérer les erreurs de connexion (ex: timeout, DNS)
            raise HTTPException(status_code=503, detail=f"Impossible de contacter l'API Jupiter Lend: {e}")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Réponse invalide de l'API Jupiter Lend (format JSON attendu).")

if __name__ == "__main__":
    # This block allows the script to be run directly with `python src/main.py`
    # It ensures the Windows-specific asyncio policy is applied before the server starts.
    print("Starting server programmatically...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
