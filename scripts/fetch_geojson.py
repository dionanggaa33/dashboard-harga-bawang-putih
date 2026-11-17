"""Unduh dan proses GeoJSON kabupaten/kota Jawa Tengah dari GADM 4.1.

Jalankan sekali untuk menyiapkan aset lokal:
    python scripts/fetch_geojson.py

Hasil: assets/jateng_kabupaten.geojson (feature ringkas, properti `name`).
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "jateng_kabupaten.geojson"
URL = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_IDN_2.json"


def main() -> int:
    print(f"Mengunduh {URL} ...")
    with urllib.request.urlopen(URL, timeout=120) as response:  # noqa: S310 - sumber tepercaya (GADM)
        data = json.loads(response.read().decode("utf-8"))

    features = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        if props.get("NAME_1") != "JawaTengah":
            continue
        name = str(props.get("NAME_2", "")).strip()
        tipe = str(props.get("TYPE_2", "")).strip().lower()
        if not name or name.lower().startswith("waduk"):
            continue  # abaikan bentukan waduk
        if tipe == "kota":
            continue  # fokus ke kabupaten sesuai cakupan data harga
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "name": name,
                    "kode": props.get("CC_2", ""),
                    "tipe": props.get("TYPE_2", ""),
                },
                "geometry": feature.get("geometry"),
            }
        )

    collection = {"type": "FeatureCollection", "features": features}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as file:
        json.dump(collection, file, ensure_ascii=False)

    size_kb = OUT.stat().st_size / 1024
    print(f"Tersimpan: {OUT} ({len(features)} fitur, {size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
