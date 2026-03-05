from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import ml_model
from config import UPLOAD_DIR
from database import get_conn
from routes import detect, reports, geocode, whatsapp

app = FastAPI(title="GarbageGang API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.include_router(detect.router)
app.include_router(reports.router)
app.include_router(geocode.router)
app.include_router(whatsapp.router)


@app.on_event("startup")
def on_startup() -> None:
    ml_model.load_model()


@app.get("/health")
def health():
    db_ok = False
    try:
        conn = get_conn()
        conn.close()
        db_ok = True
    except Exception:
        pass
    return {
        "model_loaded": ml_model.model is not None,
        "model_path":   "models/best.pt",
        "db":           "ok" if db_ok else "error",
    }
