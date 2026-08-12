"""One-time helper used to normalize the downloaded MIT-licensed dataset.

This script is kept under work/ because it is provenance/build tooling, not part
of the student-facing application.  It never invents a property record or an
attribute value.  Coordinates are geocoded from each real locality label and
unavailable parking values remain blank.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(r"C:\Users\Samarth\Documents\Codex\2026-08-12\build-a-complete-diploma-level-smart")
SOURCE = ROOT / "work" / "dataset-inspect" / "RE_Combined_Data.xlsx"
CACHE = ROOT / "work" / "geocode_cache.json"
OUTPUT = ROOT / "outputs" / "smart_india_house_price" / "data" / "india_housing.csv"


def geocode(query: str) -> tuple[float | None, float | None]:
    """Geocode one locality with the public OpenStreetMap Nominatim service."""
    params = urllib.parse.urlencode(
        {"q": query, "format": "jsonv2", "limit": 1, "countrycodes": "in"}
    )
    request = urllib.request.Request(
        f"https://nominatim.openstreetmap.org/search?{params}",
        headers={"User-Agent": "SmartIndiaHousePriceDiplomaProject/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
        if result:
            return float(result[0]["lat"]), float(result[0]["lon"])
    except Exception as exc:  # Continue and retry failed entries on the next run.
        print(f"Geocoding failed for {query!r}: {exc}", flush=True)
    return None, None


def main() -> None:
    raw = pd.read_excel(SOURCE, sheet_name="01_Combined_Data")
    raw = raw[raw["OWNTYPE"].astype(str).str.casefold().eq("owner")].copy()

    # Each address is a locality label such as "Sector 84 Gurgaon".
    locality_pairs = (
        raw[["ADDRESS", "CITY"]]
        .dropna()
        .drop_duplicates()
        .sort_values(["CITY", "ADDRESS"])
    )
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}

    for number, row in enumerate(locality_pairs.itertuples(index=False), start=1):
        address = str(row.ADDRESS).strip()
        city = str(row.CITY).strip()
        key = f"{address}|{city}"
        if key in cache and cache[key].get("latitude") is not None:
            continue

        latitude, longitude = geocode(f"{address}, {city}, India")
        # A shorter query sometimes works better for duplicated city wording.
        if latitude is None:
            time.sleep(1.1)
            latitude, longitude = geocode(f"{address}, India")

        cache[key] = {
            "latitude": latitude,
            "longitude": longitude,
            "query": f"{address}, {city}, India",
        }
        CACHE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
        print(f"{number}/{len(locality_pairs)} {address}: {latitude}, {longitude}", flush=True)
        time.sleep(1.1)  # Respect Nominatim's public-service rate limit.

    coords = {
        key: (value.get("latitude"), value.get("longitude"))
        for key, value in cache.items()
    }
    keys = raw["ADDRESS"].astype(str).str.strip() + "|" + raw["CITY"].astype(str).str.strip()
    raw["latitude"] = keys.map(lambda key: coords.get(key, (None, None))[0])
    raw["longitude"] = keys.map(lambda key: coords.get(key, (None, None))[1])

    # Prefer carpet area, otherwise use super-built-up area.  MIN_PRICE is INR.
    area = pd.to_numeric(raw["CARPET_SQFT"], errors="coerce")
    area = area.where(area.gt(0), pd.to_numeric(raw["SUPERBUILTUP_SQFT"], errors="coerce"))

    normalized = pd.DataFrame(
        {
            "location": raw["ADDRESS"].astype(str).str.strip(),
            "latitude": raw["latitude"],
            "longitude": raw["longitude"],
            "area": area,
            "bhk": pd.to_numeric(raw["BEDROOM_NUM"], errors="coerce"),
            "bathrooms": pd.to_numeric(raw["BATHROOM_NUM"], errors="coerce"),
            # The source does not report parking.  Blank is honest and train_model
            # handles it as an unknown value; no parking data is fabricated.
            "parking": np.nan,
            "property_age": pd.to_numeric(raw["AGE"], errors="coerce"),
            "furnishing": raw["FURNISH"].astype(str).str.strip(),
            "property_type": raw["PROPERTY_TYPE"].astype(str).str.strip(),
            "price": pd.to_numeric(raw["MIN_PRICE"], errors="coerce"),
            "city": raw["CITY"].astype(str).str.strip(),
            "source_id": raw["PROP_ID"].astype(str).str.strip(),
        }
    )

    normalized = normalized.replace({"nan": np.nan, "": np.nan})
    normalized = normalized.dropna(
        subset=["location", "latitude", "longitude", "area", "bhk", "price"]
    )
    normalized = normalized[
        normalized["latitude"].between(6, 38)
        & normalized["longitude"].between(68, 98)
        & normalized["area"].between(150, 20_000)
        & normalized["price"].between(100_000, 1_000_000_000)
    ]
    normalized = normalized.drop_duplicates(subset=["source_id"]).reset_index(drop=True)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_csv(OUTPUT, index=False)
    print(f"Saved {len(normalized):,} real sale listings to {OUTPUT}")


if __name__ == "__main__":
    main()
