# backend-ml/config.py
# Single source of truth for environment variables and directory paths.
# Every other module imports from here instead of calling os.getenv() directly.

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # reads .env when running locally; no-op on Render (env vars already set)

# ── Directories ────────────────────────────────────────────────────────────
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ── Twilio ─────────────────────────────────────────────────────────────────
TWILIO_SID   = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
MAP_URL      = os.getenv("MAP_URL", "http://localhost:3000/map")

# ── Supabase Storage ───────────────────────────────────────────────────────
# Set SUPABASE_URL + SUPABASE_KEY in .env to enable cloud image storage.
# If not set, images fall back to local disk under UPLOAD_DIR.
SUPABASE_URL    = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY    = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET = "report-images"
