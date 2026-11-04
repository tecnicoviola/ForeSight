"""
Configuration and Theme Palette for ForeSight.
Supports both Light and Dark Modes with high-contrast typography and sleek modern SaaS colors.
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

# High-Contrast Light Theme Palette
THEME_LIGHT = {
    "mode": "light",
    "primary": "#2563EB",         # Electric Royal Blue
    "primary_hover": "#1D4ED8",
    "primary_light": "#EFF6FF",
    "accent": "#0D9488",          # Modern Teal
    "background": "#F8FAFC",      # Slate 50 clean background
    "surface": "#FFFFFF",         # Pure white card surface
    "surface_subtle": "#F1F5F9",
    "border": "#E2E8F0",          # Crisp Slate 200 border
    "border_subtle": "#F1F5F9",
    "text_primary": "#0F172A",    # Rich Dark Slate 900 (High contrast)
    "text_secondary": "#334155",  # Slate 700 (Legible)
    "text_muted": "#64748B",      # Slate 500 (Clear)
    "success": "#10B981",
    "danger": "#EF4444",
    "warning": "#F59E0B",
    "chart_palette": [
        "#2563EB", "#0D9488", "#F59E0B", "#8B5CF6", "#EC4899",
        "#06B6D4", "#10B981", "#6366F1", "#F97316", "#64748B"
    ]
}

# High-Contrast Dark Theme Palette (Linear / Raycast inspired)
THEME_DARK = {
    "mode": "dark",
    "primary": "#3B82F6",         # Bright Blue
    "primary_hover": "#60A5FA",
    "primary_light": "#1E293B",
    "accent": "#14B8A6",          # Teal
    "background": "#0B0F19",      # Deep Midnight Black
    "surface": "#111827",         # Deep Slate Gray
    "surface_subtle": "#1F2937",
    "border": "#374151",          # Slate 700 border
    "border_subtle": "#1F2937",
    "text_primary": "#F8FAFC",    # Pure White 50
    "text_secondary": "#E2E8F0",  # Slate 200
    "text_muted": "#94A3B8",      # Slate 400
    "success": "#34D399",
    "danger": "#F87171",
    "warning": "#FBBF24",
    "chart_palette": [
        "#3B82F6", "#14B8A6", "#FBBF24", "#A78BFA", "#F472B6",
        "#22D3EE", "#34D399", "#818CF8", "#FB923C", "#94A3B8"
    ]
}

# Active default fallback
THEME = THEME_LIGHT

# Typography: Modern Google Font Pair
FONT_FAMILY = "'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif"

# Branding Constants
CURRENCY_SYMBOL = "£"
APP_NAME = "ForeSight"
APP_TAGLINE = "Sales Trend Forecasting & Retail Analytics"
DATASET_NAME = "UCI Online Retail II"
DATASET_CITATION = "Chen, D. (2012). Online Retail II. UCI Machine Learning Repository."
