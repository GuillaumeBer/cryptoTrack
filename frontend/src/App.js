import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [search, setSearch] = useState('');
  const [pairs, setPairs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (search.length === 0) {
      setPairs([]);
      return;
    }

    const fetchPairs = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://localhost:8000/api/pairs?search=${search}`);
        const data = await response.json();
        setPairs(data);
      } catch (error) {
        console.error("Erreur lors de la récupération des paires:", error);
        setPairs([]);
      }
      setLoading(false);
    };

    const debounceFetch = setTimeout(() => {
      fetchPairs();
    }, 300);

    return () => clearTimeout(debounceFetch);
  }, [search]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Chercher une Paire de Trading USDC</h1>
        <div className="search-container">
          <input
            type="text"
            placeholder="Commencez à taper (ex: BTC)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
          {loading && <div className="loader"></div>}
          {pairs.length > 0 && (
            <ul className="suggestions-list">
              {pairs.map((pair) => (
                <li key={pair}>{pair}</li>
              ))}
            </ul>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;