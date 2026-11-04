"""
SalesPulse — Sales Trend Forecasting & Retail Analytics.
Main Application Entry Point.
"""

import sys
from pathlib import Path
import streamlit as st

# Configure root path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.utils.config import THEME, DATASET_NAME, DATASET_CITATION, ASSETS_DIR
from pages.sales_overview import render_sales_overview
from pages.sales_analytics import render_sales_analytics
from pages.product_analytics import render_product_analytics
from pages.geographical_analytics import render_geographical_analytics
from pages.sales_forecasting import render_sales_forecasting


def load_custom_css():
    """Injects Toolfolio-inspired custom styling."""
    css_file = ASSETS_DIR / "styles.css"
    if css_file.exists():
        with open(css_file, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="SalesPulse — Retail Analytics & Forecasting",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    load_custom_css()

    # Sidebar Header & Branding
    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding-bottom:14px; margin-bottom:14px; border-bottom:1px solid #E2E8F0;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="background:{THEME['primary']}; color:white; width:34px; height:34px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:18px;">
                        ⚡
                    </div>
                    <div>
                        <div style="font-size:18px; font-weight:700; color:{THEME['text_primary']}; letter-spacing:-0.03em;">SalesPulse</div>
                        <div style="font-size:11px; color:{THEME['text_muted']}; font-weight:500;">Retail Analytics & Forecasting</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<p style='font-size:11px; font-weight:600; text-transform:uppercase; color:#94A3B8; letter-spacing:0.05em; margin-bottom:6px;'>Navigation</p>", unsafe_allow_html=True)

        pages = [
            "Sales Overview",
            "Sales Analytics",
            "Product Analytics",
            "Geographical Analytics",
            "Sales Forecasting",
        ]

        icons = {
            "Sales Overview": "📊",
            "Sales Analytics": "📉",
            "Product Analytics": "📦",
            "Geographical Analytics": "🌍",
            "Sales Forecasting": "🔮",
        }

        # Page selector
        selected_page = st.radio(
            "Go to",
            pages,
            format_func=lambda p: f"{icons.get(p, '•')}  {p}",
            label_visibility="collapsed",
        )

        st.markdown("<hr style='border:0; border-top:1px solid #E2E8F0; margin:20px 0;'>", unsafe_allow_html=True)

        # Dataset Provenance Card
        st.markdown(
            f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:12px 14px;">
                <div style="font-size:11px; font-weight:700; color:{THEME['text_secondary']}; text-transform:uppercase; letter-spacing:0.04em;">Verified Dataset</div>
                <div style="font-size:13px; font-weight:600; color:{THEME['text_primary']}; margin-top:2px;">{DATASET_NAME}</div>
                <div style="font-size:11px; color:{THEME['text_muted']}; margin-top:4px;">
                    1,067,371 genuine transactions<br>
                    Period: Dec 2009 – Dec 2011<br>
                    License: CC BY 4.0
                </div>
            </div>
            <div style="margin-top:16px; font-size:11px; color:#94A3B8; line-height:1.4;">
                Academic Project built with Streamlit, Plotly, Scikit-learn & Pandas.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Route to selected page
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
