from fastapi import APIRouter, Query
import httpx

router = APIRouter()


@router.get("/geocode")
async def geocode(q: str = Query(..., min_length=3)):
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": q, "format": "json", "limit": 1},
                headers={"User-Agent": "GarbageGang/1.0 (contact@example.com)"},
            )
        if r.status_code != 200 or not r.content:
            return {"found": False}
        results = r.json()
    except Exception:
        return {"found": False}

    if not results:
        return {"found": False}
    return {
        "found":        True,
        "lat":          float(results[0]["lat"]),
        "lng":          float(results[0]["lon"]),
        "display_name": results[0]["display_name"],
    }
