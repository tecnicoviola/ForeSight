"""
Formatting, UI card, and Plotly styling helpers for SalesPulse.
"""

from typing import Dict, Any, Optional
import plotly.graph_objects as go
from src.utils.config import THEME, CURRENCY_SYMBOL, FONT_FAMILY


def format_currency(val: float, precision: int = 2, compact: bool = False) -> str:
    """Formats numeric values into British Pound currency strings."""
    if val is None or val != val:  # check NaN
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


def apply_theme_to_figure(fig: go.Figure, title: Optional[str] = None, height: int = 400) -> go.Figure:
    """Applies modern minimal Toolfolio-inspired styling to a Plotly figure."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(family=FONT_FAMILY, size=15, color=THEME["text_primary"]),
            x=0.01,
            y=0.96,
        ) if title else None,
        font=dict(family=FONT_FAMILY, color=THEME["text_secondary"], size=12),
        paper_bgcolor=THEME["surface"],
        plot_bgcolor=THEME["surface"],
        height=height,
        margin=dict(l=40, r=30, t=50 if title else 20, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=THEME["text_secondary"]),
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor=THEME["border_subtle"],
            linecolor=THEME["border"],
            zeroline=False,
            tickfont=dict(size=11, color=THEME["text_muted"]),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=THEME["border_subtle"],
            linecolor=THEME["border"],
            zeroline=False,
            tickfont=dict(size=11, color=THEME["text_muted"]),
        ),
        hoverlabel=dict(
            bgcolor=THEME["text_primary"],
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
    badge_type: str = "neutral"
) -> str:
    """Renders a modern minimal KPI card HTML snippet."""
    badge_colors = {
        "success": ("#ECFDF5", "#059669"),
        "danger": ("#FEF2F2", "#DC2626"),
        "warning": ("#FFFBEB", "#D97706"),
        "primary": ("#EFF6FF", "#2563EB"),
        "neutral": ("#F1F5F9", "#475569"),
    }
    bg, fg = badge_colors.get(badge_type, badge_colors["neutral"])
    badge_html = (
        f'<span style="background:{bg}; color:{fg}; padding:2px 8px; border-radius:9999px; font-size:11px; font-weight:600; margin-left:8px;">{badge}</span>'
        if badge
        else ""
    )
    subtitle_html = (
        f'<div style="font-size:12px; color:{THEME["text_muted"]}; margin-top:4px;">{subtitle}</div>'
        if subtitle
        else ""
    )

    return f"""
    <div style="
        background: {THEME['surface']};
        border: 1px solid {THEME['border']};
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 12px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    ">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; font-weight:600; color:{THEME['text_secondary']}; text-transform:uppercase; letter-spacing:0.05em;">{title}</span>
            {badge_html}
        </div>
        <div style="font-size:26px; font-weight:700; color:{THEME['text_primary']}; margin-top:8px; letter-spacing:-0.02em;">
            {value}
        </div>
        {subtitle_html}
    </div>
    """

