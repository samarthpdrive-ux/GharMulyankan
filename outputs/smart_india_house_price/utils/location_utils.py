"""Indian address geocoding with Geopy and OpenStreetMap Nominatim."""

from __future__ import annotations

from functools import lru_cache

from geopy.exc import GeocoderServiceError, GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim


INDIA_BOUNDS = {"min_lat": 6.0, "max_lat": 38.0, "min_lon": 68.0, "max_lon": 98.0}


@lru_cache(maxsize=128)
def geocode_location(location_text: str) -> dict[str, float | str] | None:
    """Convert any Indian address, village, locality, city, or pincode to coordinates."""
    query = " ".join(str(location_text).split())
    if not query:
        return None

    geocoder = Nominatim(user_agent="smart_india_house_price_diploma_app", timeout=10)
    try:
        result = geocoder.geocode(
            query,
            country_codes="in",
            exactly_one=True,
            addressdetails=True,
            language="en",
        )
    except (GeocoderTimedOut, GeocoderUnavailable, GeocoderServiceError):
        return None

    if result is None:
        return None
    if not (
        INDIA_BOUNDS["min_lat"] <= result.latitude <= INDIA_BOUNDS["max_lat"]
        and INDIA_BOUNDS["min_lon"] <= result.longitude <= INDIA_BOUNDS["max_lon"]
    ):
        return None

    return {
        "display_name": result.address,
        "latitude": float(result.latitude),
        "longitude": float(result.longitude),
    }

