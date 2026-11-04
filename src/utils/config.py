"""
Design System Configuration and Design Tokens for ForeSight.
Premium Enterprise Analytics SaaS aesthetic inspired by Linear, Stripe, and Vercel.
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

# Design Tokens: Light Mode (Sophisticated Neutral Minimalist SaaS)
THEME_LIGHT = {
    "mode": "light",
    "primary": "#2563EB",            # Premium Blue
    "primary_hover": "#1D4ED8",
    "primary_subtle": "#EFF6FF",     # Soft Blue Fill
    "primary_border": "#BFDBFE",
    "accent": "#0D9488",             # Deep Teal
    "background": "#F8FAFC",         # Slate 50 Neutral Canvas
    "surface": "#FFFFFF",            # Crisp White Card Surface
    "surface_elevated": "#F1F5F9",   # Slate 100
    "border": "#E2E8F0",             # Slate 200 Card Border
    "border_subtle": "#F1F5F9",      # Slate 100 Divider
    "text_primary": "#0F172A",       # Slate 900 (High-Contrast Header)
    "text_secondary": "#334155",     # Slate 700 (Body & Labels)
    "text_muted": "#64748B",         # Slate 500 (Subtext)
    "success": "#059669",            # Emerald
    "success_subtle": "#ECFDF5",
    "danger": "#DC2626",             # Crimson
    "danger_subtle": "#FEF2F2",
    "warning": "#D97706",            # Amber
    "warning_subtle": "#FFFBEB",
    "chart_palette": [
        "#2563EB", "#0D9488", "#F59E0B", "#8B5CF6", "#EC4899",
        "#06B6D4", "#10B981", "#6366F1", "#F97316", "#64748B"
    ]
}

# Design Tokens: Dark Mode (Obsidian / Linear-inspired Deep Space)
THEME_DARK = {
    "mode": "dark",
    "primary": "#3B82F6",            # Bright Linear Blue
    "primary_hover": "#60A5FA",
    "primary_subtle": "#1E293B",     # Deep Slate Fill
    "primary_border": "#2563EB",
    "accent": "#14B8A6",             # Neon Teal
    "background": "#090D16",         # Deep Obsidian Background
    "surface": "#111726",            # Dark Slate Card Surface
    "surface_elevated": "#182238",   # Elevated Slate
    "border": "#1E293B",             # Slate 800 Border
    "border_subtle": "#162032",      # Slate 900 Divider
    "text_primary": "#F8FAFC",       # Slate 50 Header
    "text_secondary": "#CBD5E1",     # Slate 300 Body
    "text_muted": "#94A3B8",         # Slate 400 Subtext
    "success": "#10B981",            # Emerald
    "success_subtle": "#064E3B",
    "danger": "#EF4444",             # Red
    "danger_subtle": "#7F1D1D",
    "warning": "#F59E0B",            # Amber
    "warning_subtle": "#78350F",
    "chart_palette": [
        "#3B82F6", "#14B8A6", "#FBBF24", "#A78BFA", "#F472B6",
        "#22D3EE", "#34D399", "#818CF8", "#FB923C", "#94A3B8"
    ]
}

# Default Active Palette
THEME = THEME_LIGHT

# Typography System
FONT_FAMILY = "'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

# Application Metadata
CURRENCY_SYMBOL = "£"
APP_NAME = "ForeSight"
APP_TAGLINE = "Sales Trend Forecasting & Retail Analytics"
DATASET_NAME = "UCI Online Retail II"
DATASET_CITATION = "Chen, D. (2012). Online Retail II. UCI Machine Learning Repository."
