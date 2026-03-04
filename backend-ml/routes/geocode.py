# backend-ml/routes/geocode.py
# GET /geocode — proxies Nominatim (OpenStreetMap). Free, no API key required.
# OSM requires a descriptive User-Agent header — do not remove it.

from fastapi import APIRouter, Query
import httpx

router = APIRouter()


@router.get("/geocode")
async def geocode(q: str = Query(..., min_length=3)):
    async with httpx.AsyncClient(timeout=8.0) as client:
        r = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": q, "format": "json", "limit": 1},
            headers={"User-Agent": "GarbageGang/1.0 (contact@example.com)"},
        )
    results = r.json()
    if not results:
        return {"found": False}
    return {
        "found":        True,
        "lat":          float(results[0]["lat"]),
        "lng":          float(results[0]["lon"]),
        "display_name": results[0]["display_name"],
    }
