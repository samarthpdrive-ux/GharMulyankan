"""Optional SQLite helpers retained for classroom demonstration.

The deployed Streamlit pages use per-browser local storage instead, so this
module is not imported by the live app and does not store visitor history.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "data" / "predictions.db"


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection whose rows can be read like dictionaries."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def _create_predictions_table(connection: sqlite3.Connection) -> None:
    """Create the current history schema."""
    connection.execute(
        """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                location TEXT NOT NULL,
                city TEXT,
                latitude REAL,
                longitude REAL,
                area REAL NOT NULL,
                bhk INTEGER NOT NULL,
                bathrooms INTEGER NOT NULL,
                parking INTEGER NOT NULL,
                property_age INTEGER NOT NULL,
                furnishing TEXT NOT NULL,
                property_type TEXT NOT NULL,
                predicted_price REAL NOT NULL,
                nearby_average_price REAL,
                nearby_price_per_sqft REAL,
                houses_found INTEGER NOT NULL,
                comparison_scope TEXT,
                annual_growth_rate REAL,
                projected_price_5y REAL,
                projected_price_10y REAL,
                search_radius REAL,
                model_name TEXT NOT NULL
            )
        """
    )


def init_database() -> None:
    """Create or safely upgrade the local prediction-history table."""
    with get_connection() as connection:
        table_exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='predictions'"
        ).fetchone()
        if not table_exists:
            _create_predictions_table(connection)
            return

        old_columns = {
            row["name"]: row for row in connection.execute("PRAGMA table_info(predictions)")
        }
        needs_upgrade = "city" not in old_columns or bool(old_columns["latitude"]["notnull"])
        if not needs_upgrade:
            return

        # Rebuild because SQLite cannot remove a NOT NULL constraint in place.
        # Existing rows are copied before the legacy table is removed.
        connection.execute("ALTER TABLE predictions RENAME TO predictions_legacy")
        _create_predictions_table(connection)
        new_columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(predictions)")
        }
        shared = [name for name in old_columns if name in new_columns]
        names = ", ".join(shared)
        connection.execute(
            f"INSERT INTO predictions ({names}) SELECT {names} FROM predictions_legacy"
        )
        connection.execute("DROP TABLE predictions_legacy")


def save_prediction(prediction: dict[str, Any]) -> int:
    """Save one user-approved prediction and return its database id."""
    columns = [
        "location",
        "city",
        "latitude",
        "longitude",
        "area",
        "bhk",
        "bathrooms",
        "parking",
        "property_age",
        "furnishing",
        "property_type",
        "predicted_price",
        "nearby_average_price",
        "nearby_price_per_sqft",
        "houses_found",
        "comparison_scope",
        "annual_growth_rate",
        "projected_price_5y",
        "projected_price_10y",
        "model_name",
    ]
    values = [prediction.get(column) for column in columns]
    placeholders = ", ".join("?" for _ in columns)

    with get_connection() as connection:
        cursor = connection.execute(
            f"INSERT INTO predictions ({', '.join(columns)}) VALUES ({placeholders})",
            values,
        )
        return int(cursor.lastrowid)


def get_prediction_history(limit: int | None = None) -> pd.DataFrame:
    """Return saved predictions, newest first."""
    query = "SELECT * FROM predictions ORDER BY datetime(created_at) DESC, id DESC"
    parameters: tuple[int, ...] = ()
    if limit is not None:
        query += " LIMIT ?"
        parameters = (int(limit),)

    with get_connection() as connection:
        return pd.read_sql_query(query, connection, params=parameters)


def get_history_summary() -> dict[str, float | int]:
    """Return small dashboard totals without loading the whole table."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                AVG(predicted_price) AS average_price,
                MAX(predicted_price) AS highest_price
            FROM predictions
            """
        ).fetchone()
    return {
        "total": int(row["total"] or 0),
        "average_price": float(row["average_price"] or 0),
        "highest_price": float(row["highest_price"] or 0),
    }
