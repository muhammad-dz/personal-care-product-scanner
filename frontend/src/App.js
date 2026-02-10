import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ScannerPage from './pages/ScannerPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header style={{ background: '#282c34', color: 'white', padding: '20px' }}>
          <h1>🧴 Cosmetic Safety Scanner</h1>
        </header>
        
        <main style={{ padding: '20px' }}>
          <Routes>
            <Route path="/" element={<ScannerPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
