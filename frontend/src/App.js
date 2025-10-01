import React, { useState, useEffect, useCallback } from 'react';
import { Home } from 'lucide-react';
import './App.css';
import LendingPage from './LendingPage';
import LandingPage from './LandingPage';

function App() {
  const [view, setView] = useState('landing'); // 'landing', 'priceChecker', or 'lending'
  const [search, setSearch] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedCoin, setSelectedCoin] = useState(null);
  const [priceInfo, setPriceInfo] = useState(null);
  const [isPriceLoading, setIsPriceLoading] = useState(false);
  const [priceError, setPriceError] = useState(null);

  // State for the refresh functionality
  const [refreshMessage, setRefreshMessage] = useState('');
  const [refreshProgress, setRefreshProgress] = useState({ current: 0, total: 0, stage: '' });
  const [showProgressBar, setShowProgressBar] = useState(false);

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
      if (response.status === 500) {
        const errorData = await response.json();
        if (errorData.detail && errorData.detail.includes("est introuvable")) {
          console.log("Fichier de données manquant, déclenchement du rafraîchissement.");
          handleRefresh(); // Déclenche le rafraîchissement si le fichier n'est pas trouvé
        }
        throw new Error('Erreur serveur lors de la recherche.');
      }
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

  // Check for data on startup and handle connection to backend
  useEffect(() => {
    // Set an interval to poll the backend until it's available.
    const startupInterval = setInterval(async () => {
      try {
        const statusResponse = await fetch('http://localhost:8000/api/refresh-status');

        // If we get a successful response, the backend is up.
        // Stop polling.
        clearInterval(startupInterval);
        setRefreshMessage(''); // Clear the "Connecting..." message.

        const statusData = await statusResponse.json();

        if (statusData.status === 'in_progress') {
          // A refresh is already running (e.g., initial data generation).
          console.log("Un rafraîchissement est déjà en cours au démarrage, surveillance en cours.");
          startRefreshPolling();
        } else {
          // If no refresh is running, check if the data file exists.
          const pairsResponse = await fetch(`http://localhost:8000/api/pairs?search=b`);
          if (pairsResponse.status === 500) {
            const errorData = await pairsResponse.json();
            if (errorData.detail && errorData.detail.includes("est introuvable")) {
              console.log("Fichier de données manquant, déclenchement du rafraîchissement automatique.");
              handleRefresh();
            }
          }
        }
      } catch (error) {
        // This catch block runs if the fetch fails, meaning the server is likely down.
        console.log("Backend non disponible, nouvelle tentative...");
        setRefreshMessage("Connexion au serveur en cours...");
      }
    }, 2000); // Poll every 2 seconds.

    // Cleanup interval on component unmount.
    return () => clearInterval(startupInterval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSelectCoin = async (coin) => {
    setSearch('');
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

  const startRefreshPolling = () => {
    setShowProgressBar(true);
    const interval = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:8000/api/refresh-status');
        const progress = await response.json();

        setRefreshProgress({
          current: progress.current,
          total: progress.total,
          stage: progress.stage,
        });

        if (progress.status === 'complete' || progress.status === 'error') {
          clearInterval(interval);
          setShowProgressBar(false);
          setRefreshMessage(progress.status === 'complete' ? 'Rafraîchissement terminé avec succès.' : `Erreur: ${progress.error_message}`);
          setTimeout(() => setRefreshMessage(''), 5000);
        }
      } catch (error) {
        console.error("Erreur lors de la récupération du statut de rafraîchissement:", error);
        clearInterval(interval);
        setShowProgressBar(false);
        setRefreshMessage('Erreur de connexion au serveur.');
        setTimeout(() => setRefreshMessage(''), 5000);
      }
    }, 1000);
  };

  const handleRefresh = async () => {
    setRefreshMessage('Lancement du rafraîchissement...');
    try {
      const response = await fetch('http://localhost:8000/api/refresh-data', {
        method: 'POST',
      });
      const data = await response.json();

      if (!response.ok) {
        if (response.status === 409) {
          // A refresh is already in progress, this is not an error.
          // Start polling to monitor the existing refresh.
          setRefreshMessage(data.detail || 'Un rafraîchissement est déjà en cours, suivi de la progression.');
          startRefreshPolling();
        } else {
          // For other errors, throw to be caught by the catch block.
          throw new Error(data.detail || 'Une erreur est survenue.');
        }
      } else {
        // This is the success case (e.g., 200 OK)
        setRefreshMessage(data.message);
        startRefreshPolling();
      }
    } catch (error) {
      setRefreshMessage(`Erreur: ${error.message}`);
    }
  };

  const formatPrice = (price) => {
    if (price === null || typeof price === 'undefined') {
      return '';
    }
    if (price >= 0.01) {
      return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    if (price > 0 && price < 0.01) {
      const decimals = -Math.floor(Math.log10(price)) + 3;
      return price.toFixed(decimals);
    }
    return '0.00';
  };

  const renderContent = () => {
    switch (view) {
      case 'priceChecker':
        return (
          <>
            <header className="App-header">
              {view !== 'landing' && (
                <button onClick={() => setView('landing')} className="home-button" title="Go to Home">
                  <Home className="w-6 h-6" />
                </button>
              )}
              <div className="controls-container">
                <button onClick={handleRefresh} disabled={showProgressBar}>
                  {showProgressBar ? 'En cours...' : 'Rafraîchir les Données'}
                </button>
                {refreshMessage && <p className="refresh-message">{refreshMessage}</p>}
              </div>

              {showProgressBar && (
                <div className="progress-container">
                  <p>{refreshProgress.stage}</p>
                  <div className="progress-bar-background">
                    <div
                      className="progress-bar-foreground"
                      style={{ width: `${(refreshProgress.current / (refreshProgress.total || 1)) * 100}%` }}
                    ></div>
                  </div>
                  <p>{refreshProgress.total > 0 ? `${refreshProgress.current} / ${refreshProgress.total}`: ''}</p>
                </div>
              )}
            </header>
            <main className="App-content">
              <h1>Chercher une Paire de Trading USDC</h1>
              <div className="search-container">
                <input
                  type="text"
                  placeholder="Commencez à taper (ex: Bitcoin)..."
                  value={search}
                  onChange={handleSearchChange}
                  className="search-input"
                  disabled={showProgressBar}
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
                    <p className="price">${formatPrice(priceInfo.price)}</p>
                    <p className="source">Source: {priceInfo.source}</p>
                  </div>
                )}
              </div>
            </main>
          </>
        );
      case 'lending':
        return (
          <>
            {view !== 'landing' && (
                <button onClick={() => setView('landing')} className="home-button" title="Go to Home">
                  <Home className="w-6 h-6" />
                </button>
              )}
            <LendingPage />
          </>
        );
      case 'landing':
      default:
        return <LandingPage setView={setView} />;
    }
  };

  return (
    <div className="App">
      {renderContent()}
    </div>
  );
}

export default App;