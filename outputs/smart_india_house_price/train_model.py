"""Train, compare, and save the house-price regression pipeline.

Run this file once before opening the Streamlit app:
    python train_model.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "india_housing.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "best_model.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

NUMERIC_FEATURES = [
    "area",
    "bhk",
    "bathrooms",
    "parking",
    "property_age",
]
CATEGORICAL_FEATURES = ["city", "location", "furnishing", "property_type"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "price"
REQUIRED_DATA_COLUMNS = ["location", *FEATURES, TARGET]


def load_and_clean_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Read the canonical CSV and apply only transparent quality checks."""
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}\n"
            "Place a real dataset at data/india_housing.csv using the schema in README.md."
        )

    data = pd.read_csv(path)
    missing_columns = sorted(set(REQUIRED_DATA_COLUMNS) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing_columns)}")

    data = data.copy()
    for column in NUMERIC_FEATURES + [TARGET]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    for column in CATEGORICAL_FEATURES:
        data[column] = data[column].astype("string").str.strip()

    # These checks remove impossible/error rows; they do not manufacture values.
    data = data.dropna(subset=["city", "location", "area", "bhk", TARGET])
    data = data[
        data["area"].between(150, 20_000)
        & data["bhk"].between(1, 15)
        & data[TARGET].between(100_000, 1_000_000_000)
    ]
    data = data.drop_duplicates().reset_index(drop=True)

    if len(data) < 50:
        raise ValueError(
            f"Only {len(data)} valid rows remain. At least 50 real property rows are required."
        )
    return data


def build_preprocessor() -> ColumnTransformer:
    """Create reusable numeric and categorical preprocessing steps."""
    numeric_pipeline = Pipeline(
        steps=[
            # Constant imputation keeps genuinely unavailable fields explicit.
            (
                "imputer",
                SimpleImputer(
                    strategy="constant", fill_value=-1, keep_empty_features=True
                ),
            ),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )


def calculate_metrics(actual: pd.Series, predicted: np.ndarray) -> dict[str, float]:
    """Calculate all requested regression metrics in the original rupee scale."""
    return {
        "MAE": float(mean_absolute_error(actual, predicted)),
        "RMSE": float(np.sqrt(mean_squared_error(actual, predicted))),
        "R2": float(r2_score(actual, predicted)),
    }


def train_and_compare(data: pd.DataFrame) -> tuple[Pipeline, dict]:
    """Train both models on the same split and select the lower-RMSE model."""
    x_train, x_test, y_train, y_test = train_test_split(
        data[FEATURES],
        data[TARGET],
        test_size=0.20,
        random_state=42,
    )

    candidates = {
        "Linear Regression": LinearRegression(),
        "Random Forest Regression": RandomForestRegressor(
            n_estimators=120,
            max_depth=18,
            min_samples_leaf=3,
            random_state=42,
            n_jobs=-1,
        ),
    }

    trained_models: dict[str, Pipeline] = {}
    metrics: dict[str, dict[str, float]] = {}

    for model_name, estimator in candidates.items():
        pipeline = Pipeline(
            steps=[("preprocessor", build_preprocessor()), ("model", estimator)]
        )
        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)
        trained_models[model_name] = pipeline
        metrics[model_name] = calculate_metrics(y_test, predictions)

    selected_name = min(metrics, key=lambda name: metrics[name]["RMSE"])
    metadata = {
        "selected_model": selected_name,
        "selection_rule": "Lowest RMSE on the same held-out 20% test set",
        "metrics": metrics,
        "dataset_rows": int(len(data)),
        "training_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "features": FEATURES,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "random_state": 42,
        "dataset_file": DATA_PATH.name,
        "dataset_note": (
            "Real sale listings from eight Indian city markets; missing source attributes "
            "remain missing and are imputed inside the saved pipeline. Metrics are calculated "
            "during this run."
        ),
    }
    return trained_models[selected_name], metadata


def main() -> None:
    """Command-line entry point."""
    print(f"Loading real property data from: {DATA_PATH}")
    data = load_and_clean_data()
    print(f"Valid rows: {len(data):,}")
    print("Training Linear Regression and Random Forest Regression...")

    best_pipeline, metadata = train_and_compare(data)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, MODEL_PATH)
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print("\nModel comparison (real held-out test data):")
    for name, values in metadata["metrics"].items():
        print(
            f"  {name:<27} MAE INR {values['MAE']:,.0f} | "
            f"RMSE INR {values['RMSE']:,.0f} | R2 {values['R2']:.4f}"
        )
    print(f"\nSelected: {metadata['selected_model']} ({metadata['selection_rule']})")
    print(f"Saved complete pipeline to: {MODEL_PATH}")
    print(f"Saved measured metrics to: {METADATA_PATH}")


if __name__ == "__main__":
    main()
