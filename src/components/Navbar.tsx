import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  return (
    <header className="navbar">
      <div className="container">
        <div className="brand" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>GarbageGang</div>
        <nav className="nav-links" role="navigation" aria-label="main navigation">
          <NavLink to="/about">About</NavLink>
          <NavLink to="/map">Report Map</NavLink>
          <NavLink to="/dataset">Dataset</NavLink>
        </nav>
      </div>
    </header>
  );
};

export default Navbar;
