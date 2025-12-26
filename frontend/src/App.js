import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [lots, setLots] = useState([]);
  const [selectedLot, setSelectedLot] = useState(null);
  const [spots, setSpots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

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

  const fetchSpots = async (lotId) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/spots/?parking_lot=${lotId}`);
      if (!response.ok) throw new Error('Failed to fetch spots');
      const data = await response.json();
      setSpots(data);
    } catch (err) {
      console.error('Error fetching spots:', err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedLot) {
      fetchSpots(selectedLot.id);
      const interval = setInterval(() => fetchSpots(selectedLot.id), 3000);
      return () => clearInterval(interval);
    }
  }, [selectedLot]);

  const filteredLots = lots.filter(lot => {
    if (filter === 'available') return lot.available_spots > 0;
    if (filter === 'full') return lot.available_spots === 0;
    return true;
  });

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="app">
      <header className="header">
        <h1>🅿️ VT Smart Parking</h1>
        <p>Real-time parking availability</p>
      </header>

      <div className="filters">
        <button className={filter === 'all' ? 'active' : ''} onClick={() => setFilter('all')}>
          All Lots
        </button>
        <button className={filter === 'available' ? 'active' : ''} onClick={() => setFilter('available')}>
          Has Space
        </button>
        <button className={filter === 'full' ? 'active' : ''} onClick={() => setFilter('full')}>
          Full
        </button>
      </div>

      <div className="dashboard">
        {filteredLots.map((lot) => (
          <div 
            key={lot.id} 
            className={`lot-card ${selectedLot?.id === lot.id ? 'selected' : ''}`}
            onClick={() => setSelectedLot(selectedLot?.id === lot.id ? null : lot)}
          >
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

      {selectedLot && (
        <div className="spot-detail">
          <h2>{selectedLot.name} - Individual Spots</h2>
          <div className="spots-grid">
            {spots.map((spot) => (
              <div 
                key={spot.parking_spot_id} 
                className={`spot ${spot.availability ? 'free' : 'taken'}`}
              >
                {spot.parking_spot_id}
              </div>
            ))}
          </div>
          <div className="legend">
            <span><span className="dot free"></span> Available</span>
            <span><span className="dot taken"></span> Occupied</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;