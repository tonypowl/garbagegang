import React, { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import MapPage from './pages/MapPage';
import About from './pages/About';
import Dataset from './pages/Dataset';
import API_BASE from './config';

function App() {
  // Silent ping on load — wakes Render from cold start before user interacts
  useEffect(() => {
    fetch(`${API_BASE}/docs`).catch(() => {});
  }, []);

  return (
    <>
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/about" element={<About />} />
          <Route path="/dataset" element={<Dataset />} />
        </Routes>
      </main>
      <Footer />
    </>
  );
}

export default App;
