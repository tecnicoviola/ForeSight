"""
Feature Engineering for Weekly Sales Forecasting.
Strictly prevents target leakage by applying shifts before rolling windows.
"""

from typing import List, Tuple
import pandas as pd
import numpy as np

FEATURE_COLUMNS = [
    "TimeIndex",
    "Year",
    "Month",
    "WeekOfYear",
    "Lag_1",
    "Lag_2",
    "Lag_4",
    "Rolling_Mean_4",
]

TARGET_COLUMN = "Revenue"


def create_forecasting_features(weekly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs time-series lag and rolling features from chronological weekly revenue.
    Shift is applied before rolling window calculations to ensure zero target leakage.
    """
    df = weekly_df.sort_values("Week_Start").copy().reset_index(drop=True)
    
    # 1. Temporal calendar features
    df["TimeIndex"] = np.arange(len(df))
    df["Year"] = df["Week_Start"].dt.year
    df["Month"] = df["Week_Start"].dt.month
    df["WeekOfYear"] = df["Week_Start"].dt.isocalendar().week.astype(int)
    
    # 2. Lag features (prior historical weeks only)
    df["Lag_1"] = df[TARGET_COLUMN].shift(1)
    df["Lag_2"] = df[TARGET_COLUMN].shift(2)
    df["Lag_4"] = df[TARGET_COLUMN].shift(4)
    
    # 3. Rolling statistics (Strictly using past values via shift(1))
    df["Rolling_Mean_4"] = df[TARGET_COLUMN].shift(1).rolling(window=4).mean()
    
    return df


def prepare_training_data(weekly_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Creates feature dataframe, drops warm-up NaN rows resulting from 4-week lags,
    and returns (X, y, clean_df).
    """
    df_feat = create_forecasting_features(weekly_df)
    
    # Drop warm-up rows (first 4 weeks where Lag_4 and Rolling_Mean_4 are NaN)
    valid_df = df_feat.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN]).copy().reset_index(drop=True)
    
    X = valid_df[FEATURE_COLUMNS]
    y = valid_df[TARGET_COLUMN]
    
    return X, y, valid_df

