# backend-ml/routes/reports.py
# POST /reports        — chatbot-confirmed submission (requires YOLO model)
# POST /reports/seed   — dev/test endpoint, no model required
# GET  /reports        — fetch all reports for the map

from fastapi import APIRouter, File, UploadFile, HTTPException
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import io, json, uuid

import ml_model
from config import UPLOAD_DIR
from database import get_conn
from storage import upload_image

router = APIRouter()


@router.post("/reports")
async def submit_report(
    file: UploadFile = File(...),
    lat: float | None = None,
    lng: float | None = None,
    address: str = "",
    description: str = "",
):
    if ml_model.model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Place best.pt at backend-ml/models/best.pt",
        )
    contents = await file.read()
    suffix   = Path(file.filename or "upload.jpg").suffix or ".jpg"
    fname    = f"{uuid.uuid4()}{suffix}"

    # Detect in-memory before committing to storage
    img  = Image.open(io.BytesIO(contents)).convert("RGB")
    res  = ml_model.model.predict(img, conf=0.25)[0]
    boxes = [b.xyxy[0].tolist() for b in res.boxes]
    if not boxes:
        raise HTTPException(status_code=422, detail="No trash detected.")

    # Upload to Supabase; fall back to local disk
    image_path = await upload_image(contents, fname)
    if not image_path:
        (UPLOAD_DIR / fname).write_bytes(contents)
        image_path = fname

    report_id = str(uuid.uuid4())
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO reports (id, image_path, lat, lng, address, detections, count, created_at, description)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            report_id, image_path, lat, lng,
            address.strip() or None,
            json.dumps(boxes), len(boxes),
            datetime.now(timezone.utc).isoformat(),
            description.strip() or None,
        ),
    )
    conn.commit()
    cur.close()
    conn.close()

    image_url = image_path if image_path.startswith("http") else f"/uploads/{image_path}"
    return {
        "id":        report_id,
        "image_url": image_url,
        "count":     len(boxes),
        "lat":       lat,
        "lng":       lng,
        "address":   address,
    }


@router.post("/reports/seed")
async def seed_report(
    lat: float,
    lng: float,
    address: str = "",
    count: int = 1,
    description: str = "",
    file: UploadFile | None = File(None),
):
    """Dev/test endpoint — inserts a report row without requiring the YOLO model."""
    count      = max(count, 1)   # DB enforces CHECK (count >= 1)
    image_path = ""

    if file:
        contents   = await file.read()
        suffix     = Path(file.filename or "upload.jpg").suffix or ".jpg"
        fname      = f"{uuid.uuid4()}{suffix}"
        image_path = await upload_image(contents, fname) or ""
        if not image_path:
            (UPLOAD_DIR / fname).write_bytes(contents)
            image_path = fname

    report_id = str(uuid.uuid4())
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO reports (id, image_path, lat, lng, address, detections, count, created_at, description)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            report_id, image_path, lat, lng,
            address.strip() or None,
            json.dumps([]), count,
            datetime.now(timezone.utc).isoformat(),
            description.strip() or None,
        ),
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"id": report_id, "lat": lat, "lng": lng, "count": count}


@router.get("/reports")
def get_reports():
    """Return all confirmed reports ordered newest-first. Used by the React map."""
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM reports ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {**dict(r), "detections": json.loads(r["detections"] or "[]")}
        for r in rows
    ]
