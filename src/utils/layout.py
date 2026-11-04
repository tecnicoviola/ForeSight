"""
Shared Page Layout and Sidebar Navigation Component for ForeSight.
Ensures consistent branding, styling, and navigation across all entry points.
"""

import sys
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.utils.config import THEME, APP_NAME, APP_TAGLINE, DATASET_NAME, ASSETS_DIR


def load_custom_css():
    """Injects ForeSight modern SaaS custom styling."""
    css_file = ASSETS_DIR / "styles.css"
    if css_file.exists():
        with open(css_file, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_sidebar_header():
    """Renders the top branding card in the sidebar."""
    st.markdown(
        f"""
        <div style="padding-bottom:14px; margin-bottom:16px; border-bottom:1px solid #E2E8F0;">
            <div style="display:flex; align-items:center; gap:12px;">
                <div style="background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); color:white; width:38px; height:38px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:18px; box-shadow:0 2px 6px rgba(37,99,235,0.3);">
                    ✦
                </div>
                <div>
                    <div style="font-size:19px; font-weight:800; color:{THEME['text_primary']}; letter-spacing:-0.03em; font-family:'Plus Jakarta Sans', sans-serif;">{APP_NAME}</div>
                    <div style="font-size:11px; color:{THEME['text_muted']}; font-weight:500; font-family:'Inter', sans-serif;">{APP_TAGLINE}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_provenance():
    """Renders the dataset provenance card at the bottom of the sidebar."""
    st.markdown(
        f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:12px 14px; box-shadow:0 1px 2px rgba(15,23,42,0.04);">
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <span style="font-size:11px; font-weight:700; color:{THEME['text_secondary']}; text-transform:uppercase; letter-spacing:0.05em;">Verified Dataset</span>
                <span style="background:#ECFDF5; color:#059669; padding:2px 7px; border-radius:9999px; font-size:10px; font-weight:700;">Active</span>
            </div>
            <div style="font-size:13px; font-weight:700; color:{THEME['text_primary']}; margin-top:4px;">{DATASET_NAME}</div>
            <div style="font-size:11px; color:{THEME['text_muted']}; margin-top:4px; line-height:1.5;">
                • 1,067,371 genuine transactions<br>
                • Period: Dec 2009 – Dec 2011<br>
                • License: CC BY 4.0 (UCI #502)
            </div>
        </div>
        <div style="margin-top:14px; font-size:11px; color:#94A3B8; line-height:1.4;">
            Academic ML & Analytics Platform.<br>Built with Streamlit, Plotly & Scikit-learn.
        </div>
        """,
        unsafe_allow_html=True,
    )
