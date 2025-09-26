from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from src.binance_client import get_tradable_usdc_pairs

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

@app.get("/api/pairs", response_model=List[str])
async def read_pairs(search: Optional[str] = None):
    """
    Retourne une liste de paires USDC tradables.
    Si un paramètre 'search' est fourni, filtre les paires qui commencent par la chaîne de recherche.
    """
    try:
        pairs = get_tradable_usdc_pairs()
        if not pairs:
            raise HTTPException(status_code=404, detail="Aucune paire trouvée ou erreur lors de la récupération.")

        if search:
            return [pair for pair in pairs if pair.startswith(search.upper())]

        return pairs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))