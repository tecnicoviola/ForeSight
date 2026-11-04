"""
Module 1: Sales Overview Page.
Provides high-level KPI cards, interactive date filters, and core summary visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data.loader import (
    load_cleaned_transactions,
    load_weekly_sales,
    load_product_sales,
    load_country_sales,
    load_cleaning_summary,
)
from src.analytics.sales_metrics import compute_overview_kpis
from src.utils.helpers import (
    format_currency,
    format_number,
    apply_theme_to_figure,
    render_kpi_card_html,
)
from src.utils.config import THEME, CURRENCY_SYMBOL


def render_sales_overview():
    st.markdown("## Sales Overview")
    st.markdown(
        "<p style='color:#64748B; font-size:14px; margin-top:-8px; margin-bottom:20px;'>"
        "Executive dashboard tracking genuine historical retail performance from the UCI Online Retail II dataset."
        "</p>",
        unsafe_allow_html=True,
    )

    # Load cached datasets
    df_tx = load_cleaned_transactions()
    df_weekly = load_weekly_sales()
    df_products = load_product_sales()
    df_countries = load_country_sales()

    # Filter Section
    min_date = df_tx["InvoiceDate"].min().date()
    max_date = df_tx["InvoiceDate"].max().date()

    with st.container():
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:12px 18px; margin-bottom:18px;">
                <span style="font-size:13px; font-weight:600; color:{THEME['text_primary']};">Timeline Range Filter: </span>
                <span style="font-size:13px; color:{THEME['text_secondary']};">{min_date.strftime('%d %b %Y')} – {max_date.strftime('%d %b %Y')}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        f_col1, f_col2, f_col3 = st.columns([2, 2, 1])
        with f_col1:
            start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
        with f_col2:
            end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)
        with f_col3:
            st.write("")
            st.write("")
            reset = st.button("Reset Timeline", use_container_width=True)
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

    # Render KPI Cards in two rows of 3
    k_col1, k_col2, k_col3 = st.columns(3)
    with k_col1:
        st.markdown(
            render_kpi_card_html("Total Revenue", format_currency(kpis["total_revenue"]), f"Across {format_number(kpis['total_transactions'])} orders", badge="Actual Sales", badge_type="primary"),
            unsafe_allow_html=True,
        )
    with k_col2:
        st.markdown(
            render_kpi_card_html("Total Transactions", format_number(kpis["total_transactions"]), "Unique invoice numbers", badge="Validated", badge_type="success"),
            unsafe_allow_html=True,
        )
    with k_col3:
        st.markdown(
            render_kpi_card_html("Units Sold", format_number(kpis["total_units_sold"]), "Total volume dispatched", badge="Physical Qty", badge_type="neutral"),
            unsafe_allow_html=True,
        )

    k_col4, k_col5, k_col6 = st.columns(3)
    with k_col4:
        st.markdown(
            render_kpi_card_html("Average Order Value (AOV)", format_currency(kpis["average_order_value"]), "Revenue per transaction", badge="Efficiency", badge_type="neutral"),
            unsafe_allow_html=True,
        )
    with k_col5:
        st.markdown(
            render_kpi_card_html("Active Catalog Products", format_number(kpis["number_of_products"]), "Distinct SKUs transacted", badge_type="neutral"),
            unsafe_allow_html=True,
        )
    with k_col6:
        st.markdown(
            render_kpi_card_html("Global Markets", format_number(kpis["number_of_countries"]), "Countries receiving shipments", badge_type="neutral"),
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border:0; border-top:1px solid #E2E8F0; margin: 24px 0;'>", unsafe_allow_html=True)

    # Visualizations Row 1: Revenue Trend & Weekly Sales
    c1, c2 = st.columns([3, 2])

    with c1:
        st.markdown("### Overall Revenue Trend")
        # Aggregate filtered transactions by week for smooth area curve
        filtered_weekly = (
            filtered_tx.groupby(pd.Grouper(key="InvoiceDate", freq="W-MON"))
            .agg(Revenue=("Revenue", "sum"))
            .reset_index()
        )
        filtered_weekly.rename(columns={"InvoiceDate": "Week"}, inplace=True)

        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Scatter(
                x=filtered_weekly["Week"],
                y=filtered_weekly["Revenue"],
                mode="lines",
                name="Weekly Revenue",
                line=dict(color=THEME["primary"], width=2.5),
                fill="tozeroy",
                fillcolor="rgba(37, 99, 235, 0.08)",
                hovertemplate="<b>Week</b>: %{x|%d %b %Y}<br><b>Revenue</b>: " + CURRENCY_SYMBOL + "%{y:,.2f}<extra></extra>",
            )
        )
        apply_theme_to_figure(fig_trend, height=360)
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        st.markdown("### Top Country Revenue Distribution")
        # Filtered country contribution
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
                    hole=0.55,
                    marker=dict(colors=THEME["chart_palette"]),
                    textinfo="percent",
                    hovertemplate="<b>%{label}</b><br>Revenue: " + CURRENCY_SYMBOL + "%{value:,.2f}<br>Share: %{percent}<extra></extra>",
                )
            ]
        )
        apply_theme_to_figure(fig_pie, height=360)
        fig_pie.update_layout(showlegend=True, legend=dict(orientation="v", x=1.05, y=0.5))
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
                marker=dict(color=THEME["primary"]),
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
