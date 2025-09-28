import os
import json
from functools import lru_cache
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional

from src.binance_client import get_price_from_binance
from src.coingecko_client import get_price_from_coingecko
from src.data_updater import run_update

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
        json_path = os.path.join(project_root, 'top_500_cryptos_tradability.json')

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        coins = data.get('coins', [])
        if not coins:
            raise HTTPException(status_code=404, detail="Aucune cryptomonnaie trouvée dans le fichier de données.")
        return coins

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Le fichier de données 'top_500_cryptos_tradability.json' est introuvable.")
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

@app.post("/api/refresh-data")
async def refresh_data():
    """
    Déclenche le processus de mise à jour du fichier de données JSON
    et vide le cache pour que les nouvelles données soient chargées.
    """
    try:
        print("Début de la mise à jour des données via l'API...")
        run_update()
        # Vider le cache de la fonction pour forcer la relecture du fichier
        load_crypto_data.cache_clear()
        print("Mise à jour des données et vidage du cache terminés.")
        return {"message": "Les données ont été rafraîchies avec succès."}
    except Exception as e:
        # Log de l'erreur côté serveur pour le débogage
        print(f"Erreur lors du rafraîchissement des données : {e}")
        raise HTTPException(status_code=500, detail="Une erreur interne est survenue lors du rafraîchissement des données.")

@app.get("/api/price")
async def get_price(symbol: str, coin_id: str, is_tradable: bool):
    """
    Récupère le prix d'une cryptomonnaie, soit de Binance si elle est tradable,
    soit de CoinGecko sinon.
    """
    price = None
    source = None

    if is_tradable:
        # Le symbole pour Binance doit être au format 'BTCUSDC'
        binance_symbol = f"{symbol.upper()}USDC"
        price = get_price_from_binance(binance_symbol)
        source = "Binance"

    if price is None:
        # Si non tradable sur Binance ou si l'appel a échoué, utiliser CoinGecko
        price = get_price_from_coingecko(coin_id)
        source = "CoinGecko" if source is None else "Binance (fallback CoinGecko)"

    if price is None:
        raise HTTPException(status_code=404, detail="Impossible de récupérer le prix pour le symbole demandé.")

    return {"symbol": symbol, "price": price, "source": source}