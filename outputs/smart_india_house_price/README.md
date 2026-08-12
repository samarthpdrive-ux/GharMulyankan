# Smart India House Price Prediction System

A diploma-level Streamlit project that compares real listings across eight
Indian city markets, predicts a current valuation, explores transparent 5-year
and 10-year appreciation scenarios, and stores selected results in SQLite.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python train_model.py
streamlit run app.py
```

The city/locality questionnaire, training, predictions and comparable searches
work offline from the local CSV. No API key is required.

## Dataset schema

The included `data/india_housing.csv` is normalized real listing data. To use
your own data, preserve these columns (price must be total INR and area sq.ft):

```text
location, latitude, longitude, area, bhk, bathrooms, parking,
property_age, furnishing, property_type, price
```

Additional columns are allowed. Missing optional attributes are imputed inside
the Scikit-learn pipeline; rows must have location, coordinates, area, BHK and
price. Do not put lakhs/crores as unit-scaled decimals in `price`.

## Viva summary

- The user selects a city and a real locality available in the dataset.
- Exact-locality listings are used first; similar-size real listings from the
  same city complete the comparison when locality data is limited.
- A `ColumnTransformer` imputes numeric values, scales them, and one-hot encodes
  categorical values.
- Linear Regression and Random Forest use the same 80/20 split. The model with
  lower test RMSE is saved as a complete Joblib pipeline.
- SQLite stores only predictions the user explicitly saves.
- Five-year and ten-year values use compound growth at a rate selected by the
  user. They are scenarios, not time-series model forecasts.
- Dashboard, History and Model Performance are separate Streamlit pages.

Predictions are educational estimates, not professional valuations or financial
advice. Sparse nearby evidence is clearly marked in the interface.
