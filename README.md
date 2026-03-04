# GarbageGang (LOCAL ONLY FOR NOW)

Community-driven garbage mapping platform for cleaner neighborhoods. Upload images of garbage with live location to create heatmaps for cleanup planning.

## Proposed Features

- **Image Upload with Geolocation**: Upload garbage images with automatic location capture
- **Interactive Heatmap**: Visualize garbage concentration across your city
- **Dataset Dashboard**: View all submitted reports with images and coordinates

## Project Structure

```
garbagegang/
├── backend/              # Node.js + Express API
│   ├── server.js        # Express server with file uploads
│   ├── db.js            # SQLite database setup
│   ├── uploads/         # Uploaded images storage
│   └── data.sqlite      # SQLite database file
├── src/                 # React frontend
│   ├── components/      # React components
│   │   ├── Navbar.tsx
│   │   ├── Footer.tsx
│   │   └── ReportForm.tsx
│   └── pages/           # Page components
│       ├── Home.tsx
│       ├── MapPage.tsx  # Interactive map with heatmap
│       ├── Dataset.tsx  # Reports gallery
│       └── About.tsx
└── public/
```


### Prerequisites
- Node.js (v14 or higher)
- npm

### Installation & Running

#### 1. Install Dependencies

**Backend:**
```bash
cd backend
npm install 
```

**Frontend:**
```bash
npm install
```

#### 2. Start the Backend Server

```bash
uvicorn main:app --reload --port 8000
ngrok http 8000 
```

Backend will run on `http://localhost:8000`

#### 3. Start the Frontend (in a new terminal)

```bash
npm start
```

Frontend will run on `http://localhost:3000`
