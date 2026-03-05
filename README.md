# GarbageGang

Community-driven waste mapping platform for Bengaluru. Send a photo of illegal dumping via WhatsApp — a YOLOv11 model detects the trash, and confirmed reports appear as live markers on an interactive Leaflet map.

## Features

- **WhatsApp reporting** — photo → YOLO detection → location → saved to Supabase
- **Live map** — clustered emoji markers, heatmap overlay, 369 GBA ward boundaries
- **Auto-geocoding** — typed addresses resolved via Nominatim (no API key needed)
- **Supabase backend** — images stored in Supabase Storage, reports in PostgreSQL

## Project Structure

```
garbagegang/
├── backend-ml/                  # Python FastAPI backend
│   ├── main.py                  # App entry point, /health endpoint
│   ├── config.py                # Env vars (Twilio, Supabase, upload dir)
│   ├── database.py              # psycopg2 connection + db_conn() context manager
│   ├── ml_model.py              # YOLOv11 singleton, load_model()
│   ├── storage.py               # Supabase image upload, local disk fallback
│   ├── requirements.txt
│   ├── .env                     # Local secrets — never commit
│   ├── models/
│   │   └── best.pt              # Trained YOLOv11 model
│   ├── uploads/                 # Local image fallback (auto-created)
│   └── routes/
│       ├── detect.py            # POST /detect — stateless YOLO inference
│       ├── reports.py           # POST /reports, GET /reports
│       ├── geocode.py           # GET /geocode — Nominatim proxy
│       └── whatsapp.py          # POST /whatsapp — Twilio webhook
│
├── src/                         # React + TypeScript frontend
│   ├── App.tsx                  # Router shell, cold-start ping
│   ├── config.ts                # API_BASE URL (single source of truth)
│   ├── components/
│   │   ├── Navbar.tsx
│   │   └── Footer.tsx
│   └── pages/
│       ├── Home.tsx             # Hero + CTA
│       ├── MapPage.tsx          # Live Leaflet map, polls /reports every 30s
│       ├── About.tsx
│       └── Dataset.tsx
│
├── public/
│   ├── index.html
│   └── wards.geojson            # 369 GBA ward boundaries for map overlay
│
├── notebooks/                   # Colab training notebooks
├── dataset/                     # Not committed (see .gitignore)
├── package.json
└── tsconfig.json
```

## Running Locally

### Prerequisites
- Python 3.10+ with a virtual environment
- Node.js 18+
- `best.pt` placed at `backend-ml/models/best.pt`
- `backend-ml/.env` filled with Supabase + Twilio credentials

### 1. Start the backend

```bash
cd backend-ml
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`

### 2. Start ngrok (for WhatsApp webhook)

```bash
ngrok http 8000
```

Paste the `https://` URL into the Twilio sandbox webhook field as `https://xxxx.ngrok.io/whatsapp`

### 3. Start the frontend

```bash
npm start
```

Frontend runs at `http://localhost:3000`
