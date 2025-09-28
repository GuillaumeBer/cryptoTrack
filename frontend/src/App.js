import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

function App() {
  const [search, setSearch] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedCoin, setSelectedCoin] = useState(null);
  const [priceInfo, setPriceInfo] = useState(null);
  const [isPriceLoading, setIsPriceLoading] = useState(false);
  const [priceError, setPriceError] = useState(null);

  // New state for the refresh functionality
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshMessage, setRefreshMessage] = useState('');

  const debounce = (func, delay) => {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), delay);
    };
  };

  const fetchSuggestions = async (searchTerm) => {
    if (searchTerm.trim() === '') {
      setSuggestions([]);
      return;
    }
    setIsSearching(true);
    try {
      const response = await fetch(`http://localhost:8000/api/pairs?search=${searchTerm}`);
      if (!response.ok) throw new Error('Network response was not ok.');
      const data = await response.json();
      setSuggestions(data);
    } catch (error) {
      console.error("Erreur lors de la récupération des suggestions:", error);
      setSuggestions([]);
    }
    setIsSearching(false);
  };

  const debouncedFetch = useCallback(debounce(fetchSuggestions, 300), []);

  useEffect(() => {
    debouncedFetch(search);
  }, [search, debouncedFetch]);

  const handleSelectCoin = async (coin) => {
    setSearch(coin.name);
    setSelectedCoin(coin);
    setSuggestions([]);
    setPriceInfo(null);
    setPriceError(null);
    setIsPriceLoading(true);

    try {
      const { symbol, id, is_tradable_on_binance_vs_usdc } = coin;
      const response = await fetch(`http://localhost:8000/api/price?symbol=${symbol}&coin_id=${id}&is_tradable=${is_tradable_on_binance_vs_usdc}`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de la récupération du prix.');
      }
      const data = await response.json();
      setPriceInfo(data);
    } catch (error) {
      console.error("Erreur lors de la récupération du prix:", error);
      setPriceError(error.message);
    }
    setIsPriceLoading(false);
  };

  const handleSearchChange = (e) => {
    setSearch(e.target.value);
    if (selectedCoin) {
      setSelectedCoin(null);
      setPriceInfo(null);
      setPriceError(null);
    }
  };

  // Function to handle the data refresh
  const handleRefresh = async () => {
    setIsRefreshing(true);
    setRefreshMessage('Rafraîchissement des données en cours...');
    try {
      const response = await fetch('http://localhost:8000/api/refresh-data', {
        method: 'POST',
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Une erreur est survenue.');
      }
      setRefreshMessage(data.message);
      // Clear search and price info after successful refresh
      setSearch('');
      setSelectedCoin(null);
      setPriceInfo(null);
      setPriceError(null);
    } catch (error) {
      setRefreshMessage(`Erreur: ${error.message}`);
    }
    setIsRefreshing(false);
    // Hide the message after a few seconds
    setTimeout(() => setRefreshMessage(''), 5000);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Chercher une Paire de Trading USDC</h1>
        <div className="controls-container">
          <button onClick={handleRefresh} disabled={isRefreshing}>
            {isRefreshing ? 'En cours...' : 'Rafraîchir les Données'}
          </button>
          {refreshMessage && <p className="refresh-message">{refreshMessage}</p>}
        </div>
        <div className="search-container">
          <input
            type="text"
            placeholder="Commencez à taper (ex: Bitcoin)..."
            value={search}
            onChange={handleSearchChange}
            className="search-input"
          />
          {isSearching && <div className="loader"></div>}
          {suggestions.length > 0 && (
            <ul className="suggestions-list">
              {suggestions.map((coin) => (
                <li key={coin.id} onClick={() => handleSelectCoin(coin)}>
                  {coin.name} ({coin.symbol})
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="price-display">
          {isPriceLoading && <div className="loader"></div>}
          {priceError && <p className="error-message">Erreur : {priceError}</p>}
          {priceInfo && (
            <div className="price-result">
              <h2>Prix pour {selectedCoin.name} ({priceInfo.symbol})</h2>
              <p className="price">${priceInfo.price.toLocaleString()}</p>
              <p className="source">Source: {priceInfo.source}</p>
            </div>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;