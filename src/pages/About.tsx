import React from 'react';

const About: React.FC = () => {
  return (
    <section className="about-section">
      <div className="container">
        <div className="about-content">
          <h1 className="about-title">
            About <span className="underline-text">GarbageGang</span>
          </h1>
          
          <div className="about-block">
            <h2 className="about-subtitle">Our Mission</h2>
            <p className="about-text">
              GarbageGang enables communities to collaboratively map illegal dumping sites and create open datasets for cleanup planning. We believe that transparency and data-driven approaches are essential for addressing waste management challenges.
            </p>
          </div>

          <div className="about-block">
            <h2 className="about-subtitle">How It Works</h2>
            <p className="about-text">
              Community members report garbage sites through our WhatsApp integration. Each report includes a photo and location data, visualized on an interactive map. We want to partner with a certain NGO and BBMP for coordinated cleanup efforts. The collected data is openly available for researchers, policymakers, and organizers.
            </p> 
          </div>

          <div className="about-block">
            <h2 className="about-subtitle">Open Data Philosophy</h2>
            <p className="about-text">
              All data collected through GarbageGang is open and freely accessible. We use OpenStreetMap for our base maps and ensure that every report contributes to a public dataset that anyone can analyze and use to drive change.
            </p>
          </div>

          <div className="about-block">
            <h2 className="about-subtitle">Technology</h2>
            <p className="about-text">
              This platform combines modern web technologies with community engagement tools. Reports are submitted via WhatsApp for maximum accessibility, stored in a local database, and visualized using heat maps to identify problem areas requiring attention.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
