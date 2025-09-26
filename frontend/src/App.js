import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [search, setSearch] = useState('');
  const [allPairs, setAllPairs] = useState([]);
  const [filteredPairs, setFilteredPairs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAllPairs = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/pairs');
        const data = await response.json();
        setAllPairs(data);
      } catch (error) {
        console.error("Erreur lors de la récupération de toutes les paires:", error);
      }
      setLoading(false);
    };

    fetchAllPairs();
  }, []);

  useEffect(() => {
    if (search.length === 0) {
      setFilteredPairs([]);
    } else {
      const filtered = allPairs.filter(pair =>
        pair.toLowerCase().startsWith(search.toLowerCase())
      );
      setFilteredPairs(filtered);
    }
  }, [search, allPairs]);

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
          {filteredPairs.length > 0 && (
            <ul className="suggestions-list">
              {filteredPairs.map((pair) => (
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