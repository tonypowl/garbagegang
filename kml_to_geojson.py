"""
Convert GBA wards KML → GeoJSON for use in the React map.
Run from the project root:
  python kml_to_geojson.py
"""

import json
import re
from pathlib import Path
from lxml import etree

KML_PATH  = Path("/Users/antonyshibupaul/Downloads/gba-369-wards-december-2025.kml")
OUT_PATH  = Path("public/wards.geojson")

NS = {
    "kml": "http://www.opengis.net/kml/2.2",
    "gx":  "http://www.google.com/kml/ext/2.2",
}

def parse_coordinates(coord_text: str) -> list:
    """Parse KML coordinate string → list of [lng, lat] pairs."""
    points = []
    for token in coord_text.strip().split():
        parts = token.split(",")
        if len(parts) >= 2:
            try:
                lng, lat = float(parts[0]), float(parts[1])
                points.append([lng, lat])
            except ValueError:
                pass
    return points


def placemark_to_feature(pm) -> dict | None:
    # ── Properties ──────────────────────────────────────────────────────
    props: dict = {}
    for sd in pm.findall(".//kml:SimpleData", NS):
        name  = sd.get("name", "")
        value = (sd.text or "").strip()
        props[name] = value

    # ── Geometry ─────────────────────────────────────────────────────────
    # Support Polygon and MultiGeometry (multiple Polygons)
    polygons = []

    for poly in pm.findall(".//kml:Polygon", NS):
        outer = poly.find(".//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates", NS)
        if outer is None:
            continue
        exterior = parse_coordinates(outer.text or "")
        holes = []
        for inner in poly.findall(".//kml:innerBoundaryIs/kml:LinearRing/kml:coordinates", NS):
            holes.append(parse_coordinates(inner.text or ""))
        polygons.append([exterior] + holes)

    if not polygons:
        return None

    if len(polygons) == 1:
        geometry = {"type": "Polygon", "coordinates": polygons[0]}
    else:
        geometry = {"type": "MultiPolygon", "coordinates": polygons}

    return {"type": "Feature", "properties": props, "geometry": geometry}


def main():
    tree  = etree.parse(str(KML_PATH))
    root  = tree.getroot()

    features = []
    for pm in root.findall(".//kml:Placemark", NS):
        feat = placemark_to_feature(pm)
        if feat:
            features.append(feat)

    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)

    zone_names = sorted({
        f["properties"].get("zone_name", "")
        for f in features
        if f["properties"].get("zone_name")
    })

    print(f" Written {len(features)} features → {OUT_PATH}")
    print(f" Zones found ({len(zone_names)}):")
    for z in zone_names:
        print(f"    • {z}")


if __name__ == "__main__":
    main()
