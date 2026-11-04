"""
Core Sales Metrics & Analytics Computations.
Calculates KPIs, period-over-period growth, peak/lowest periods, and filtered views.
"""

from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np


def compute_overview_kpis(
    df_transactions: pd.DataFrame,
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
) -> Dict[str, Any]:
    """
    Computes overall or filtered KPI metrics directly from genuine transaction records.
    """
    df = df_transactions
    if start_date is not None:
        df = df[df["InvoiceDate"] >= pd.to_datetime(start_date)]
    if end_date is not None:
        df = df[df["InvoiceDate"] <= pd.to_datetime(end_date)]

    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_transactions": 0,
            "total_units_sold": 0,
            "average_order_value": 0.0,
            "number_of_products": 0,
            "number_of_countries": 0,
            "number_of_customers": 0,
        }

    total_revenue = float(df["Revenue"].sum())
    total_transactions = int(df["Invoice"].nunique())
    total_units_sold = int(df["Quantity"].sum())
    aov = round(total_revenue / total_transactions, 2) if total_transactions > 0 else 0.0
    num_products = int(df["StockCode"].nunique())
    num_countries = int(df["Country"].nunique())
    valid_customers = df[df["CustomerID_Clean"] != "Guest"]["CustomerID_Clean"].nunique()

    return {
        "total_revenue": round(total_revenue, 2),
        "total_transactions": total_transactions,
        "total_units_sold": total_units_sold,
        "average_order_value": aov,
        "number_of_products": num_products,
        "number_of_countries": num_countries,
        "number_of_customers": valid_customers,
    }


def compute_time_series_growth(df_series: pd.DataFrame, value_col: str = "Revenue") -> pd.DataFrame:
    """Computes period-over-period absolute and percentage growth."""
    res = df_series.copy()
    res["Previous_Value"] = res[value_col].shift(1)
    res["Growth_Absolute"] = res[value_col] - res["Previous_Value"]
    res["Growth_Pct"] = np.where(
        res["Previous_Value"] > 0,
        ((res["Growth_Absolute"] / res["Previous_Value"]) * 100).round(2),
        0.0
    )
    return res


def compute_peak_and_trough_periods(
    df: pd.DataFrame,
    date_col: str,
    metric_col: str = "Revenue",
    top_n: int = 5
) -> Dict[str, pd.DataFrame]:
    """Identifies peak and lowest performing periods."""
    valid_periods = df[df[metric_col] > 0]
    peaks = valid_periods.nlargest(top_n, metric_col)[[date_col, metric_col, "Transactions", "Quantity"]].reset_index(drop=True)
    troughs = valid_periods.nsmallest(top_n, metric_col)[[date_col, metric_col, "Transactions", "Quantity"]].reset_index(drop=True)
    return {
        "peaks": peaks,
        "troughs": troughs
    }
