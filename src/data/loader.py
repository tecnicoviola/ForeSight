"""
Dataset Loader for SalesPulse.
Provides cached, lightning-fast access to processed datasets.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import streamlit as st

from src.utils.config import (
    CLEANED_PARQUET,
    DAILY_PARQUET,
    WEEKLY_PARQUET,
    MONTHLY_PARQUET,
    PRODUCT_PARQUET,
    COUNTRY_PARQUET,
    SUMMARY_JSON,
)


@st.cache_data(show_spinner=False)
def load_cleaning_summary() -> Dict[str, Any]:
    """Loads preprocessing audit metadata and metrics."""
    if not SUMMARY_JSON.exists():
        raise FileNotFoundError(f"Summary JSON not found at {SUMMARY_JSON}. Run preprocessing pipeline first.")
    with open(SUMMARY_JSON, "r") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_weekly_sales() -> pd.DataFrame:
    """Loads chronological weekly sales time-series."""
    if not WEEKLY_PARQUET.exists():
        raise FileNotFoundError(f"Weekly parquet not found at {WEEKLY_PARQUET}.")
    df = pd.read_parquet(WEEKLY_PARQUET)
    df["Week_Start"] = pd.to_datetime(df["Week_Start"])
    return df.sort_values("Week_Start").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_daily_sales() -> pd.DataFrame:
    """Loads daily sales aggregation."""
    if not DAILY_PARQUET.exists():
        raise FileNotFoundError(f"Daily parquet not found at {DAILY_PARQUET}.")
    df = pd.read_parquet(DAILY_PARQUET)
    df["Date"] = pd.to_datetime(df["Date"])
    return df.sort_values("Date").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_monthly_sales() -> pd.DataFrame:
    """Loads monthly sales aggregation."""
    if not MONTHLY_PARQUET.exists():
        raise FileNotFoundError(f"Monthly parquet not found at {MONTHLY_PARQUET}.")
    df = pd.read_parquet(MONTHLY_PARQUET)
    df["Month_Start"] = pd.to_datetime(df["Month_Start"])
    return df.sort_values("Month_Start").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_product_sales() -> pd.DataFrame:
    """Loads product-level sales aggregation."""
    if not PRODUCT_PARQUET.exists():
        raise FileNotFoundError(f"Product parquet not found at {PRODUCT_PARQUET}.")
    return pd.read_parquet(PRODUCT_PARQUET)


@st.cache_data(show_spinner=False)
def load_country_sales() -> pd.DataFrame:
    """Loads country-level sales aggregation."""
    if not COUNTRY_PARQUET.exists():
        raise FileNotFoundError(f"Country parquet not found at {COUNTRY_PARQUET}.")
    return pd.read_parquet(COUNTRY_PARQUET)


@st.cache_data(show_spinner=False)
def load_cleaned_transactions() -> pd.DataFrame:
    """Loads transaction-level dataset."""
    if not CLEANED_PARQUET.exists():
        raise FileNotFoundError(f"Cleaned parquet not found at {CLEANED_PARQUET}.")
    df = pd.read_parquet(CLEANED_PARQUET)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    return df

