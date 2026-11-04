"""
Recursive Multi-Step Forecasting Engine for SalesPulse.
Predicts future weekly sales using recursive autoregression, updating lag features dynamically.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

from src.forecasting.feature_engineering import FEATURE_COLUMNS, TARGET_COLUMN


def forecast_future_weeks(
    model: Any,
    historical_weekly_df: pd.DataFrame,
    horizon_weeks: int = 8,
    model_name: str = "Trained Regressor"
) -> pd.DataFrame:
    """
    Generates genuine recursive predictions for H future weeks.
    At each step h, lag and rolling features are derived from genuine past actuals
    and preceding model predictions.
    """
    df_sorted = historical_weekly_df.sort_values("Week_Start").copy().reset_index(drop=True)
    if len(df_sorted) < 5:
        raise ValueError("Insufficient historical observations for recursive forecasting.")

    # We maintain a buffer of dates and revenues
    revenue_history = list(df_sorted[TARGET_COLUMN].values)
    dates_history = list(df_sorted["Week_Start"].values)
    last_time_index = len(df_sorted) - 1

    future_records = []

    for step in range(1, horizon_weeks + 1):
        # 1. Compute future week timestamp (7 days after preceding date)
        next_date = pd.to_datetime(dates_history[-1]) + pd.Timedelta(days=7)
        next_time_index = last_time_index + step
        
        # 2. Extract lag values from the rolling history buffer
        lag_1 = revenue_history[-1]
        lag_2 = revenue_history[-2]
        lag_4 = revenue_history[-4]
        rolling_4 = float(np.mean(revenue_history[-4:]))

        # 3. Assemble feature row
        feat_dict = {
            "TimeIndex": next_time_index,
            "Year": next_date.year,
            "Month": next_date.month,
            "WeekOfYear": int(next_date.isocalendar().week),
            "Lag_1": lag_1,
            "Lag_2": lag_2,
            "Lag_4": lag_4,
            "Rolling_Mean_4": rolling_4,
        }
        X_future = pd.DataFrame([feat_dict])[FEATURE_COLUMNS]

        # 4. Predict next revenue
        pred_val = float(model.predict(X_future)[0])
        # Non-negative bounded revenue
        pred_val = max(0.0, round(pred_val, 2))

        # 5. Append to buffer for subsequent recursive steps
        revenue_history.append(pred_val)
        dates_history.append(next_date)

        future_records.append({
            "Week_Start": next_date,
            "Predicted_Revenue": pred_val,
            "Horizon_Week": step,
            "Model": model_name,
            "Type": "Forecast",
        })

    return pd.DataFrame(future_records)
