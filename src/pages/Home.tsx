import React from 'react';

const Home: React.FC = () => {
  return (
    <>
      <section className="hero-section">
        <div className="container">
          <div className="hero-content">
            <h1 className="hero-title">
              <span className="hero-title-light">Your neighborhood deserves</span>
              <br />
              <span className="hero-title-bold">cleaner streets</span>
            </h1>
            <p className="hero-subtitle">
              Help us map illegal dumping sites and create open data for cleanup planning.
            </p>
          </div>
        </div>
      </section>

      <section className="features-section">
        <div className="container">
          <h2 className="section-title">Why this matters</h2>
          <div className="features-grid">
            <div className="feature-card">
              <h3 className="feature-title">Visibility</h3>
              <p className="feature-description">
                Maps make invisible problems visible, enabling accountability and action.
              </p>
            </div>
            <div className="feature-card">
              <h3 className="feature-title">Community Action</h3>
              <p className="feature-description">
                Open data empowers communities to organize cleanup efforts effectively.
              </p>
            </div>
            <div className="feature-card">
              <h3 className="feature-title">Data-Driven Solutions</h3>
              <p className="feature-description">
                Pattern analysis helps authorities optimize waste management resources.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="cta-section">
        <div className="container">
          <h2 className="cta-title">Ready to make a difference?</h2>
          <p className="cta-description">
            Report garbage in your area through our WhatsApp bot or view existing reports on the map.
          </p>
          <div className="cta-buttons">
            <a href="/map" className="btn-primary">View Report Map</a>
            <a href="/dataset" className="btn-secondary">Browse Dataset</a>
          </div>
        </div>
      </section>
    </>
  );
};

export default Home;
