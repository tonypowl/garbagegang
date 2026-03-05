# backend-ml/routes/detect.py
# POST /detect — stateless image detection.
# Reads image into memory, runs YOLO, returns bounding boxes. Nothing is saved to disk or DB.

from fastapi import APIRouter, File, UploadFile, HTTPException
from PIL import Image
import io

import ml_model

router = APIRouter()


@router.post("/detect")
async def detect(file: UploadFile = File(...)):
    if ml_model.model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Place best.pt at backend-ml/models/best.pt",
        )
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    res = ml_model.model.predict(img, conf=0.45)[0]

    boxes = [
        {
            "x1":   float(b.xyxy[0][0]),
            "y1":   float(b.xyxy[0][1]),
            "x2":   float(b.xyxy[0][2]),
            "y2":   float(b.xyxy[0][3]),
            "conf": round(float(b.conf[0]), 3),
        }
        for b in res.boxes
    ]

    return {
        "trash_found": len(boxes) > 0,
        "count":       len(boxes),
        "detections":  boxes,
        "image_size":  {"w": img.width, "h": img.height},
    }
