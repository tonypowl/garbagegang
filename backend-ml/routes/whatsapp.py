# POST /whatsapp — Twilio WhatsApp sandbox webhook.
# flow:  photo → description → location → saved report

from fastapi import APIRouter, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime, timezone
from PIL import Image
import io, json, uuid, httpx

import ml_model
from config import TWILIO_SID, TWILIO_TOKEN, UPLOAD_DIR
from database import db_conn
from storage import upload_image

router = APIRouter()

_convs: dict[str, dict] = {}


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form        = await request.form()
    from_number = str(form.get("From", ""))
    body        = str(form.get("Body", "")).strip()
    num_media   = int(form.get("NumMedia", 0))
    wa_lat      = form.get("Latitude")    # set when user shares a WhatsApp location pin
    wa_lng      = form.get("Longitude")
    wa_address  = str(form.get("Address", ""))

    resp = MessagingResponse()
    conv = _convs.get(from_number, {"step": "idle"})

    # ── Branch 1: user sent a photo ───────────────────────────────────────
    if num_media > 0:
        media_url = str(form.get("MediaUrl0", ""))
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                img_res = await client.get(media_url, auth=(TWILIO_SID, TWILIO_TOKEN))
            if img_res.status_code != 200:
                print(f"[whatsapp] media download failed: HTTP {img_res.status_code} for {media_url}")
                resp.message("⚠️ Couldn't download your image (media error). Please try again.")
                return Response(content=str(resp), media_type="application/xml")
        except Exception as e:
            print(f"[whatsapp] media download exception: {e}")
            resp.message("⚠️ Couldn't download your image. Please try again.")
            return Response(content=str(resp), media_type="application/xml")

        img_bytes = img_res.content

        if ml_model.model is None:
            _convs[from_number] = {
                "step":        "awaiting_description",
                "image_bytes": img_bytes,
                "count":       0,
            }
            resp.message(
                "📸 Got your photo! Detection is offline but we'll still log it.\n\n"
                "📝 Add a short description of the waste\n"
                "(e.g. 'construction debris by park gate'), or type *skip*."
            )
            return Response(content=str(resp), media_type="application/xml")

        img   = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        res   = ml_model.model.predict(img, conf=0.45)[0]
        count = len(res.boxes)

        if count == 0:
            resp.message(
                "🤔 I didn't detect any trash in that photo.\n"
                "Try a clearer or closer shot and send it again!"
            )
            return Response(content=str(resp), media_type="application/xml")
        else:
            _convs[from_number] = {
                "step":        "awaiting_description",
                "image_bytes": img_bytes,
                "count":       count,
            }
            resp.message(
                f"✅ Found *{count} trash item{'s' if count != 1 else ''}*!\n\n"
                f"📝 Add a short description of the waste\n"
                f"(e.g. 'mixed garbage near bus stop'), or type *skip*."
            )

    # ── Branch 2: user shared a WhatsApp location pin ─────────────────────
    elif wa_lat and wa_lng:
        if conv.get("step") == "awaiting_location":
            await _save_wa_report(
                from_number, float(wa_lat), float(wa_lng), wa_address, conv, resp
            )
        else:
            resp.message("👋 Send a photo of the trash first, then share your location!")

    # ── Branch 3: text message — description / typed address / greeting ────
    elif body:
        step = conv.get("step", "idle")
        if step == "awaiting_description":
            desc = "" if body.strip().lower() == "skip" else body.strip()
            _convs[from_number] = {**conv, "step": "awaiting_location", "description": desc}
            resp.message(
                "📍 Got it! Now share your *location* to pin it on the map.\n"
                "Tap the ＋ icon → Location, or type the address."
            )
        elif step == "awaiting_location":
            geo = await _geocode_query(body)
            if geo:
                await _save_wa_report(
                    from_number, geo["lat"], geo["lng"], geo["display_name"], conv, resp
                )
            else:
                resp.message(
                    "🔍 Couldn't find that address.\n"
                    "Try adding a city name or nearby landmark."
                )
        else:
            resp.message(
                "👋 Hi! I'm *GarbageGang Bot*.\n\n"
                "📸 Send me a *photo* of an illegal dump site and I'll detect "
                "the trash and log it on our public map!"
            )

    # ── Branch 4: nothing matched — show greeting ─────────────────────────
    else:
        resp.message(
            "👋 Hi! I'm *GarbageGang Bot*.\n\n"
            "📸 Send me a *photo* of an illegal dump site and I'll detect "
            "the trash and log it on our public map!"
        )

    return Response(content=str(resp), media_type="application/xml")


# ── Private helpers ────────────────────────────────────────────────────────

async def _geocode_query(query: str) -> dict | None:
    """Geocode a free-text address via Nominatim. Returns a dict or None."""
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": query, "format": "json", "limit": 1},
                headers={"User-Agent": "GarbageGang/1.0 (contact@example.com)"},
            )
        results = r.json()
        if not results:
            return None
        return {
            "lat":          float(results[0]["lat"]),
            "lng":          float(results[0]["lon"]),
            "display_name": results[0]["display_name"],
        }
    except Exception:
        return None


async def _save_wa_report(
    from_number: str,
    lat: float,
    lng: float,
    address: str,
    conv: dict,
    resp: MessagingResponse,
) -> None:
    """Upload image → insert DB row → reply with confirmation."""
    file_bytes  = conv.get("image_bytes", b"")
    description = conv.get("description", "")

    if not file_bytes:
        resp.message("⚠️ Couldn't find the image. Please send a new photo to start over.")
        _convs.pop(from_number, None)
        return

    # Run YOLO on the in-memory bytes
    if ml_model.model is None:
        boxes = []
        count = max(conv.get("count", 1), 1)
    else:
        img   = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        res   = ml_model.model.predict(img, conf=0.45)[0]
        boxes = [b.xyxy[0].tolist() for b in res.boxes]
        count = len(boxes)
        if not boxes:
            resp.message("⚠️ Re-analysis found no trash. Please try with a clearer photo.")
            _convs.pop(from_number, None)
            return

    # Upload to Supabase; fall back to local disk
    fname      = f"{uuid.uuid4()}.jpg"
    image_path = await upload_image(file_bytes, fname)
    if not image_path:
        (UPLOAD_DIR / fname).write_bytes(file_bytes)
        image_path = fname  # served via /uploads/<fname>

    report_id = str(uuid.uuid4())
    with db_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO reports (id, image_path, lat, lng, address, detections, count, created_at, description)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                report_id, image_path, lat, lng,
                address.strip() or None,
                json.dumps(boxes), count,
                datetime.now(timezone.utc).isoformat(),
                description or None,
            ),
        )
    _convs.pop(from_number, None)

    loc_str = address or f"{lat:.4f}, {lng:.4f}"
    resp.message(
        f"✅ *Report saved!* {count} item{'s' if count != 1 else ''} logged at _{loc_str}_."
        + (f"\n📝 _{description}_" if description else "")
        + "\n\n🌱 Thank you for helping keep streets clean!"
    )
