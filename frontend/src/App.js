import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import ScannerPage from './pages/ScannerPage';
import SentimentDashboard from './pages/SentimentDashboard';

function App() {
  return (
    <Router>
      <div>
        <div>
          <div>
            <h2>Personal Care Product Safety Scanner</h2>
            <div>
              <Link to="/">Scanner</Link>
              <Link to="/sentiment">Sentiment</Link>
            </div>
          </div>
        </div>
        
        <div>
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