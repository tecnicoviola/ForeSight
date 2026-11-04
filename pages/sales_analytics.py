"""
Module 2: Sales Analytics Page.
Granular multi-frequency sales trend analysis across Daily, Weekly, and Monthly time horizons.
Includes growth/decline rate tracking, peak/trough detection, and year-over-year performance benchmarking.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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
)
from src.utils.config import THEME, CURRENCY_SYMBOL, APP_NAME
from src.utils.layout import load_custom_css, render_sidebar_header, render_sidebar_provenance


def render_sales_analytics():
    st.markdown("## Sales Analytics & Time-Series Dynamics")
    st.markdown(
        "<p style='color:#64748B; font-size:14px; margin-top:-6px; margin-bottom:22px;'>"
        "Multi-frequency historical examination of retail velocity, seasonal surges, period-over-period growth rates, and operational extremes."
        "</p>",
        unsafe_allow_html=True,
    )

    df_daily = load_daily_sales()
    df_weekly = load_weekly_sales()
    df_monthly = load_monthly_sales()

    # Time Granularity Selector
    tab_granularity = st.radio(
        "Select Time Granularity",
        ["Weekly Cadence (Primary Forecast Baseline)", "Daily Resolution", "Monthly Overview"],
        horizontal=True,
        key="analytics_granularity",
    )

    if "Weekly" in tab_granularity:
        active_df = compute_time_series_growth(df_weekly, "Revenue")
        date_col = "Week_Start"
        title_prefix = "Weekly"
    elif "Daily" in tab_granularity:
        active_df = compute_time_series_growth(df_daily, "Revenue")
        date_col = "Date"
        title_prefix = "Daily"
    else:
        active_df = compute_time_series_growth(df_monthly, "Revenue")
        date_col = "Month_Start"
        title_prefix = "Monthly"

    # Peak & Trough Metrics
    extremes = compute_peak_and_trough_periods(active_df, date_col, metric_col="Revenue", top_n=3)
    highest_record = extremes["peaks"].iloc[0]
    lowest_record = extremes["troughs"].iloc[0]

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            render_kpi_card_html(
                f"Peak {title_prefix} Revenue",
                format_currency(highest_record["Revenue"]),
                f"Recorded on {pd.to_datetime(highest_record[date_col]).strftime('%d %b %Y')}",
                badge="All-Time High",
                badge_type="success",
            ),
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            render_kpi_card_html(
                f"Lowest {title_prefix} Revenue",
                format_currency(lowest_record["Revenue"]),
                f"Recorded on {pd.to_datetime(lowest_record[date_col]).strftime('%d %b %Y')}",
                badge="Trough",
                badge_type="warning",
            ),
            unsafe_allow_html=True,
        )
    with m3:
        avg_revenue = active_df["Revenue"].mean()
        st.markdown(
            render_kpi_card_html(
                f"Mean {title_prefix} Revenue",
                format_currency(avg_revenue),
                f"Std Dev: {format_currency(active_df['Revenue'].std())}",
                badge_type="neutral",
            ),
            unsafe_allow_html=True,
        )
    with m4:
        avg_growth = active_df["Growth_Pct"].replace([np.inf, -np.inf], np.nan).dropna().mean()
        badge_type = "success" if avg_growth > 0 else "danger"
        st.markdown(
            render_kpi_card_html(
                f"Mean {title_prefix} Growth",
                format_percentage(avg_growth, include_sign=True),
                "Period-over-period average",
                badge="Velocity",
                badge_type=badge_type,
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border:0; border-top:1px solid #E2E8F0; margin: 20px 0;'>", unsafe_allow_html=True)

    # Primary Interactive Chart: Revenue with 4-period moving average
    st.markdown(f"### {title_prefix} Historical Sales Trend & Moving Average")
    active_df["MA4"] = active_df["Revenue"].rolling(window=4, min_periods=1).mean()

    fig_sales = go.Figure()
    fig_sales.add_trace(
        go.Bar(
            x=active_df[date_col],
            y=active_df["Revenue"],
            name=f"Actual {title_prefix} Revenue",
            marker=dict(color="rgba(37, 99, 235, 0.45)", line=dict(color=THEME["primary"], width=1)),
            hovertemplate="<b>Date</b>: %{x|%d %b %Y}<br><b>Revenue</b>: " + CURRENCY_SYMBOL + "%{y:,.2f}<extra></extra>",
        )
    )
    fig_sales.add_trace(
        go.Scatter(
            x=active_df[date_col],
            y=active_df["MA4"],
            mode="lines",
            name="4-Period Rolling Mean",
            line=dict(color=THEME["accent"], width=2.5),
            hovertemplate="<b>4-Period MA</b>: " + CURRENCY_SYMBOL + "%{y:,.2f}<extra></extra>",
        )
    )
    apply_theme_to_figure(fig_sales, height=380)
    st.plotly_chart(fig_sales, use_container_width=True)

    # Period-over-Period Growth / Decline Chart
    st.markdown(f"### Period-over-Period Growth & Decline Rate (%)")
    growth_colors = [THEME["success"] if g >= 0 else THEME["danger"] for g in active_df["Growth_Pct"]]
    
    fig_growth = go.Figure()
    fig_growth.add_trace(
        go.Bar(
            x=active_df[date_col],
            y=active_df["Growth_Pct"],
            marker=dict(color=growth_colors),
            hovertemplate="<b>Date</b>: %{x|%d %b %Y}<br><b>Growth</b>: %{y:.2f}%<extra></extra>",
        )
    )
    apply_theme_to_figure(fig_growth, height=280)
    fig_growth.update_layout(yaxis=dict(title="Growth Rate (%)", zeroline=True, zerolinecolor="#64748B"))
    st.plotly_chart(fig_growth, use_container_width=True)

    # Historical Comparison (Year-over-Year)
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
    year_palette = ["#94A3B8", "#2563EB", "#0D9488"]
    for i, yr in enumerate(years):
        if yr in pivot_yoy.columns:
            fig_yoy.add_trace(
                go.Bar(
                    x=pivot_yoy.index,
                    y=pivot_yoy[yr],
                    name=f"Year {yr}",
                    marker_color=year_palette[i % len(year_palette)],
                    hovertemplate="<b>" + str(yr) + " %{x}</b><br>Revenue: " + CURRENCY_SYMBOL + "%{y:,.2f}<extra></extra>",
                )
            )

    apply_theme_to_figure(fig_yoy, height=360)
    fig_yoy.update_layout(barmode="group")
    st.plotly_chart(fig_yoy, use_container_width=True)

    # Peak & Lowest Sales Tables
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
    st.set_page_config(
        page_title=f"Sales Analytics — {APP_NAME}",
        page_icon="📉",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_custom_css()
    with st.sidebar:
        render_sidebar_header()
        st.markdown(
            f"<div style='background:#EFF6FF; border:1px solid #DBEAFE; border-radius:8px; padding:8px 12px; margin-bottom:12px;'>"
            f"<span style='font-size:13px; font-weight:700; color:{THEME['primary']};'>📉 Sales Analytics</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<hr style='border:0; border-top:1px solid #E2E8F0; margin:16px 0;'>", unsafe_allow_html=True)
        render_sidebar_provenance()
    render_sales_analytics()
