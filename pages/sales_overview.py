"""
Module 1: Sales Overview Page.
Provides high-level KPI cards, interactive date filters, and core summary visualizations.
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
    get_current_theme,
)
from src.utils.config import CURRENCY_SYMBOL, APP_NAME
from src.utils.layout import load_custom_css, render_sidebar_header, render_sidebar_provenance, render_theme_toggle


def render_sales_overview():
    theme = get_current_theme()
    is_dark = theme["mode"] == "dark"

    st.markdown("## Sales Overview")
    st.markdown(
        f"<p style='color:{theme['text_muted']}; font-size:14px; margin-top:-6px; margin-bottom:22px; font-weight:500;'>"
        "Executive retail summary tracking revenue velocity, order volumes, and key performance indicators from the UCI Online Retail II dataset."
        "</p>",
        unsafe_allow_html=True,
    )

    # Load cached datasets
    df_tx = load_cleaned_transactions()

    # Filter Section
    min_date = df_tx["InvoiceDate"].min().date()
    max_date = df_tx["InvoiceDate"].max().date()

    with st.container():
        card_bg = theme["surface"]
        card_border = theme["border"]
        f_card_html = (
            f'<div style="background:{card_bg}; border:1px solid {card_border}; border-radius:10px; padding:12px 18px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center;">'
            f'<div>'
            f'<span style="font-size:12px; font-weight:700; color:{theme["text_primary"]}; text-transform:uppercase; letter-spacing:0.04em;">Timeline Range Filter</span>'
            f'<div style="font-size:12px; color:{theme["text_muted"]}; margin-top:2px;">Original Dataset: {min_date.strftime("%d %b %Y")} – {max_date.strftime("%d %b %Y")}</div>'
            f'</div>'
            f'<span style="background:{"#1E3A8A" if is_dark else "#EFF6FF"}; color:{"#60A5FA" if is_dark else "#2563EB"}; padding:3px 10px; border-radius:9999px; font-size:11px; font-weight:700;">100% Genuine Data</span>'
            f'</div>'
        )
        st.markdown(f_card_html, unsafe_allow_html=True)

        f_col1, f_col2, f_col3 = st.columns([2, 2, 1])
        with f_col1:
            start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key="overview_start_date")
        with f_col2:
            end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key="overview_end_date")
        with f_col3:
            st.write("")
            st.write("")
            reset = st.button("Reset Timeline", use_container_width=True, key="overview_reset_btn")
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

    # Render KPI Cards with distinct accent bars
    k_col1, k_col2, k_col3 = st.columns(3)
    with k_col1:
        st.markdown(
            render_kpi_card_html("Total Revenue", format_currency(kpis["total_revenue"]), f"Across {format_number(kpis['total_transactions'])} orders", badge="Actual Sales", badge_type="primary", accent_bar="#2563EB"),
            unsafe_allow_html=True,
        )
    with k_col2:
        st.markdown(
            render_kpi_card_html("Total Transactions", format_number(kpis["total_transactions"]), "Unique invoice numbers", badge="Validated", badge_type="success", accent_bar="#10B981"),
            unsafe_allow_html=True,
        )
    with k_col3:
        st.markdown(
            render_kpi_card_html("Units Sold", format_number(kpis["total_units_sold"]), "Physical items dispatched", badge="Volume", badge_type="neutral", accent_bar="#8B5CF6"),
            unsafe_allow_html=True,
        )

    k_col4, k_col5, k_col6 = st.columns(3)
    with k_col4:
        st.markdown(
            render_kpi_card_html("Average Order Value", format_currency(kpis["average_order_value"]), "Revenue per transaction", badge="AOV", badge_type="neutral", accent_bar="#F59E0B"),
            unsafe_allow_html=True,
        )
    with k_col5:
        st.markdown(
            render_kpi_card_html("Active Catalog Products", format_number(kpis["number_of_products"]), "Distinct SKUs transacted", badge="Catalog", badge_type="neutral", accent_bar="#06B6D4"),
            unsafe_allow_html=True,
        )
    with k_col6:
        st.markdown(
            render_kpi_card_html("Global Markets", format_number(kpis["number_of_countries"]), "Destination countries", badge="Global", badge_type="neutral", accent_bar="#EC4899"),
            unsafe_allow_html=True,
        )

    st.markdown(f"<hr style='border:0; border-top:1px solid {theme['border']}; margin: 20px 0;'>", unsafe_allow_html=True)

    # Visualizations Row 1: Revenue Trend & Weekly Sales
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
        fill_color = "rgba(59, 130, 246, 0.15)" if is_dark else "rgba(37, 99, 235, 0.08)"
        line_color = "#3B82F6" if is_dark else "#2563EB"

        fig_trend.add_trace(
            go.Scatter(
                x=filtered_weekly["Week"],
                y=filtered_weekly["Revenue"],
                mode="lines",
                name="Weekly Revenue",
                line=dict(color=line_color, width=2.5),
                fill="tozeroy",
                fillcolor=fill_color,
                hovertemplate="<b>Week</b>: %{x|%d %b %Y}<br><b>Revenue</b>: " + CURRENCY_SYMBOL + "%{y:,.2f}<extra></extra>",
            )
        )
        apply_theme_to_figure(fig_trend, height=360)
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        st.markdown("### Top Country Revenue Distribution")
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
                    hole=0.6,
                    marker=dict(colors=theme["chart_palette"]),
                    textinfo="percent",
                    hovertemplate="<b>%{label}</b><br>Revenue: " + CURRENCY_SYMBOL + "%{value:,.2f}<br>Share: %{percent}<extra></extra>",
                )
            ]
        )
        apply_theme_to_figure(fig_pie, height=360)
        fig_pie.update_layout(showlegend=True, legend=dict(orientation="v", x=1.02, y=0.5))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Row 2: Top Performing Products in Selected Range
    st.markdown("### Top 10 Best-Selling Products (Selected Period)")
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
                y=prod_agg["Description"].str[:35][::-1],
                orientation="h",
                marker=dict(color=theme["primary"]),
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
        prod_table["Orders"] = prod_table["Orders"].apply(lambda v: format_number(v))
        prod_table.rename(
            columns={
                "StockCode": "SKU",
                "Description": "Product Name",
                "Revenue": "Revenue (£)",
                "Units": "Units Sold",
                "Orders": "Orders",
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
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_custom_css()
    with st.sidebar:
        render_sidebar_header()
        render_theme_toggle()
        st.markdown("<hr style='border:0; border-top:1px solid rgba(226, 232, 240, 0.4); margin:14px 0;'>", unsafe_allow_html=True)
        render_sidebar_provenance()
    render_sales_overview()
