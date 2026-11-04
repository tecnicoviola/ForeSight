"""
Model Training Module for SalesPulse.
Implements Chronological Train/Test Splitting and Three Multiple Regression Architectures:
1. Linear Regression
2. Polynomial Regression (degree 2 pipeline)
3. Random Forest Regressor
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor

from src.forecasting.feature_engineering import FEATURE_COLUMNS, TARGET_COLUMN


def chronological_split(
    X: pd.DataFrame,
    y: pd.Series,
    holdout_weeks: int = 12
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Performs chronological splitting without random shuffling.
    The earliest observations form the training set, and the final unseen weeks form the holdout test set.
    """
    n_samples = len(X)
    if holdout_weeks >= n_samples:
        raise ValueError(f"Holdout weeks ({holdout_weeks}) must be smaller than dataset length ({n_samples}).")

    split_idx = n_samples - holdout_weeks
    X_train = X.iloc[:split_idx].copy()
    X_test = X.iloc[split_idx:].copy()
    y_train = y.iloc[:split_idx].copy()
    y_test = y.iloc[split_idx:].copy()

    return X_train, X_test, y_train, y_test


def get_model_definitions() -> Dict[str, Any]:
    """Returns dictionary of model architectures and pipelines."""
    return {
        "Linear Regression": LinearRegression(),
        "Polynomial Regression": Pipeline([
            ("poly", PolynomialFeatures(degree=2, include_bias=False)),
            ("scaler", StandardScaler()),
            ("regressor", Ridge(alpha=50.0, random_state=42))
        ]),
        "Random Forest": RandomForestRegressor(
            n_estimators=100,
            max_depth=6,
            min_samples_split=4,
            random_state=42
        ),
    }


def train_models(
    X_train: pd.DataFrame,
    y_train: pd.Series
) -> Dict[str, Any]:
    """Fits all three regression models on the training partition."""
    models = get_model_definitions()
    fitted_models = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        fitted_models[name] = model

    return fitted_models
