// src/config.ts
// Single source of truth for the API base URL.
// Every file that calls the backend imports from here.

const API_BASE =
  process.env.NODE_ENV === "production"
    ? "https://your-app.onrender.com"   // ← replace after deploying to Render
    : "http://localhost:8000";

export default API_BASE;
