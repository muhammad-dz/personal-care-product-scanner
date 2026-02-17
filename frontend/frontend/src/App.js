import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import ScannerPage from './pages/ScannerPage';
import SentimentDashboard from './pages/SentimentDashboard';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header style={{ 
          background: '#2c3e50',
          color: 'white', 
          padding: '15px 20px'
        }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            maxWidth: '1200px',
            margin: '0 auto'
          }}>
            <h1 style={{ margin: 0, fontSize: '1.5rem' }}>
              Personal Care Product Safety Scanner
            </h1>
            <nav>
              <Link to="/" style={{ color: 'white', marginRight: '20px', textDecoration: 'none' }}>
                Scanner
              </Link>
              <Link to="/sentiment" style={{ color: 'white', textDecoration: 'none' }}>
                Sentiment Dashboard
              </Link>
            </nav>
          </div>
        </header>
        
        <main style={{ 
          padding: '20px',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          <Routes>
            <Route path="/" element={<ScannerPage />} />
            <Route path="/sentiment" element={<SentimentDashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;