import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import ScannerPage from './pages/ScannerPage';
import SentimentDashboard from './pages/SentimentDashboard';
import './App.css';

function App() {
  return (
    <Router>
      <div>
        <div style={{ 
          borderBottom: '1px solid #ccc',
          padding: '10px 20px',
          background: '#f5f5f5'
        }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            maxWidth: '1000px',
            margin: '0 auto'
          }}>
            <h2 style={{ margin: 0, fontSize: '20px' }}>
              Personal Care Product Safety Scanner
            </h2>
            <div>
              <Link to="/" style={{ marginRight: '15px', color: '#000', textDecoration: 'none' }}>
                Scanner
              </Link>
              <Link to="/sentiment" style={{ color: '#000', textDecoration: 'none' }}>
                Sentiment
              </Link>
            </div>
          </div>
        </div>
        
        <div style={{ 
          padding: '20px',
          maxWidth: '1000px',
          margin: '0 auto'
        }}>
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