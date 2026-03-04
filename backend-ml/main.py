# backend-ml/main.py
# Entry point — kept intentionally thin.
# Business logic lives in: routes/, storage.py, ml_model.py, config.py, database.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import ml_model
from config import UPLOAD_DIR
from routes import detect, reports, geocode, whatsapp

app = FastAPI(title="GarbageGang API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to your Vercel URL in production
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
