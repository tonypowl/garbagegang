import React from 'react';

const Footer: React.FC = () => (
  <footer className="footer">
    <div className="container">
      © {new Date().getFullYear()} GarbageGang · Open data for cleaner neighborhoods.
    </div>
  </footer>
);

export default Footer;
