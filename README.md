# GarbageGang 🗑️

Community-driven garbage mapping platform for cleaner neighborhoods. Upload images of garbage with live location to create heatmaps for cleanup planning.

## 🌟 Features

- **📷 Image Upload with Geolocation**: Upload garbage images with automatic location capture
- **🗺️ Interactive Heatmap**: Visualize garbage concentration across your city
- **📊 Dataset Dashboard**: View all submitted reports with images and coordinates
- **🌱 Green Theme**: Eco-friendly design with smooth animations

## 🏗️ Project Structure

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

## 🚀 Quick Start

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
cd backend
npm run dev
```

Backend will run on `http://localhost:4000`

#### 3. Start the Frontend (in a new terminal)

```bash
npm start
```

Frontend will run on `http://localhost:3000`

## 📱 Usage

1. **Navigate to Local Map** page
2. Click **"Report Garbage"** button
3. Choose an image from your device
4. Click **"Upload with Live Location"**
5. Allow location access when prompted
6. View your report on the map and in the Dataset tab

## 🛠️ Tech Stack

### Backend
- **Express.js** - Web framework
- **Better-SQLite3** - Fast, embedded database
- **Multer** - File upload handling
- **CORS** - Cross-origin resource sharing

### Frontend
- **React** - UI framework
- **TypeScript** - Type safety
- **React Router** - Navigation
- **Leaflet** - Interactive maps
- **Leaflet.heat** - Heatmap visualization

## 📊 API Endpoints

### `POST /api/report`
Upload a new garbage report with image and location.

**Request:**
- Form-data with `image` (file), `lat` (number), `lng` (number)

**Response:**
```json
{
  "id": 1,
  "filename": "garbage-1234567890.jpg",
  "lat": 12.9716,
  "lng": 77.5946,
  "message": "Report submitted successfully"
}
```

### `GET /api/reports`
Fetch all garbage reports.

**Response:**
```json
[
  {
    "id": 1,
    "filename": "garbage-1234567890.jpg",
    "url": "http://localhost:4000/uploads/garbage-1234567890.jpg",
    "lat": 12.9716,
    "lng": 77.5946,
    "created_at": "2026-02-07T10:30:00.000Z"
  }
]
```

### `GET /api/reports/:id`
Fetch a specific report by ID.

## 🎨 Color Palette

- Primary Green: `#2e8b57`
- Dark Green: `#1a5a36`
- Light Green: `#e8f8ef`
- Background: `#f0fff4`

## 🔮 Future Enhancements

- [ ] User authentication and profiles
- [ ] Admin dashboard for cleanup coordination
- [ ] Email notifications for nearby reports
- [ ] Mobile app (React Native)
- [ ] ML-based garbage classification
- [ ] Community cleanup event scheduling
- [ ] Gamification with leaderboards

## 📝 License

MIT License - feel free to use this for your community!

## 🤝 Contributing

Contributions welcome! Open issues or submit PRs.

---

**Made with 💚 for cleaner neighborhoods**
