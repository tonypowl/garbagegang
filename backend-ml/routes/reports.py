# POST /reports        — chatbot-confirmed submission (requires YOLO model)
# GET  /reports        — fetch all reports for the map

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import io, json, uuid

import ml_model
from config import UPLOAD_DIR
from database import db_conn
from storage import upload_image

router = APIRouter()


@router.post("/reports")
async def submit_report(
    file: UploadFile = File(...),
    lat: float | None = Form(None),
    lng: float | None = Form(None),
    address: str = Form(""),
    description: str = Form(""),
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
    res  = ml_model.model.predict(img, conf=0.45)[0]
    boxes = [b.xyxy[0].tolist() for b in res.boxes]
    if not boxes:
        raise HTTPException(status_code=422, detail="No trash detected.")

    # Upload to Supabase; fall back to local disk
    image_path = await upload_image(contents, fname)
    if not image_path:
        (UPLOAD_DIR / fname).write_bytes(contents)
        image_path = fname

    report_id = str(uuid.uuid4())
    with db_conn() as conn:
        cur = conn.cursor()
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

    image_url = image_path if image_path.startswith("http") else f"/uploads/{image_path}"
    return {
        "id":        report_id,
        "image_url": image_url,
        "count":     len(boxes),
        "lat":       lat,
        "lng":       lng,
        "address":   address,
    }




@router.get("/reports")
def get_reports():
    """Return all confirmed reports ordered newest-first. Used by the React map."""
    with db_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM reports ORDER BY created_at DESC")
        rows = cur.fetchall()
    return [
        {**dict(r), "detections": json.loads(r["detections"] or "[]")}
        for r in rows
    ]
