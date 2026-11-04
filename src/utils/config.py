"""
Application Configuration and Design Constants for SalesPulse.
Inspired by Toolfolio.com: Modern, minimal, professional, data-focused, clean light aesthetic.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
ASSETS_DIR = BASE_DIR / "assets"

RAW_EXCEL_PATH = RAW_DIR / "online_retail_II.xlsx"
CLEANED_PARQUET = PROCESSED_DIR / "cleaned_transactions.parquet"
DAILY_PARQUET = PROCESSED_DIR / "daily_sales.parquet"
WEEKLY_PARQUET = PROCESSED_DIR / "weekly_sales.parquet"
MONTHLY_PARQUET = PROCESSED_DIR / "monthly_sales.parquet"
PRODUCT_PARQUET = PROCESSED_DIR / "product_sales.parquet"
COUNTRY_PARQUET = PROCESSED_DIR / "country_sales.parquet"
SUMMARY_JSON = PROCESSED_DIR / "cleaning_summary.json"

# UI / Design System Theme (Toolfolio Inspired)
THEME = {
    "primary": "#2563EB",         # Professional Royal Blue / Indigo
    "primary_dark": "#1D4ED8",
    "primary_light": "#EFF6FF",
    "accent": "#0D9488",          # Teal accent
    "accent_subtle": "#F0FDFA",
    "background": "#F8FAFC",      # Slate 50 ultra clean background
    "surface": "#FFFFFF",         # Pure white card surface
    "border": "#E2E8F0",          # Slate 200 border
    "border_subtle": "#F1F5F9",
    "text_primary": "#0F172A",    # Slate 900
    "text_secondary": "#475569",  # Slate 600
    "text_muted": "#94A3B8",      # Slate 400
    "success": "#10B981",         # Emerald 500
    "danger": "#EF4444",          # Rose 500
    "warning": "#F59E0B",         # Amber 500
    "chart_palette": [
        "#2563EB", "#0D9488", "#F59E0B", "#8B5CF6", "#EC4899",
        "#06B6D4", "#10B981", "#6366F1", "#F97316", "#64748B"
    ]
}

# Typography
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

# Currency and Locale
CURRENCY_SYMBOL = "£"
DATASET_NAME = "UCI Online Retail II"
DATASET_CITATION = "Chen, D. (2012). Online Retail II. UCI Machine Learning Repository."

