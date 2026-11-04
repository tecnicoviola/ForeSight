"""
Shared Page Layout, Navigation, and Sidebar Architecture for ForeSight.
Strictly follows the Linear / Stripe design system:
- Compact sidebar width (260px)
- Material symbol navigation (no emojis)
- Compact segmented control theme switcher
- Elegant dataset provenance card
"""

import sys
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.utils.config import APP_NAME, APP_TAGLINE, DATASET_NAME, ASSETS_DIR


def load_custom_css():
    """Injects core stylesheets and theme-specific dynamic variables."""
    mode = st.session_state.get("theme_mode", "Light")
    is_dark = mode == "Dark"

    css_file = ASSETS_DIR / "styles.css"
    base_css = ""
    if css_file.exists():
        with open(css_file, "r") as f:
            base_css = f.read()

    if is_dark:
        theme_css = """
        /* Dark Theme Variables */
        :root {
            --bg-canvas: #090D16;
            --bg-surface: #111726;
            --bg-surface-elevated: #182238;
            --border-color: #1E293B;
            --border-subtle: #162032;
            --text-primary: #F8FAFC;
            --text-secondary: #CBD5E1;
            --text-muted: #94A3B8;
            --primary-accent: #3B82F6;
            --nav-active-bg: #182238;
            --nav-active-border: #3B82F6;
            --nav-active-text: #60A5FA;
            --nav-hover-bg: #141C2E;
        }
        .stApp {
            background-color: #090D16 !important;
            color: #F8FAFC !important;
        }
        header[data-testid="stHeader"] {
            background-color: rgba(9, 13, 22, 0.85) !important;
            border-bottom: 1px solid #1E293B !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #0D121F !important;
            border-right: 1px solid #1E293B !important;
        }
        h1, h2, h3, h4 {
            color: #F8FAFC !important;
        }
        p, span, label {
            color: #CBD5E1 !important;
        }
        div[data-baseweb="input"], div[data-baseweb="select"] > div, div[data-baseweb="input"] input {
            background-color: #111726 !important;
            color: #F8FAFC !important;
            border-color: #1E293B !important;
        }
        button[kind="secondary"], .stButton > button {
            background-color: #111726 !important;
            color: #F8FAFC !important;
            border: 1px solid #1E293B !important;
        }
        button[kind="secondary"]:hover, .stButton > button:hover {
            background-color: #182238 !important;
            border-color: #374151 !important;
        }
        .js-plotly-plot {
            border-color: #1E293B !important;
            background: #111726 !important;
        }
        div[data-testid="stDataFrame"] {
            background-color: #111726 !important;
            border-color: #1E293B !important;
        }
        """
    else:
        theme_css = """
        /* Light Theme Variables */
        :root {
            --bg-canvas: #F8FAFC;
            --bg-surface: #FFFFFF;
            --bg-surface-elevated: #F1F5F9;
            --border-color: #E2E8F0;
            --border-subtle: #F1F5F9;
            --text-primary: #0F172A;
            --text-secondary: #334155;
            --text-muted: #64748B;
            --primary-accent: #2563EB;
            --nav-active-bg: #EFF6FF;
            --nav-active-border: #BFDBFE;
            --nav-active-text: #1D4ED8;
            --nav-hover-bg: #F8FAFC;
        }
        .stApp {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
        }
        header[data-testid="stHeader"] {
            background-color: rgba(248, 250, 252, 0.85) !important;
            border-bottom: 1px solid #E2E8F0 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0 !important;
        }
        h1, h2, h3, h4 {
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
            background-color: #F8FAFC !important;
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
        """

    st.markdown(f"<style>{base_css}\n{theme_css}</style>", unsafe_allow_html=True)


def render_sidebar_header():
    """Renders sleek top logo and branding in the sidebar."""
    mode = st.session_state.get("theme_mode", "Light")
    is_dark = mode == "Dark"

    header_color = "#F8FAFC" if is_dark else "#0F172A"
    tagline_color = "#94A3B8" if is_dark else "#64748B"
    border_color = "#1E293B" if is_dark else "#E2E8F0"

    st.markdown(
        f"""
        <div style="padding-bottom:12px; margin-bottom:12px; border-bottom:1px solid {border_color};">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="background:linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); color:white; width:34px; height:34px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:17px; box-shadow:0 2px 5px rgba(37,99,235,0.25);">
                    ✦
                </div>
                <div>
                    <div style="font-size:18px; font-weight:800; color:{header_color}; letter-spacing:-0.03em; font-family:'Plus Jakarta Sans', sans-serif; line-height:1.2;">{APP_NAME}</div>
                    <div style="font-size:10.5px; color:{tagline_color}; font-weight:600; font-family:'Inter', sans-serif;">{APP_TAGLINE}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_theme_segmented_control():
    """Renders a compact, professional segmented control for Light/Dark mode."""
    current_mode = st.session_state.get("theme_mode", "Light")
    
    selected = st.segmented_control(
        "Appearance",
        options=["Light", "Dark"],
        default=current_mode,
        format_func=lambda x: "☀️ Light" if x == "Light" else "🌙 Dark",
        label_visibility="collapsed",
        key="fs_theme_seg_control"
    )

    if selected and selected != current_mode:
        st.session_state["theme_mode"] = selected
        st.rerun()


def render_sidebar_provenance():
    """Renders a compact dataset information card at the bottom of the sidebar."""
    mode = st.session_state.get("theme_mode", "Light")
    is_dark = mode == "Dark"

    card_bg = "#111726" if is_dark else "#F8FAFC"
    card_border = "#1E293B" if is_dark else "#E2E8F0"
    title_color = "#F8FAFC" if is_dark else "#0F172A"
    body_color = "#94A3B8" if is_dark else "#64748B"

    st.markdown(
        f"""
        <div style="background:{card_bg}; border:1px solid {card_border}; border-radius:8px; padding:10px 12px; margin-top:10px;">
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <span style="font-size:10px; font-weight:700; color:{title_color}; text-transform:uppercase; letter-spacing:0.05em;">Dataset Provenance</span>
                <span style="background:{'#064E3B' if is_dark else '#ECFDF5'}; color:{'#34D399' if is_dark else '#059669'}; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:700;">Verified</span>
            </div>
            <div style="font-size:12px; font-weight:700; color:{title_color}; margin-top:3px;">{DATASET_NAME}</div>
            <div style="font-size:11px; color:{body_color}; margin-top:4px; line-height:1.45;">
                • ~1.07M original transactions<br>
                • Dec 2009 – Dec 2011<br>
                • CC BY 4.0 license (UCI #502)
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
