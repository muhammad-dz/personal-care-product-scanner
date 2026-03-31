import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import ScannerPage from './pages/ScannerPage';
import SentimentDashboard from './pages/SentimentDashboard';

function App() {
  return (
    <Router>
      <div>
        <div style={{ borderBottom: '1px solid #ccc', padding: '12px 20px', background: '#f5f5f5' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', maxWidth: '1200px', margin: '0 auto' }}>
            <h2 style={{ margin: 0, fontSize: '1.2rem' }}>Personal Care Product Safety Scanner</h2>
            <div>
              <Link to="/" style={{ marginRight: '20px', color: '#333', textDecoration: 'none' }}>Scanner</Link>
              <Link to="/sentiment" style={{ color: '#333', textDecoration: 'none' }}>Sentiment</Link>
            </div>
          </div>
        </div>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <Routes>
            <Route path="/" element={<ScannerPage />} />
            <Route path="/sentiment" element={<SentimentDashboard />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;