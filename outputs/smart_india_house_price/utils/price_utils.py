"""Indian currency formatting helpers."""

from __future__ import annotations

import math


def format_indian_number(value: float, decimals: int = 0) -> str:
    """Format a number with Indian digit grouping, for example 1,25,00,000."""
    if value is None or not math.isfinite(float(value)):
        return "—"

    sign = "-" if value < 0 else ""
    absolute = abs(float(value))
    fixed = f"{absolute:.{decimals}f}"
    integer, _, fraction = fixed.partition(".")

    if len(integer) > 3:
        last_three = integer[-3:]
        leading = integer[:-3]
        pairs = []
        while leading:
            pairs.insert(0, leading[-2:])
            leading = leading[:-2]
        integer = ",".join(pairs + [last_three])

    suffix = f".{fraction}" if decimals else ""
    return f"{sign}{integer}{suffix}"


def format_price(value: float) -> str:
    """Display INR values in rupees, lakh, or crore using familiar Indian units."""
    if value is None or not math.isfinite(float(value)):
        return "—"

    value = max(0.0, float(value))
    if value >= 10_000_000:
        return f"₹{value / 10_000_000:.2f} Crore"
    if value >= 100_000:
        return f"₹{value / 100_000:.2f} Lakh"
    return f"₹{format_indian_number(value, 0)}"


def format_price_per_sqft(value: float) -> str:
    """Format a rupee-per-square-foot value."""
    if value is None or not math.isfinite(float(value)):
        return "—"
    return f"₹{format_indian_number(value, 0)} / sq.ft"

