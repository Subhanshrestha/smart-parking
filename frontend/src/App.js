import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [lots, setLots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/dashboard/');
      if (!response.ok) throw new Error('Failed to fetch');
      const data = await response.json();
      setLots(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000); // Poll every 3 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="app">
      <header className="header">
        <h1>🅿️ VT Smart Parking</h1>
        <p>Real-time parking availability</p>
      </header>

      <div className="dashboard">
        {lots.map((lot) => (
          <div key={lot.id} className="lot-card">
            <h2>{lot.name}</h2>
            <div className="stats">
              <div className="stat available">
                <span className="number">{lot.available_spots}</span>
                <span className="label">Available</span>
              </div>
              <div className="stat total">
                <span className="number">{lot.total_spots}</span>
                <span className="label">Total</span>
              </div>
            </div>
            <div className="occupancy-bar">
              <div 
                className="occupancy-fill"
                style={{ 
                  width: `${lot.occupancy_percent}%`,
                  backgroundColor: lot.occupancy_percent > 80 ? '#e74c3c' : 
                                   lot.occupancy_percent > 50 ? '#f39c12' : '#2ecc71'
                }}
              />
            </div>
            <p className="occupancy-text">{lot.occupancy_percent}% occupied</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;