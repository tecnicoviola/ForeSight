"""
Formatting, UI card, and Plotly styling helpers for ForeSight.
Dynamically respects Light / Dark mode settings with animations and high-contrast typography.
"""

from typing import Dict, Any, Optional
import streamlit as st
import plotly.graph_objects as go
from src.utils.config import THEME_LIGHT, THEME_DARK, CURRENCY_SYMBOL, FONT_FAMILY


def get_current_theme() -> Dict[str, Any]:
    """Returns the active theme palette based on session state."""
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


def apply_theme_to_figure(fig: go.Figure, title: Optional[str] = None, height: int = 380) -> go.Figure:
    """Applies dynamic Light or Dark mode styling to a Plotly figure."""
    theme = get_current_theme()
    is_dark = theme["mode"] == "dark"

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(family=FONT_FAMILY, size=15, color=theme["text_primary"]),
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
            bgcolor="#0F172A" if not is_dark else "#1F2937",
            font_size=12,
            font_family=FONT_FAMILY,
            font_color="#FFFFFF"
        ),
    )
    return fig


def render_kpi_card_html(
    title: str,
    value: str,
    subtitle: Optional[str] = None,
    badge: Optional[str] = None,
    badge_type: str = "neutral",
    accent_bar: str = "#2563EB"
) -> str:
    """
    Renders a modern, animated, unindented HTML KPI card.
    Prevents text-wrapping on large numbers and adapts to Light/Dark modes.
    """
    theme = get_current_theme()
    is_dark = theme["mode"] == "dark"

    badge_colors_light = {
        "success": ("#ECFDF5", "#059669"),
        "danger": ("#FEF2F2", "#DC2626"),
        "warning": ("#FFFBEB", "#D97706"),
        "primary": ("#EFF6FF", "#2563EB"),
        "neutral": ("#F1F5F9", "#334155"),
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
        f'<span style="background:{bg}; color:{fg}; padding:3px 8px; border-radius:9999px; font-size:11px; font-weight:700; letter-spacing:0.02em;">{badge}</span>'
        if badge else ""
    )
    
    subtitle_div = (
        f'<div style="font-size:12px; color:{theme["text_muted"]}; margin-top:6px; font-weight:500;">{subtitle}</div>'
        if subtitle else ""
    )

    card_bg = theme["surface"]
    card_border = theme["border"]
    text_primary = theme["text_primary"]
    text_secondary = theme["text_secondary"]
    shadow = "0 4px 6px -1px rgba(0, 0, 0, 0.3)" if is_dark else "0 1px 3px rgba(15,23,42,0.06)"

    raw_html = (
        f'<div class="foresight-kpi-card" style="background:{card_bg}; border:1px solid {card_border}; border-top:3px solid {accent_bar}; border-radius:12px; padding:18px 20px; box-shadow:{shadow}; margin-bottom:14px; min-height:118px; display:flex; flex-direction:column; justify-content:space-between; animation:fadeInUp 0.35s ease-out;">'
        f'<div style="display:flex; justify-content:space-between; align-items:center;">'
        f'<span style="font-size:11px; font-weight:700; color:{text_secondary}; text-transform:uppercase; letter-spacing:0.06em;">{title}</span>'
        f'{badge_span}'
        f'</div>'
        f'<div style="font-size:clamp(20px, 1.8vw, 26px); font-weight:800; color:{text_primary}; margin-top:8px; letter-spacing:-0.03em; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-family:\'Plus Jakarta Sans\', sans-serif;">'
        f'{value}'
        f'</div>'
        f'{subtitle_div}'
        f'</div>'
    )
    return raw_html
