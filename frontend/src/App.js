import React from 'react';
import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom';

import ScannerPage from './pages/ScannerPage';
import SentimentDashboard from './pages/SentimentDashboard';
import './App.css';

export default function App() {
  return (
    <BrowserRouter>
      <header className="header">
        <h1>Product Safety Scanner</h1>
        <nav>
          <NavLink to="/" end>Scanner</NavLink>
          <NavLink to="/reviews">Reviews</NavLink>
        </nav>
      </header>

      <main className="container">
        <Routes>
          <Route path="/" element={<ScannerPage />} />
          <Route path="/reviews" element={<SentimentDashboard />} />
        </Routes>
      </main>

      <footer className="container muted small">
        Ratings are a simple rule-based guide, not medical advice.
      </footer>
    </BrowserRouter>
  );
}
