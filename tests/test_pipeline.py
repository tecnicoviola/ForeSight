"""
Comprehensive Test Suite for SalesPulse.
Validates:
- Data loading, column integrity, revenue computation.
- Filtering of cancellations and invalid transactions.
- Zero leakage in feature engineering.
- Chronological train/test split.
- Model training and recursive future prediction.
"""

import pytest
import pandas as pd
import numpy as np

from src.data.loader import (
    load_cleaning_summary,
    load_weekly_sales,
    load_daily_sales,
    load_product_sales,
    load_country_sales,
)
from src.forecasting.feature_engineering import (
    create_forecasting_features,
    prepare_training_data,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
)
from src.forecasting.train import (
    chronological_split,
    get_model_definitions,
    train_models,
)
from src.forecasting.evaluate import (
    evaluate_predictions,
    compare_models,
)
from src.forecasting.predict import (
    forecast_future_weeks,
)


def test_cleaning_summary_integrity():
    summary = load_cleaning_summary()
    assert summary["initial_raw_records"] == 1_067_371
    assert summary["final_cleaned_records"] > 900_000
    assert summary["cancellations_excluded"] > 0
    assert summary["total_revenue"] > 15_000_000
    assert summary["total_units_sold"] > 5_000_000


def test_weekly_sales_aggregation():
    weekly = load_weekly_sales()
    assert not weekly.empty
    assert "Week_Start" in weekly.columns
    assert "Revenue" in weekly.columns
    assert "Quantity" in weekly.columns
    assert "Transactions" in weekly.columns
    # Check chronological ordering
    assert weekly["Week_Start"].is_monotonic_increasing
    # Check no negative revenues
    assert (weekly["Revenue"] >= 0).all()


def test_product_and_country_aggregations():
    products = load_product_sales()
    countries = load_country_sales()
    assert len(products) > 1000
    assert len(countries) >= 35
    assert "Revenue_Rank" in products.columns
    assert products["Revenue"].iloc[0] >= products["Revenue"].iloc[1]  # sorted descending
    assert "United Kingdom" in countries["Country"].values


def test_feature_engineering_no_leakage():
    weekly = load_weekly_sales()
    X, y, df_clean = prepare_training_data(weekly)
    
    assert len(X) == len(y)
    assert not X.isna().any().any()
    
    # Verify Lag_1 equals previous week revenue
    orig_rev = df_clean[TARGET_COLUMN].values
    lag1 = df_clean["Lag_1"].values
    np.testing.assert_array_equal(orig_rev[:-1], lag1[1:])

    # Verify Rolling_Mean_4 strictly uses preceding weeks
    # At index 4, Rolling_Mean_4 must be mean of indices 0, 1, 2, 3
    expected_roll = np.mean(orig_rev[0:4])
    assert abs(df_clean["Rolling_Mean_4"].iloc[4] - expected_roll) < 1e-4


def test_chronological_split():
    weekly = load_weekly_sales()
    X, y, _ = prepare_training_data(weekly)
    holdout = 12
    X_train, X_test, y_train, y_test = chronological_split(X, y, holdout_weeks=holdout)
    
    assert len(X_test) == holdout
    assert len(X_train) == len(X) - holdout
    # Test indices must be strictly greater than train indices
    assert X_train.index.max() < X_test.index.min()
    assert X_train["TimeIndex"].max() < X_test["TimeIndex"].min()


def test_model_training_and_evaluation():
    weekly = load_weekly_sales()
    X, y, _ = prepare_training_data(weekly)
    X_train, X_test, y_train, y_test = chronological_split(X, y, holdout_weeks=12)
    
    fitted_models = train_models(X_train, y_train)
    assert "Linear Regression" in fitted_models
    assert "Polynomial Regression" in fitted_models
    assert "Random Forest" in fitted_models

    eval_result = compare_models(fitted_models, X_test, y_test)
    comp_df = eval_result["comparison_table"]
    
    assert len(comp_df) == 3
    assert set(comp_df["Model"]) == {"Linear Regression", "Polynomial Regression", "Random Forest"}
    for _, row in comp_df.iterrows():
        assert row["MAE (£)"] > 0
        assert row["RMSE (£)"] > 0
        assert not np.isnan(row["R²"])


def test_recursive_forecasting():
    weekly = load_weekly_sales()
    X, y, _ = prepare_training_data(weekly)
    X_train, _, y_train, _ = chronological_split(X, y, holdout_weeks=12)
    models = train_models(X_train, y_train)
    
    model = models["Linear Regression"]
    for horizon in [4, 8, 12]:
        future_df = forecast_future_weeks(model, weekly, horizon_weeks=horizon)
        assert len(future_df) == horizon
        assert (future_df["Predicted_Revenue"] >= 0).all()
        assert future_df["Week_Start"].is_monotonic_increasing
        assert future_df["Week_Start"].iloc[0] > weekly["Week_Start"].max()

