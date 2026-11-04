"""
Shared Page Layout and Sidebar Navigation Component for ForeSight.
Features:
- Dynamic Light Mode & Dark Mode toggle with instant CSS switching
- Sleek modern branding
- Styled navigation pills without circular radio dots
- Fixes Material Icons ligature font (eliminates 'keyboard_double' text bug)
"""

import sys
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.utils.config import THEME_LIGHT, THEME_DARK, APP_NAME, APP_TAGLINE, DATASET_NAME, ASSETS_DIR


def load_custom_css():
    """Injects ForeSight modern SaaS styling with dynamic Light/Dark mode."""
    mode = st.session_state.get("theme_mode", "Light")
    is_dark = mode == "Dark"

    # Base CSS file
    css_file = ASSETS_DIR / "styles.css"
    base_css = ""
    if css_file.exists():
        with open(css_file, "r") as f:
            base_css = f.read()

    # Dynamic theme overrides
    if is_dark:
        theme_css = """
        /* Dark Mode Overrides */
        .stApp {
            background-color: #0B0F19 !important;
            color: #F8FAFC !important;
        }
        header[data-testid="stHeader"] {
            background-color: rgba(11, 15, 25, 0.9) !important;
            border-bottom: 1px solid #1F2937 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #111827 !important;
            border-right: 1px solid #1F2937 !important;
        }
        h1, h2, h3 {
            color: #F8FAFC !important;
        }
        p, span, label {
            color: #CBD5E1 !important;
        }
        div[data-baseweb="input"], div[data-baseweb="select"] > div, div[data-baseweb="input"] input {
            background-color: #1F2937 !important;
            color: #F8FAFC !important;
            border-color: #374151 !important;
        }
        button[kind="secondary"], .stButton > button {
            background-color: #1F2937 !important;
            color: #F8FAFC !important;
            border: 1px solid #374151 !important;
        }
        button[kind="secondary"]:hover, .stButton > button:hover {
            background-color: #374151 !important;
            border-color: #4B5563 !important;
        }
        .js-plotly-plot {
            border-color: #1F2937 !important;
            background: #111827 !important;
        }
        div[data-testid="stDataFrame"] {
            background-color: #111827 !important;
            border-color: #1F2937 !important;
        }
        /* Dark mode navigation pill hover */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
            background-color: #1F2937 !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] {
            background: linear-gradient(90deg, rgba(59, 130, 246, 0.15) 0%, rgba(59, 130, 246, 0.05) 100%) !important;
            border: 1px solid #2563EB !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] p {
            color: #60A5FA !important;
        }
        """
    else:
        theme_css = """
        /* Light Mode Overrides */
        .stApp {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
        }
        header[data-testid="stHeader"] {
            background-color: rgba(248, 250, 252, 0.9) !important;
            border-bottom: 1px solid #E2E8F0 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0 !important;
        }
        h1, h2, h3 {
            color: #0F172A !important;
        }
        p, span, label {
            color: #334155 !important;
        }
        div[data-baseweb="input"], div[data-baseweb="select"] > div, div[data-baseweb="input"] input {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border-color: #CBD5E1 !important;
        }
        button[kind="secondary"], .stButton > button {
            background-color: #FFFFFF !important;
            color: #1E293B !important;
            border: 1px solid #CBD5E1 !important;
        }
        button[kind="secondary"]:hover, .stButton > button:hover {
            background-color: #F1F5F9 !important;
            border-color: #94A3B8 !important;
        }
        .js-plotly-plot {
            border-color: #E2E8F0 !important;
            background: #FFFFFF !important;
        }
        div[data-testid="stDataFrame"] {
            background-color: #FFFFFF !important;
            border-color: #E2E8F0 !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
            background-color: #F1F5F9 !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] {
            background: linear-gradient(90deg, #EFF6FF 0%, #F8FAFC 100%) !important;
            border: 1px solid #BFDBFE !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] p {
            color: #1D4ED8 !important;
        }
        """

    st.markdown(f"<style>{base_css}\n{theme_css}</style>", unsafe_allow_html=True)


def render_sidebar_header():
    """Renders the top branding card in the sidebar."""
    mode = st.session_state.get("theme_mode", "Light")
    is_dark = mode == "Dark"

    header_text_color = "#F8FAFC" if is_dark else "#0F172A"
    tagline_color = "#94A3B8" if is_dark else "#64748B"
    border_color = "#1F2937" if is_dark else "#E2E8F0"

    st.markdown(
        f"""
        <div style="padding-bottom:12px; margin-bottom:14px; border-bottom:1px solid {border_color};">
            <div style="display:flex; align-items:center; gap:12px;">
                <div style="background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); color:white; width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:20px; box-shadow:0 3px 8px rgba(37,99,235,0.35);">
                    ✦
                </div>
                <div>
                    <div style="font-size:20px; font-weight:800; color:{header_text_color}; letter-spacing:-0.03em; font-family:'Plus Jakarta Sans', sans-serif;">{APP_NAME}</div>
                    <div style="font-size:11px; color:{tagline_color}; font-weight:600; font-family:'Inter', sans-serif;">{APP_TAGLINE}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_theme_toggle():
    """Renders a sleek theme toggle in the sidebar."""
    current_mode = st.session_state.get("theme_mode", "Light")
    is_dark = current_mode == "Dark"

    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        if st.button("☀️ Light", use_container_width=True, type="primary" if not is_dark else "secondary", key="theme_light_btn"):
            if is_dark:
                st.session_state["theme_mode"] = "Light"
                st.rerun()
    with col_t2:
        if st.button("🌙 Dark", use_container_width=True, type="primary" if is_dark else "secondary", key="theme_dark_btn"):
            if not is_dark:
                st.session_state["theme_mode"] = "Dark"
                st.rerun()


def render_sidebar_provenance():
    """Renders the dataset provenance card at the bottom of the sidebar."""
    mode = st.session_state.get("theme_mode", "Light")
    is_dark = mode == "Dark"

    card_bg = "#1F2937" if is_dark else "#FFFFFF"
    card_border = "#374151" if is_dark else "#E2E8F0"
    title_color = "#F8FAFC" if is_dark else "#0F172A"
    body_color = "#94A3B8" if is_dark else "#475569"

    st.markdown(
        f"""
        <div style="background:{card_bg}; border:1px solid {card_border}; border-radius:10px; padding:12px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.05); margin-top:8px;">
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <span style="font-size:11px; font-weight:700; color:{title_color}; text-transform:uppercase; letter-spacing:0.05em;">Verified Dataset</span>
                <span style="background:{'#064E3B' if is_dark else '#ECFDF5'}; color:{'#34D399' if is_dark else '#059669'}; padding:2px 7px; border-radius:9999px; font-size:10px; font-weight:700;">Active</span>
            </div>
            <div style="font-size:13px; font-weight:700; color:{title_color}; margin-top:4px;">{DATASET_NAME}</div>
            <div style="font-size:11px; color:{body_color}; margin-top:4px; line-height:1.5;">
                • 1,067,371 genuine transactions<br>
                • Period: Dec 2009 – Dec 2011<br>
                • License: CC BY 4.0 (UCI #502)
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
