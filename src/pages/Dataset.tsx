import React, { useEffect, useState } from 'react';
import './Dataset.css';

interface Report {
  id: number;
  filename: string;
  url: string;
  lat: number;
  lng: number;
  created_at: string;
}

const Dataset: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const response = await fetch('http://localhost:4000/api/reports');
      if (!response.ok) throw new Error('Failed to fetch reports');
      const data = await response.json();
      setReports(data);
    } catch (err) {
      setError('Failed to load dataset. Make sure the backend is running.');
      console.error('Error fetching reports:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="section dataset-section">
      <div className="container">
        <h2 className="dataset-title">Garbage Reports Dataset</h2>
        <p className="dataset-description">
          Community-submitted garbage images with location data for cleanup planning
        </p>

        {loading && (
          <div className="loading-message">Loading reports...</div>
        )}

        {error && (
          <div className="error-message">{error}</div>
        )}

        {!loading && !error && reports.length === 0 && (
          <div className="empty-message">
            No reports yet. Upload your first garbage report from the map page!
          </div>
        )}

        {!loading && reports.length > 0 && (
          <>
            <div className="dataset-stats">
              <div className="stat-card">
                <span className="stat-number">{reports.length}</span>
                <span className="stat-label">Total Reports</span>
              </div>
            </div>

            <div className="dataset-grid">
              {reports.map((report) => (
                <div key={report.id} className="dataset-card">
                  <div className="card-image-wrapper">
                    <img 
                      src={report.url} 
                      alt={`Report ${report.id}`}
                      className="card-image"
                      onError={(e) => {
                        e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><rect fill="%23ddd"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%23999">No Image</text></svg>';
                      }}
                    />
                  </div>
                  <div className="card-content">
                    <div className="card-info">
                      <span className="info-label">Date</span>
                      <span className="info-text">
                        {new Date(report.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="card-info">
                      <span className="info-label">Location</span>
                      <span className="info-text">
                        {Number(report.lat).toFixed(4)}, {Number(report.lng).toFixed(4)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </section>
  );
};

export default Dataset;
