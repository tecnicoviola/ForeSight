"""
Module 1: Sales Overview Page.
Redesigned with Linear / Stripe SaaS visual hierarchy:
- Premium page header with status indicator
- Compact timeline filter bar
- 6 balanced, equal-height KPI cards
- Two-column responsive chart layout
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.data.loader import (
    load_cleaned_transactions,
    load_weekly_sales,
    load_product_sales,
    load_country_sales,
)
from src.analytics.sales_metrics import compute_overview_kpis
from src.utils.helpers import (
    format_currency,
    format_number,
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


def render_sales_overview():
    theme = get_current_theme()
    is_dark = theme["mode"] == "dark"

    # Section A: Premium Page Header
    render_page_header(
        title="Sales Overview",
        description="An overview of retail revenue, transaction activity and historical sales performance.",
        badge="Live Analytics",
    )

    # Load cached transactions
    df_tx = load_cleaned_transactions()
    min_date = df_tx["InvoiceDate"].min().date()
    max_date = df_tx["InvoiceDate"].max().date()

    # Section B: Compact Timeline Filter Toolbar
    with st.container():
        f_card_bg = theme["surface"]
        f_border = theme["border"]
        f_header = (
            f'<div class="fs-filter-bar" style="background:{f_card_bg}; border:1px solid {f_border}; border-radius:8px; padding:10px 14px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center;">'
            f'<div>'
            f'<span style="font-size:11px; font-weight:700; color:{theme["text_primary"]}; text-transform:uppercase; letter-spacing:0.04em;">Timeline Filter</span>'
            f'<span style="font-size:12px; color:{theme["text_muted"]}; margin-left:8px;">Historical Period: {min_date.strftime("%d %b %Y")} – {max_date.strftime("%d %b %Y")}</span>'
            f'</div>'
            f'<span style="background:{"#182238" if is_dark else "#EFF6FF"}; color:{"#60A5FA" if is_dark else "#2563EB"}; border:1px solid {"#2563EB" if is_dark else "#BFDBFE"}; padding:2px 8px; border-radius:4px; font-size:10.5px; font-weight:700;">Genuine Dataset</span>'
            f'</div>'
        )
        st.markdown(f_header, unsafe_allow_html=True)

        col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
        with col_f1:
            start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key="ov_start_date")
        with col_f2:
            end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key="ov_end_date")
        with col_f3:
            st.write("")
            st.write("")
            reset = st.button("Reset Timeline", use_container_width=True, key="ov_reset_btn")
            if reset:
                start_date = min_date
                end_date = max_date

    if start_date > end_date:
        st.error("Invalid Date Range: Start Date must be prior to or equal to End Date.")
        return

    # Filtered transactions
    mask = (df_tx["InvoiceDate"].dt.date >= start_date) & (df_tx["InvoiceDate"].dt.date <= end_date)
    filtered_tx = df_tx[mask]

    # Calculate actual KPIs
    kpis = compute_overview_kpis(filtered_tx)

    # Section C: KPI Dashboard (6 equal-height cards in 2 balanced rows of 3)
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(
            render_kpi_card_html("Total Revenue", format_currency(kpis["total_revenue"]), f"Across {format_number(kpis['total_transactions'])} completed orders", badge="Sales", badge_type="primary", accent_bar="#2563EB"),
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            render_kpi_card_html("Total Transactions", format_number(kpis["total_transactions"]), "Distinct invoice numbers validated", badge="Verified", badge_type="success", accent_bar="#059669"),
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            render_kpi_card_html("Units Sold", format_number(kpis["total_units_sold"]), "Total physical item volume dispatched", badge="Volume", badge_type="neutral", accent_bar="#8B5CF6"),
            unsafe_allow_html=True,
        )

    st.write("")  # consistent spacing
    k4, k5, k6 = st.columns(3)
    with k4:
        st.markdown(
            render_kpi_card_html("Average Order Value", format_currency(kpis["average_order_value"]), "Revenue generated per order", badge="AOV", badge_type="neutral", accent_bar="#D97706"),
            unsafe_allow_html=True,
        )
    with k5:
        st.markdown(
            render_kpi_card_html("Active Catalog Products", format_number(kpis["number_of_products"]), "Distinct SKUs sold in period", badge="SKUs", badge_type="neutral", accent_bar="#0D9488"),
            unsafe_allow_html=True,
        )
    with k6:
        st.markdown(
            render_kpi_card_html("Global Markets", format_number(kpis["number_of_countries"]), "Destination countries served", badge="Markets", badge_type="neutral", accent_bar="#EC4899"),
            unsafe_allow_html=True,
        )

    st.markdown(f"<hr style='border:0; border-top:1px solid {theme['border']}; margin: 24px 0;'>", unsafe_allow_html=True)

    # Section D & E: 2-Column Chart Row (Revenue Trend + Country Distribution)
    c1, c2 = st.columns([3, 2])

    with c1:
        st.markdown("### Overall Revenue Trend")
        filtered_weekly = (
            filtered_tx.groupby(pd.Grouper(key="InvoiceDate", freq="W-MON"))
            .agg(Revenue=("Revenue", "sum"))
            .reset_index()
        )
        filtered_weekly.rename(columns={"InvoiceDate": "Week"}, inplace=True)

        fig_trend = go.Figure()
        line_color = "#3B82F6" if is_dark else "#2563EB"
        fill_color = "rgba(59, 130, 246, 0.12)" if is_dark else "rgba(37, 99, 235, 0.08)"

        fig_trend.add_trace(
            go.Scatter(
                x=filtered_weekly["Week"],
                y=filtered_weekly["Revenue"],
                mode="lines",
                name="Weekly Sales",
                line=dict(color=line_color, width=2.5),
                fill="tozeroy",
                fillcolor=fill_color,
                hovertemplate="<b>Week</b>: %{x|%d %b %Y}<br><b>Revenue</b>: " + CURRENCY_SYMBOL + "%{y:,.2f}<extra></extra>",
            )
        )
        apply_theme_to_figure(fig_trend, height=350)
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        st.markdown("### Geographical Performance")
        country_agg = (
            filtered_tx.groupby("Country")["Revenue"]
            .sum()
            .reset_index()
            .sort_values("Revenue", ascending=False)
        )
        top_countries = country_agg.head(6).copy()
        other_rev = country_agg.iloc[6:]["Revenue"].sum() if len(country_agg) > 6 else 0
        if other_rev > 0:
            top_countries = pd.concat([
                top_countries,
                pd.DataFrame([{"Country": "Other Markets", "Revenue": other_rev}])
            ], ignore_index=True)

        fig_pie = go.Figure(
            data=[
                go.Pie(
                    labels=top_countries["Country"],
                    values=top_countries["Revenue"],
                    hole=0.62,
                    marker=dict(colors=theme["chart_palette"]),
                    textinfo="percent",
                    hovertemplate="<b>%{label}</b><br>Revenue: " + CURRENCY_SYMBOL + "%{value:,.2f}<br>Share: %{percent}<extra></extra>",
                )
            ]
        )
        apply_theme_to_figure(fig_pie, height=350)
        fig_pie.update_layout(showlegend=True, legend=dict(orientation="v", x=1.02, y=0.5))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Section F: Product Performance (2-Column: Chart + Table)
    st.markdown("### Product Performance (Selected Period)")
    prod_agg = (
        filtered_tx.groupby(["StockCode", "Description"])
        .agg(Revenue=("Revenue", "sum"), Units=("Quantity", "sum"), Orders=("Invoice", "nunique"))
        .reset_index()
        .sort_values("Revenue", ascending=False)
        .head(10)
    )

    p1, p2 = st.columns([3, 2])
    with p1:
        fig_prod = go.Figure(
            go.Bar(
                x=prod_agg["Revenue"][::-1],
                y=prod_agg["Description"].str[:32][::-1],
                orientation="h",
                marker=dict(color=theme["primary"], cornerradius=4),
                hovertemplate="<b>%{y}</b><br>Revenue: " + CURRENCY_SYMBOL + "%{x:,.2f}<extra></extra>",
            )
        )
        apply_theme_to_figure(fig_prod, height=340)
        fig_prod.update_layout(yaxis=dict(autorange=True))
        st.plotly_chart(fig_prod, use_container_width=True)

    with p2:
        prod_table = prod_agg.copy()
        prod_table["Revenue"] = prod_table["Revenue"].apply(lambda v: format_currency(v))
        prod_table["Units"] = prod_table["Units"].apply(lambda v: format_number(v))
        prod_table.rename(
            columns={
                "StockCode": "SKU",
                "Description": "Product Name",
                "Revenue": "Revenue (£)",
                "Units": "Units Sold",
            },
            inplace=True,
        )
        st.dataframe(
            prod_table[["SKU", "Product Name", "Revenue (£)", "Units Sold"]],
            height=340,
            use_container_width=True,
            hide_index=True,
        )


if __name__ == "__main__":
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "Light"
    st.set_page_config(
        page_title=f"Sales Overview — {APP_NAME}",
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
    render_sales_overview()
