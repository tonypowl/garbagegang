# backend-ml/storage.py
# Image upload helper.
# Tries Supabase Storage first; returns None if not configured or upload fails,
# so callers can fall back to saving to local disk.

import httpx
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET


async def upload_image(
    file_bytes: bytes, filename: str, content_type: str = "image/jpeg"
) -> str | None:
    """
    Upload image bytes to Supabase Storage.
    Returns the public URL on success, or None if Supabase is not configured / upload fails.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Create bucket if it doesn't exist yet — 409 means already exists, which is fine
            await client.post(
                f"{SUPABASE_URL}/storage/v1/bucket",
                json={"id": SUPABASE_BUCKET, "name": SUPABASE_BUCKET, "public": True},
                headers={
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                },
            )
            r = await client.post(
                f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{filename}",
                content=file_bytes,
                headers={
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": content_type,
                    "x-upsert": "false",
                },
            )
        if r.status_code in (200, 201):
            return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        print(f"⚠️  Supabase upload failed: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"⚠️  Supabase upload error: {e}")
    return None
