"""Fast geographic-distance and comparable-property helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd


SEARCH_RADII_KM = (1, 3, 5, 10, 20)


def find_market_comparables(
    properties: pd.DataFrame,
    city: str,
    location: str,
    area: float,
    bhk: int,
    requested_count: int = 10,
) -> tuple[pd.DataFrame, str, int]:
    """Find real comparable listings in the selected locality and city.

    Exact-locality records are ranked first. If a small locality does not contain
    enough records, similar-size homes from the same city complete the list. This
    provides honest multi-city comparisons when exact coordinates are unavailable.
    """
    working = properties[properties["city"].astype(str).eq(str(city))].copy()
    if working.empty:
        return working, "No market data", 0

    working["same_locality"] = working["location"].astype(str).eq(str(location))
    same_locality_count = int(working["same_locality"].sum())
    working["price_per_sqft"] = working["price"] / working["area"]
    working["similarity_score"] = (
        (working["area"] - float(area)).abs() / max(float(area), 1.0)
        + (working["bhk"] - int(bhk)).abs() * 0.35
    )
    working = working.replace([np.inf, -np.inf], np.nan).dropna(
        subset=["price", "area", "price_per_sqft", "similarity_score"]
    )
    working = working.sort_values(
        ["same_locality", "similarity_score"], ascending=[False, True]
    )
    selected = working.head(int(requested_count)).reset_index(drop=True)
    scope = (
        f"{location} locality"
        if same_locality_count >= requested_count
        else f"{location} + similar homes in {city}"
    )
    return selected, scope, same_locality_count


def haversine_distances(
    latitudes: pd.Series | np.ndarray,
    longitudes: pd.Series | np.ndarray,
    target_latitude: float,
    target_longitude: float,
) -> np.ndarray:
    """Calculate great-circle distances from one point using the Haversine formula."""
    earth_radius_km = 6371.0088
    lat1 = np.radians(np.asarray(latitudes, dtype=float))
    lon1 = np.radians(np.asarray(longitudes, dtype=float))
    lat2 = np.radians(float(target_latitude))
    lon2 = np.radians(float(target_longitude))

    delta_lat = lat1 - lat2
    delta_lon = lon1 - lon2
    value = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat2) * np.cos(lat1) * np.sin(delta_lon / 2) ** 2
    )
    return earth_radius_km * 2 * np.arctan2(np.sqrt(value), np.sqrt(1 - value))


def find_nearby_properties(
    properties: pd.DataFrame,
    latitude: float,
    longitude: float,
    requested_count: int = 10,
) -> tuple[pd.DataFrame, int, int]:
    """Use the smallest standard radius containing the requested comparables.

    Returns the selected comparable rows, chosen radius, and total rows available
    inside that radius.  When 20 km still has too few rows, every available row is
    returned so the UI can truthfully mark the market evidence as limited.
    """
    if properties.empty:
        return properties.copy(), SEARCH_RADII_KM[-1], 0

    working = properties.copy()
    working["distance_km"] = haversine_distances(
        working["latitude"], working["longitude"], latitude, longitude
    )
    working["price_per_sqft"] = working["price"] / working["area"]
    working = working.replace([np.inf, -np.inf], np.nan).dropna(
        subset=["distance_km", "price", "area", "price_per_sqft"]
    )

    chosen_radius = SEARCH_RADII_KM[-1]
    within_radius = working[working["distance_km"] <= chosen_radius]
    for radius in SEARCH_RADII_KM:
        candidates = working[working["distance_km"] <= radius]
        if len(candidates) >= requested_count:
            chosen_radius = radius
            within_radius = candidates
            break

    within_radius = within_radius.sort_values("distance_km")
    available_count = len(within_radius)
    return within_radius.head(requested_count).reset_index(drop=True), chosen_radius, available_count


def get_market_statistics(nearby: pd.DataFrame) -> dict[str, float | int | None]:
    """Summarize only the real comparable rows currently selected."""
    if nearby.empty:
        return {
            "average_price": None,
            "median_price": None,
            "price_per_sqft": None,
            "houses_found": 0,
        }
    return {
        "average_price": float(nearby["price"].mean()),
        "median_price": float(nearby["price"].median()),
        "price_per_sqft": float(nearby["price_per_sqft"].mean()),
        "houses_found": int(len(nearby)),
    }
