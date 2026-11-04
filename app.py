"""
ForeSight — Sales Trend Forecasting & Retail Analytics.
Main Application Entry Point.
"""

import sys
from pathlib import Path
import streamlit as st

# Configure root path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Initialize Theme state
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Light"

from src.utils.config import APP_NAME, APP_TAGLINE
from src.utils.layout import (
    load_custom_css,
    render_sidebar_header,
    render_theme_segmented_control,
    render_sidebar_provenance,
)
from pages.sales_overview import render_sales_overview
from pages.sales_analytics import render_sales_analytics
from pages.product_analytics import render_product_analytics
from pages.geographical_analytics import render_geographical_analytics
from pages.sales_forecasting import render_sales_forecasting


def main():
    st.set_page_config(
        page_title=f"{APP_NAME} — {APP_TAGLINE}",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject global design system & theme variables
    load_custom_css()

    # Redesigned Compact Sidebar
    with st.sidebar:
        render_sidebar_header()

        # Theme Segmented Control
        st.markdown(
            "<p style='font-size:10px; font-weight:700; text-transform:uppercase; color:var(--text-muted, #64748B); letter-spacing:0.06em; margin-bottom:4px;'>Appearance</p>",
            unsafe_allow_html=True,
        )
        render_theme_segmented_control()

        st.markdown("<hr style='border:0; border-top:1px solid var(--border-color, #E2E8F0); margin:12px 0;'>", unsafe_allow_html=True)

        st.markdown(
            "<p style='font-size:10px; font-weight:700; text-transform:uppercase; color:var(--text-muted, #64748B); letter-spacing:0.06em; margin-bottom:4px;'>Navigation</p>",
            unsafe_allow_html=True,
        )

        pages = [
            "Sales Overview",
            "Sales Analytics",
            "Product Analytics",
            "Geographical Analytics",
            "Sales Forecasting",
        ]

        # Material Symbols (Consistent icon library without goofy emojis)
        icons = {
            "Sales Overview": ":material/dashboard:",
            "Sales Analytics": ":material/monitoring:",
            "Product Analytics": ":material/inventory_2:",
            "Geographical Analytics": ":material/public:",
            "Sales Forecasting": ":material/trending_up:",
        }

        selected_page = st.radio(
            "Navigation",
            pages,
            format_func=lambda p: f"{icons.get(p, '')}  {p}",
            label_visibility="collapsed",
            key="active_nav_module",
        )

        st.markdown("<hr style='border:0; border-top:1px solid var(--border-color, #E2E8F0); margin:14px 0;'>", unsafe_allow_html=True)
        render_sidebar_provenance()

    # Route to selected page module
    if selected_page == "Sales Overview":
        render_sales_overview()
    elif selected_page == "Sales Analytics":
        render_sales_analytics()
    elif selected_page == "Product Analytics":
        render_product_analytics()
    elif selected_page == "Geographical Analytics":
        render_geographical_analytics()
    elif selected_page == "Sales Forecasting":
        render_sales_forecasting()


if __name__ == "__main__":
    main()
