"""
Data Preprocessing Pipeline for SalesPulse.
Cleans raw transaction records, computes revenue, and builds analytical aggregations.

Cleaning Methodology (Documented):
1. Raw transactions: 1,067,371 rows across sheets 'Year 2009-2010' and 'Year 2010-2011'.
2. Duplicates: Exact duplicate transaction rows are identified and removed.
3. Cancellations: Invoices beginning with 'C' indicate cancelled orders/returns and are excluded.
4. Non-positive Quantities: Quantities <= 0 represent returns, adjustments, or errors and are excluded.
5. Non-positive Unit Prices: Prices <= 0 represent bad debts, gifts, or manual system adjustments and are excluded.
6. Missing Customer IDs: Retained! Guest/anonymous transactions represent genuine sales.
7. Missing Descriptions: Imputed with 'Unspecified Product [' + StockCode + ']' to preserve valid transactions.
8. Revenue Calculation: Revenue = Quantity * Price.
9. Zero-sales preservation: Daily and weekly series are reindexed over the observed timeline with 0 fill.
"""

import json
import time
from pathlib import Path
from typing import Dict, Tuple
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_EXCEL_PATH = BASE_DIR / "data" / "raw" / "online_retail_II.xlsx"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def load_raw_dataset(excel_path: Path = RAW_EXCEL_PATH) -> pd.DataFrame:
    """Loads and concatenates both yearly sheets from the raw Excel workbook."""
    excel_path = Path(excel_path)
    if not excel_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at {excel_path}. Run download.py first.")

    print(f"[PREPROCESS] Loading raw workbook from {excel_path}...")
    t0 = time.time()
    
    # Read both sheets
    df_2009 = pd.read_excel(excel_path, sheet_name="Year 2009-2010")
    df_2010 = pd.read_excel(excel_path, sheet_name="Year 2010-2011")
    
    raw_df = pd.concat([df_2009, df_2010], ignore_index=True)
    print(f"[PREPROCESS] Loaded {len(raw_df):,} raw transactions across both sheets in {time.time() - t0:.1f}s.")
    return raw_df


def clean_transactions(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Cleans raw transactions according to documented criteria.
    Returns cleaned dataframe and a metadata dictionary recording all filtering decisions.
    """
    initial_rows = len(raw_df)
    
    # Standardize column names
    col_map = {
        "Invoice": "Invoice",
        "StockCode": "StockCode",
        "Description": "Description",
        "Quantity": "Quantity",
        "InvoiceDate": "InvoiceDate",
        "Price": "Price",
        "Customer ID": "CustomerID",
        "Country": "Country",
    }
    df = raw_df.rename(columns=col_map).copy()
    
    # 1. Deduplication
    dup_mask = df.duplicated()
    dup_count = int(dup_mask.sum())
    df = df[~dup_mask].copy()
    
    # 2. Date conversion
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    invalid_dates = int(df["InvoiceDate"].isna().sum())
    df = df[df["InvoiceDate"].notna()].copy()
    
    # 3. Clean string columns
    df["Invoice"] = df["Invoice"].astype(str).str.strip()
    df["StockCode"] = df["StockCode"].astype(str).str.strip()
    df["Country"] = df["Country"].astype(str).str.strip()
    
    # Identify cancellations
    is_cancellation = df["Invoice"].str.startswith("C", na=False) | (df["Quantity"] < 0)
    cancellation_count = int(is_cancellation.sum())
    
    # Filter cancellations
    df = df[~is_cancellation].copy()
    
    # 4. Filter positive quantities only
    non_pos_qty = int((df["Quantity"] <= 0).sum())
    df = df[df["Quantity"] > 0].copy()
    
    # 5. Filter positive prices only
    non_pos_price = int((df["Price"] <= 0).sum())
    df = df[df["Price"] > 0].copy()
    
    # 6. Handle missing descriptions without discarding transactions
    missing_desc_count = int(df["Description"].isna().sum())
    df["Description"] = df["Description"].fillna("Unspecified Item [" + df["StockCode"] + "]")
    df["Description"] = df["Description"].astype(str).str.strip()
    
    # 7. Customer ID missing count (retained as Guest)
    missing_cust_count = int(df["CustomerID"].isna().sum())
    # Format CustomerID: convert floats to int string or 'Guest'
    df["CustomerID_Clean"] = df["CustomerID"].apply(
        lambda x: f"{int(x)}" if pd.notna(x) and str(x).replace(".", "").isdigit() else "Guest"
    )
    
    # 8. Compute Revenue
    df["Quantity"] = df["Quantity"].astype(int)
    df["Price"] = df["Price"].astype(float)
    df["Revenue"] = (df["Quantity"] * df["Price"]).round(2)
    
    # Chronological sort
    df = df.sort_values("InvoiceDate").reset_index(drop=True)
    
    cleaned_rows = len(df)
    
    summary = {
        "initial_raw_records": initial_rows,
        "duplicate_rows_removed": dup_count,
        "invalid_dates_removed": invalid_dates,
        "cancellations_excluded": cancellation_count,
        "non_positive_quantity_removed": non_pos_qty,
        "non_positive_price_removed": non_pos_price,
        "missing_descriptions_imputed": missing_desc_count,
        "guest_transactions_retained": missing_cust_count,
        "final_cleaned_records": cleaned_rows,
        "retention_rate_pct": round(cleaned_rows / initial_rows * 100, 2),
        "min_invoice_date": str(df["InvoiceDate"].min()),
        "max_invoice_date": str(df["InvoiceDate"].max()),
        "total_revenue": round(float(df["Revenue"].sum()), 2),
        "total_units_sold": int(df["Quantity"].sum()),
        "total_invoices": int(df["Invoice"].nunique()),
        "total_products": int(df["StockCode"].nunique()),
        "total_countries": int(df["Country"].nunique()),
    }
    
    print(f"[PREPROCESS] Cleaned transactions: {cleaned_rows:,} retained out of {initial_rows:,} ({summary['retention_rate_pct']}%)")
    print(f"[PREPROCESS] Total calculated revenue: £{summary['total_revenue']:,.2f}")
    return df, summary


def generate_aggregations(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Generates daily, weekly, monthly, product, and country aggregations."""
    print("[PREPROCESS] Generating aggregations...")
    
    # 1. Daily Aggregation
    df["Date"] = df["InvoiceDate"].dt.date
    daily = df.groupby("Date").agg(
        Revenue=("Revenue", "sum"),
        Quantity=("Quantity", "sum"),
        Transactions=("Invoice", "nunique"),
        Customers=("CustomerID_Clean", lambda s: len(set(s[s != "Guest"]))),
        Products=("StockCode", "nunique")
    ).reset_index()
    
    # Ensure complete timeline with zero-fill for days with no sales
    min_date = df["InvoiceDate"].min().date()
    max_date = df["InvoiceDate"].max().date()
    all_days = pd.date_range(start=min_date, end=max_date, freq="D").date
    daily_indexed = daily.set_index("Date").reindex(all_days).fillna(0).reset_index()
    daily_indexed.rename(columns={"index": "Date"}, inplace=True)
    daily_indexed["Date"] = pd.to_datetime(daily_indexed["Date"])
    daily_indexed["DayOfWeek"] = daily_indexed["Date"].dt.day_name()
    daily_indexed["DayIndex"] = np.arange(len(daily_indexed))
    
    # 2. Weekly Aggregation (Consistent Monday start: 'W-MON')
    df["Week_Start"] = df["InvoiceDate"].dt.to_period("W-SUN").apply(lambda r: r.start_time)
    weekly = df.groupby("Week_Start").agg(
        Revenue=("Revenue", "sum"),
        Quantity=("Quantity", "sum"),
        Transactions=("Invoice", "nunique"),
        Customers=("CustomerID_Clean", lambda s: len(set(s[s != "Guest"]))),
        Products=("StockCode", "nunique")
    ).reset_index()
    
    min_week = df["Week_Start"].min()
    max_week = df["Week_Start"].max()
    all_weeks = pd.date_range(start=min_week, end=max_week, freq="W-MON")
    weekly_indexed = weekly.set_index("Week_Start").reindex(all_weeks).fillna(0).reset_index()
    weekly_indexed.rename(columns={"index": "Week_Start"}, inplace=True)
    weekly_indexed["Week_Start"] = pd.to_datetime(weekly_indexed["Week_Start"])
    weekly_indexed["Year"] = weekly_indexed["Week_Start"].dt.year
    weekly_indexed["WeekNumber"] = weekly_indexed["Week_Start"].dt.isocalendar().week.astype(int)
    weekly_indexed["TimeIndex"] = np.arange(len(weekly_indexed))
    weekly_indexed["AvgOrderValue"] = np.where(
        weekly_indexed["Transactions"] > 0,
        (weekly_indexed["Revenue"] / weekly_indexed["Transactions"]).round(2),
        0.0
    )
    
    # 3. Monthly Aggregation
    df["Month_Start"] = df["InvoiceDate"].dt.to_period("M").apply(lambda r: r.start_time)
    monthly = df.groupby("Month_Start").agg(
        Revenue=("Revenue", "sum"),
        Quantity=("Quantity", "sum"),
        Transactions=("Invoice", "nunique"),
        Customers=("CustomerID_Clean", lambda s: len(set(s[s != "Guest"]))),
        Products=("StockCode", "nunique")
    ).reset_index()
    
    min_month = df["Month_Start"].min()
    max_month = df["Month_Start"].max()
    all_months = pd.date_range(start=min_month, end=max_month, freq="MS")
    monthly_indexed = monthly.set_index("Month_Start").reindex(all_months).fillna(0).reset_index()
    monthly_indexed.rename(columns={"index": "Month_Start"}, inplace=True)
    monthly_indexed["Month_Start"] = pd.to_datetime(monthly_indexed["Month_Start"])
    monthly_indexed["YearMonth"] = monthly_indexed["Month_Start"].dt.strftime("%Y-%m")
    monthly_indexed["AvgOrderValue"] = np.where(
        monthly_indexed["Transactions"] > 0,
        (monthly_indexed["Revenue"] / monthly_indexed["Transactions"]).round(2),
        0.0
    )
    
    # 4. Product Aggregation
    # Identify primary description per StockCode (most frequent non-empty description)
    desc_mode = df.groupby("StockCode")["Description"].agg(lambda s: s.mode()[0] if not s.mode().empty else s.iloc[0])
    
    product = df.groupby("StockCode").agg(
        Revenue=("Revenue", "sum"),
        Quantity=("Quantity", "sum"),
        Transactions=("Invoice", "nunique"),
        AvgPrice=("Price", "mean")
    ).reset_index()
    product["Description"] = product["StockCode"].map(desc_mode)
    product["Revenue"] = product["Revenue"].round(2)
    product["AvgPrice"] = product["AvgPrice"].round(2)
    product = product.sort_values("Revenue", ascending=False).reset_index(drop=True)
    product["Revenue_Rank"] = np.arange(1, len(product) + 1)
    total_rev = product["Revenue"].sum()
    product["Revenue_Contribution_Pct"] = (product["Revenue"] / total_rev * 100).round(2)
    product["Cumulative_Revenue_Pct"] = (product["Revenue"].cumsum() / total_rev * 100).round(2)
    
    # 5. Country Aggregation
    country = df.groupby("Country").agg(
        Revenue=("Revenue", "sum"),
        Transactions=("Invoice", "nunique"),
        Quantity=("Quantity", "sum"),
        Customers=("CustomerID_Clean", lambda s: len(set(s[s != "Guest"]))),
        Products=("StockCode", "nunique")
    ).reset_index()
    country["Revenue"] = country["Revenue"].round(2)
    country = country.sort_values("Revenue", ascending=False).reset_index(drop=True)
    country["Revenue_Contribution_Pct"] = (country["Revenue"] / total_rev * 100).round(2)
    country["Cumulative_Revenue_Pct"] = (country["Revenue"].cumsum() / total_rev * 100).round(2)
    country["AvgOrderValue"] = np.where(
        country["Transactions"] > 0,
        (country["Revenue"] / country["Transactions"]).round(2),
        0.0
    )
    
    return {
        "daily": daily_indexed,
        "weekly": weekly_indexed,
        "monthly": monthly_indexed,
        "product": product,
        "country": country,
    }


def run_pipeline(force: bool = False) -> Dict:
    """Executes the full preprocessing pipeline and saves optimized Parquet datasets."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    cleaned_file = PROCESSED_DIR / "cleaned_transactions.parquet"
    daily_file = PROCESSED_DIR / "daily_sales.parquet"
    weekly_file = PROCESSED_DIR / "weekly_sales.parquet"
    monthly_file = PROCESSED_DIR / "monthly_sales.parquet"
    product_file = PROCESSED_DIR / "product_sales.parquet"
    country_file = PROCESSED_DIR / "country_sales.parquet"
    summary_file = PROCESSED_DIR / "cleaning_summary.json"
    
    if (
        not force
        and cleaned_file.exists()
        and weekly_file.exists()
        and product_file.exists()
        and summary_file.exists()
    ):
        print("[INFO] Processed parquet datasets already exist. Loading cached summary.")
        with open(summary_file, "r") as f:
            return json.load(f)
            
    raw_df = load_raw_dataset()
    cleaned_df, summary = clean_transactions(raw_df)
    aggregations = generate_aggregations(cleaned_df)
    
    print("[PREPROCESS] Saving optimized Parquet datasets...")
    # Save cleaned transactions with optimized types
    cleaned_df.to_parquet(cleaned_file, index=False, engine="pyarrow", compression="snappy")
    aggregations["daily"].to_parquet(daily_file, index=False, engine="pyarrow")
    aggregations["weekly"].to_parquet(weekly_file, index=False, engine="pyarrow")
    aggregations["monthly"].to_parquet(monthly_file, index=False, engine="pyarrow")
    aggregations["product"].to_parquet(product_file, index=False, engine="pyarrow")
    aggregations["country"].to_parquet(country_file, index=False, engine="pyarrow")
    
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
        
    print(f"[SUCCESS] Pipeline complete! All datasets saved to {PROCESSED_DIR}")
    return summary


if __name__ == "__main__":
    run_pipeline()

