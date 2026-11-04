"""
Formatting, Component Builders, and Plotly Styling Utilities for ForeSight.
Follows Linear / Stripe design principles: crisp contrast, equal heights, tabular numbers, subtle micro-interactions.
"""

from typing import Dict, Any, Optional
import streamlit as st
import plotly.graph_objects as go
from src.utils.config import THEME_LIGHT, THEME_DARK, CURRENCY_SYMBOL, FONT_FAMILY


def get_current_theme() -> Dict[str, Any]:
    """Retrieves the active design tokens based on session state."""
    mode = st.session_state.get("theme_mode", "Light")
    return THEME_DARK if mode == "Dark" else THEME_LIGHT


def format_currency(val: float, precision: int = 2, compact: bool = False) -> str:
    """Formats numeric values into British Pound currency strings."""
    if val is None or val != val:
        return f"{CURRENCY_SYMBOL}0.00"
    
    if compact:
        abs_val = abs(val)
        sign = "-" if val < 0 else ""
        if abs_val >= 1_000_000:
            return f"{sign}{CURRENCY_SYMBOL}{abs_val / 1_000_000:.2f}M"
        elif abs_val >= 1_000:
            return f"{sign}{CURRENCY_SYMBOL}{abs_val / 1_000:.1f}k"
        else:
            return f"{sign}{CURRENCY_SYMBOL}{abs_val:,.{precision}f}"
    return f"{CURRENCY_SYMBOL}{val:,.{precision}f}"


def format_number(val: int | float, compact: bool = False) -> str:
    """Formats numeric counts with comma or compact suffixes."""
    if val is None or val != val:
        return "0"
    if compact:
        abs_val = abs(val)
        sign = "-" if val < 0 else ""
        if abs_val >= 1_000_000:
            return f"{sign}{abs_val / 1_000_000:.2f}M"
        elif abs_val >= 1_000:
            return f"{sign}{abs_val / 1_000:.1f}k"
        else:
            return f"{sign}{abs_val:,.0f}"
    return f"{val:,.0f}"


def format_percentage(val: float, include_sign: bool = False) -> str:
    """Formats float ratio or percentage value."""
    if val is None or val != val:
        return "0.0%"
    prefix = "+" if include_sign and val > 0 else ""
    return f"{prefix}{val:.2f}%"


def apply_theme_to_figure(fig: go.Figure, title: Optional[str] = None, height: int = 370) -> go.Figure:
    """Applies unified Linear/Stripe-inspired SaaS styling to a Plotly figure."""
    theme = get_current_theme()
    is_dark = theme["mode"] == "dark"

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(family=FONT_FAMILY, size=14, color=theme["text_primary"]),
            x=0.01,
            y=0.96,
        ) if title else None,
        font=dict(family=FONT_FAMILY, color=theme["text_secondary"], size=12),
        paper_bgcolor=theme["surface"],
        plot_bgcolor=theme["surface"],
        height=height,
        margin=dict(l=45, r=30, t=45 if title else 25, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family=FONT_FAMILY, size=11, color=theme["text_secondary"]),
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor=theme["border_subtle"],
            linecolor=theme["border"],
            zeroline=False,
            tickfont=dict(family=FONT_FAMILY, size=11, color=theme["text_muted"]),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=theme["border_subtle"],
            linecolor=theme["border"],
            zeroline=False,
            tickfont=dict(family=FONT_FAMILY, size=11, color=theme["text_muted"]),
        ),
        hoverlabel=dict(
            bgcolor="#0F172A" if not is_dark else "#182238",
            font_size=12,
            font_family=FONT_FAMILY,
            font_color="#FFFFFF"
        ),
    )
    return fig


def render_page_header(title: str, description: str, badge: Optional[str] = None):
    """Renders a unified, premium SaaS application header across all pages."""
    theme = get_current_theme()
    is_dark = theme["mode"] == "dark"

    badge_html = (
        f'<span style="background:{"#1E293B" if is_dark else "#EFF6FF"}; color:{"#60A5FA" if is_dark else "#2563EB"}; border:1px solid {"#2563EB" if is_dark else "#BFDBFE"}; padding:3px 10px; border-radius:9999px; font-size:11px; font-weight:700; letter-spacing:0.02em;">{badge}</span>'
        if badge else ""
    )

    header_html = (
        f'<div class="fs-page-header" style="margin-bottom:20px; padding-bottom:14px; border-bottom:1px solid {theme["border"]}; display:flex; justify-content:space-between; align-items:flex-end;">'
        f'<div>'
        f'<div style="display:flex; align-items:center; gap:10px;">'
        f'<h1 style="margin:0; font-size:24px; font-weight:800; color:{theme["text_primary"]}; letter-spacing:-0.03em; font-family:\'Plus Jakarta Sans\', sans-serif;">{title}</h1>'
        f'{badge_html}'
        f'</div>'
        f'<div style="font-size:13px; color:{theme["text_muted"]}; margin-top:4px; font-weight:500;">{description}</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)


def render_kpi_card_html(
    title: str,
    value: str,
    subtitle: Optional[str] = None,
    badge: Optional[str] = None,
    badge_type: str = "neutral",
    accent_bar: str = "#2563EB"
) -> str:
    """
    Renders an equal-height, tabular-numeral, premium SaaS KPI card.
    100% unindented string prevents any Markdown code-block parsing errors.
    """
    theme = get_current_theme()
    is_dark = theme["mode"] == "dark"

    badge_colors_light = {
        "success": ("#ECFDF5", "#059669"),
        "danger": ("#FEF2F2", "#DC2626"),
        "warning": ("#FFFBEB", "#D97706"),
        "primary": ("#EFF6FF", "#2563EB"),
        "neutral": ("#F1F5F9", "#475569"),
    }
    badge_colors_dark = {
        "success": ("#064E3B", "#34D399"),
        "danger": ("#7F1D1D", "#F87171"),
        "warning": ("#78350F", "#FBBF24"),
        "primary": ("#1E3A8A", "#60A5FA"),
        "neutral": ("#1F2937", "#CBD5E1"),
    }

    badge_palette = badge_colors_dark if is_dark else badge_colors_light
    bg, fg = badge_palette.get(badge_type, badge_palette["neutral"])
    
    badge_span = (
        f'<span style="background:{bg}; color:{fg}; padding:2px 8px; border-radius:6px; font-size:11px; font-weight:700; letter-spacing:0.02em;">{badge}</span>'
        if badge else ""
    )
    
    subtitle_div = (
        f'<div style="font-size:12px; color:{theme["text_muted"]}; margin-top:4px; font-weight:500; line-height:1.4;">{subtitle}</div>'
        if subtitle else ""
    )

    card_bg = theme["surface"]
    card_border = theme["border"]
    text_primary = theme["text_primary"]
    text_label = theme["text_muted"]
    shadow = "0 1px 2px rgba(0,0,0,0.2)" if is_dark else "0 1px 3px rgba(15,23,42,0.04)"

    raw_html = (
        f'<div class="foresight-kpi-card" style="background:{card_bg}; border:1px solid {card_border}; border-top:2.5px solid {accent_bar}; border-radius:10px; padding:16px 18px; box-shadow:{shadow}; min-height:116px; display:flex; flex-direction:column; justify-content:space-between; animation:fadeInUp 0.3s ease-out;">'
        f'<div style="display:flex; justify-content:space-between; align-items:center;">'
        f'<span style="font-size:11px; font-weight:700; color:{text_label}; text-transform:uppercase; letter-spacing:0.06em;">{title}</span>'
        f'{badge_span}'
        f'</div>'
        f'<div style="font-size:clamp(19px, 1.7vw, 25px); font-weight:800; color:{text_primary}; margin-top:6px; letter-spacing:-0.03em; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-variant-numeric:tabular-nums; font-family:\'Plus Jakarta Sans\', sans-serif;">'
        f'{value}'
        f'</div>'
        f'{subtitle_div}'
        f'</div>'
    )
    return raw_html
