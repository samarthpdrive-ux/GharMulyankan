# Dataset provenance

`india_housing.csv` contains 37,084 normalized real sale-listing rows covering
Bengaluru, Chennai, Delhi, Gurgaon, Hyderabad, Kolkata, Mumbai and Pune.

Sources:

1. **Real Estate Data** by Prithu Verma (MIT license) — Gurgaon owner/sale
   listings with locality and property attributes.
   https://www.kaggle.com/datasets/lamskdna/real-estate-data
2. **House Price Prediction Dataset & Code** by Tushar Paul (CC0) — scraped
   metropolitan listings for Bengaluru, Chennai, Delhi, Hyderabad, Kolkata and
   Mumbai.
   https://www.kaggle.com/datasets/tusharpaul2001/house-price-prediction
3. **Housing Prices for Indian Cities** by Sambhav Garg (CC0) — Pune builder
   floor and villa listings.
   https://www.kaggle.com/datasets/sambhavsg/housing-prices-for-indian-cities

The sources do not all report every attribute. Missing bathrooms, parking,
property age, furnishing, property type, latitude or longitude remain blank and
are imputed inside the Scikit-learn pipeline. No houses or missing property
values are invented. Location comparisons use exact locality first and then
similar-size real listings from the same city when necessary.

The dataset has no historical time series. The app's 5-year and 10-year values
are therefore user-controlled compound-appreciation scenarios, not fabricated
model scores or claims of historical forecasting accuracy.
