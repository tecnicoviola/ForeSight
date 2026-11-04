"""
Module 2: Sales Analytics Page.
Redesigned with Linear / Stripe SaaS visual hierarchy:
- Segmented control time granularity selector (Weekly, Daily, Monthly)
- Peak & trough operational metrics
- Moving-average trend overlays & growth-rate velocity bars
- Year-over-Year comparative benchmarking
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.data.loader import load_daily_sales, load_weekly_sales, load_monthly_sales
from src.analytics.sales_metrics import (
    compute_time_series_growth,
    compute_peak_and_trough_periods,
)
from src.utils.helpers import (
    format_currency,
    format_number,
    format_percentage,
    apply_theme_to_figure,
    render_kpi_card_html,
    render_page_header,
    get_current_theme,
)
from src.utils.config import CURRENCY_SYMBOL, APP_NAME
from src.utils.layout import (
    load_custom_css,
    render_sidebar_header,
    render_theme_segmented_control,
    render_sidebar_provenance,
)


def render_sales_analytics():
    theme = get_current_theme()
    is_dark = theme["mode"] == "dark"

    # Section A: Header
    render_page_header(
        title="Sales Analytics",
        description="Granular historical velocity, seasonal cycles, period-over-period growth rates and operational extremes.",
        badge="Time-Series Analysis",
    )

    df_daily = load_daily_sales()
    df_weekly = load_weekly_sales()
    df_monthly = load_monthly_sales()

    # Section B: Granularity Segmented Control
    col_g1, col_g2 = st.columns([3, 2])
    with col_g1:
        granularity = st.segmented_control(
            "Time Granularity",
            options=["Weekly", "Daily", "Monthly"],
            default="Weekly",
            format_func=lambda x: f"{x} Resolution" if x != "Weekly" else "Weekly Baseline (Primary)",
            key="sa_granularity_seg",
        )
    if not granularity:
        granularity = "Weekly"

    if granularity == "Weekly":
        active_df = compute_time_series_growth(df_weekly, "Revenue")
        date_col = "Week_Start"
        title_prefix = "Weekly"
    elif granularity == "Daily":
        active_df = compute_time_series_growth(df_daily, "Revenue")
        date_col = "Date"
        title_prefix = "Daily"
    else:
        active_df = compute_time_series_growth(df_monthly, "Revenue")
        date_col = "Month_Start"
        title_prefix = "Monthly"

    # Extreme Performance Metrics
    extremes = compute_peak_and_trough_periods(active_df, date_col, metric_col="Revenue", top_n=3)
    highest_record = extremes["peaks"].iloc[0]
    lowest_record = extremes["troughs"].iloc[0]

    st.write("")  # spacing
    # Section C: 4 Equal-Height KPI Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            render_kpi_card_html(
                f"Peak {title_prefix} Revenue",
                format_currency(highest_record["Revenue"]),
                f"On {pd.to_datetime(highest_record[date_col]).strftime('%d %b %Y')}",
                badge="Max",
                badge_type="success",
                accent_bar="#059669",
            ),
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            render_kpi_card_html(
                f"Lowest {title_prefix} Revenue",
                format_currency(lowest_record["Revenue"]),
                f"On {pd.to_datetime(lowest_record[date_col]).strftime('%d %b %Y')}",
                badge="Trough",
                badge_type="warning",
                accent_bar="#D97706",
            ),
            unsafe_allow_html=True,
        )
    with m3:
        avg_revenue = active_df["Revenue"].mean()
        st.markdown(
            render_kpi_card_html(
                f"Mean {title_prefix} Sales",
                format_currency(avg_revenue),
                f"Std: {format_currency(active_df['Revenue'].std())}",
                badge_type="neutral",
                accent_bar="#2563EB",
            ),
            unsafe_allow_html=True,
        )
    with m4:
        avg_growth = active_df["Growth_Pct"].replace([np.inf, -np.inf], np.nan).dropna().mean()
        badge_type = "success" if avg_growth > 0 else "danger"
        accent_color = "#059669" if avg_growth > 0 else "#DC2626"
        st.markdown(
            render_kpi_card_html(
                f"Mean {title_prefix} Growth",
                format_percentage(avg_growth, include_sign=True),
                "Period-over-period velocity",
                badge="Velocity",
                badge_type=badge_type,
                accent_bar=accent_color,
            ),
            unsafe_allow_html=True,
        )

    st.markdown(f"<hr style='border:0; border-top:1px solid {theme['border']}; margin: 24px 0;'>", unsafe_allow_html=True)

    # Section D: Primary Historical Sales Trend & Moving Average
    st.markdown(f"### {title_prefix} Sales Trend & 4-Period Moving Average")
    active_df["MA4"] = active_df["Revenue"].rolling(window=4, min_periods=1).mean()

    fig_sales = go.Figure()
    bar_color = "rgba(59, 130, 246, 0.35)" if is_dark else "rgba(37, 99, 235, 0.4)"
    fig_sales.add_trace(
        go.Bar(
            x=active_df[date_col],
            y=active_df["Revenue"],
            name=f"Actual {title_prefix} Sales",
            marker=dict(color=bar_color, line=dict(color=theme["primary"], width=1), cornerradius=3),
            hovertemplate="<b>Date</b>: %{x|%d %b %Y}<br><b>Sales</b>: " + CURRENCY_SYMBOL + "%{y:,.2f}<extra></extra>",
        )
    )
    fig_sales.add_trace(
        go.Scatter(
            x=active_df[date_col],
            y=active_df["MA4"],
            mode="lines",
            name="4-Period Moving Average",
            line=dict(color=theme["accent"], width=2.5),
            hovertemplate="<b>4-Period MA</b>: " + CURRENCY_SYMBOL + "%{y:,.2f}<extra></extra>",
        )
    )
    apply_theme_to_figure(fig_sales, height=360)
    st.plotly_chart(fig_sales, use_container_width=True)

    # Section E: Period Growth / Decline Rate (%)
    st.markdown("### Period-over-Period Growth Velocity (%)")
    growth_colors = [theme["success"] if g >= 0 else theme["danger"] for g in active_df["Growth_Pct"]]
    
    fig_growth = go.Figure()
    fig_growth.add_trace(
        go.Bar(
            x=active_df[date_col],
            y=active_df["Growth_Pct"],
            marker=dict(color=growth_colors, cornerradius=2),
            hovertemplate="<b>Date</b>: %{x|%d %b %Y}<br><b>Growth</b>: %{y:.2f}%<extra></extra>",
        )
    )
    apply_theme_to_figure(fig_growth, height=270)
    fig_growth.update_layout(yaxis=dict(title="Growth Rate (%)", zeroline=True, zerolinecolor="#64748B"))
    st.plotly_chart(fig_growth, use_container_width=True)

    # Section F: Year-over-Year Comparative Analysis
    st.markdown("### Year-over-Year Monthly Comparative Analysis")
    df_m = df_monthly.copy()
    df_m["Year"] = df_m["Month_Start"].dt.year
    df_m["Month_Num"] = df_m["Month_Start"].dt.month
    df_m["Month_Name"] = df_m["Month_Start"].dt.strftime("%b")

    pivot_yoy = df_m.pivot_table(index="Month_Num", columns="Year", values="Revenue", aggfunc="sum").fillna(0)
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    pivot_yoy.index = [month_labels[i - 1] for i in pivot_yoy.index]

    fig_yoy = go.Figure()
    years = sorted(df_m["Year"].unique())
    year_palette = ["#94A3B8", "#3B82F6", "#14B8A6"] if is_dark else ["#94A3B8", "#2563EB", "#0D9488"]
    for i, yr in enumerate(years):
        if yr in pivot_yoy.columns:
            fig_yoy.add_trace(
                go.Bar(
                    x=pivot_yoy.index,
                    y=pivot_yoy[yr],
                    name=f"Year {yr}",
                    marker_color=year_palette[i % len(year_palette)],
                    marker=dict(cornerradius=3),
                    hovertemplate="<b>" + str(yr) + " %{x}</b><br>Revenue: " + CURRENCY_SYMBOL + "%{y:,.2f}<extra></extra>",
                )
            )

    apply_theme_to_figure(fig_yoy, height=350)
    fig_yoy.update_layout(barmode="group")
    st.plotly_chart(fig_yoy, use_container_width=True)

    # Section G: 2-Column Peak & Lowest Sales Tables
    t1, t2 = st.columns(2)
    with t1:
        st.markdown(f"#### Top 5 Peak {title_prefix} Periods")
        p_table = extremes["peaks"].copy()
        p_table[date_col] = pd.to_datetime(p_table[date_col]).dt.strftime("%d %b %Y")
        p_table["Revenue"] = p_table["Revenue"].apply(lambda v: format_currency(v))
        p_table["Transactions"] = p_table["Transactions"].apply(lambda v: format_number(v))
        p_table["Quantity"] = p_table["Quantity"].apply(lambda v: format_number(v))
        st.dataframe(p_table, hide_index=True, use_container_width=True)

    with t2:
        st.markdown(f"#### Bottom 5 Lowest {title_prefix} Periods")
        t_table = extremes["troughs"].copy()
        t_table[date_col] = pd.to_datetime(t_table[date_col]).dt.strftime("%d %b %Y")
        t_table["Revenue"] = t_table["Revenue"].apply(lambda v: format_currency(v))
        t_table["Transactions"] = t_table["Transactions"].apply(lambda v: format_number(v))
        t_table["Quantity"] = t_table["Quantity"].apply(lambda v: format_number(v))
        st.dataframe(t_table, hide_index=True, use_container_width=True)


if __name__ == "__main__":
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "Light"
    st.set_page_config(
        page_title=f"Sales Analytics — {APP_NAME}",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_custom_css()
    with st.sidebar:
        render_sidebar_header()
        render_theme_segmented_control()
        st.markdown("<hr style='border:0; border-top:1px solid var(--border-color, #E2E8F0); margin:14px 0;'>", unsafe_allow_html=True)
        render_sidebar_provenance()
    render_sales_analytics()
