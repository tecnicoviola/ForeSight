"""
Module 4: Geographical Analytics Page.
Global market distribution, country rankings, international vs. domestic UK revenue shares, and choropleth mapping.
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

from src.data.loader import load_country_sales
from src.analytics.country_analysis import compute_uk_vs_international, get_top_countries
from src.utils.helpers import (
    format_currency,
    format_number,
    format_percentage,
    apply_theme_to_figure,
    render_kpi_card_html,
)
from src.utils.config import THEME, CURRENCY_SYMBOL, APP_NAME
from src.utils.layout import load_custom_css, render_sidebar_header, render_sidebar_provenance


def render_geographical_analytics():
    st.markdown("## Geographical Analytics & Global Market Distribution")
    st.markdown(
        "<p style='color:#64748B; font-size:14px; margin-top:-6px; margin-bottom:22px;'>"
        "Worldwide sales distribution and international penetration across 43 verified delivery destinations."
        "</p>",
        unsafe_allow_html=True,
    )

    df_countries = load_country_sales()
    uk_vs_intl = compute_uk_vs_international(df_countries)

    # Geographic Overview KPIs
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.markdown(
            render_kpi_card_html(
                "Domestic UK Revenue",
                format_currency(uk_vs_intl["uk_revenue"]),
                f"{uk_vs_intl['uk_share_pct']}% of global turnover",
                badge="Primary Market",
                badge_type="primary",
            ),
            unsafe_allow_html=True,
        )
    with g2:
        st.markdown(
            render_kpi_card_html(
                "International Revenue",
                format_currency(uk_vs_intl["intl_revenue"]),
                f"{uk_vs_intl['intl_share_pct']}% export turnover",
                badge="Exports",
                badge_type="success",
            ),
            unsafe_allow_html=True,
        )
    with g3:
        st.markdown(
            render_kpi_card_html(
                "Export Destination Count",
                f"{uk_vs_intl['intl_countries_count']} Countries",
                "Non-UK sovereign markets served",
                badge="Footprint",
                badge_type="neutral",
            ),
            unsafe_allow_html=True,
        )
    with g4:
        top_export = get_top_countries(df_countries, top_n=1, exclude_uk=True).iloc[0]
        st.markdown(
            render_kpi_card_html(
                "Top Export Market",
                top_export["Country"],
                f"Revenue: {format_currency(top_export['Revenue'])}",
                badge="Lead Export",
                badge_type="warning",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border:0; border-top:1px solid #E2E8F0; margin: 20px 0;'>", unsafe_allow_html=True)

    # Global Choropleth Map
    st.markdown("### Global Sales Density Map (Plotly Choropleth)")
    fig_map = px.choropleth(
        df_countries,
        locations="Country",
        locationmode="country names",
        color="Revenue",
        hover_name="Country",
        hover_data={"Revenue": ":,.2f", "Transactions": ":,", "Quantity": ":,"},
        color_continuous_scale=[
            (0.0, "#EFF6FF"),
            (0.01, "#93C5FD"),
            (0.05, "#3B82F6"),
            (0.2, "#1D4ED8"),
            (1.0, "#0F172A"),
        ],
    )
    apply_theme_to_figure(fig_map, height=450)
    fig_map.update_geos(
        showcoastlines=True,
        coastlinecolor="#CBD5E1",
        showland=True,
        landcolor="#F8FAFC",
        showocean=True,
        oceancolor="#FFFFFF",
        projection_type="natural earth",
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Top International Markets (Excluding UK to show export nuance)
    c_left, c_right = st.columns([3, 2])
    with c_left:
        st.markdown("### Top 10 International Export Markets (Excl. UK)")
        top_intl = get_top_countries(df_countries, top_n=10, exclude_uk=True)
        fig_intl = go.Figure(
            go.Bar(
                x=top_intl["Revenue"][::-1],
                y=top_intl["Country"][::-1],
                orientation="h",
                marker=dict(color=THEME["primary"]),
                hovertemplate="<b>%{y}</b><br>Revenue: " + CURRENCY_SYMBOL + "%{x:,.2f}<extra></extra>",
            )
        )
        apply_theme_to_figure(fig_intl, height=380)
        st.plotly_chart(fig_intl, use_container_width=True)

    with c_right:
        st.markdown("### Country Revenue Contribution Share")
        top_slice = df_countries.head(5).copy()
        rem_rev = df_countries.iloc[5:]["Revenue"].sum()
        if rem_rev > 0:
            top_slice = pd.concat([
                top_slice,
                pd.DataFrame([{"Country": "Rest of the World", "Revenue": rem_rev}])
            ], ignore_index=True)

        fig_donut = go.Figure(
            go.Pie(
                labels=top_slice["Country"],
                values=top_slice["Revenue"],
                hole=0.6,
                marker=dict(colors=THEME["chart_palette"]),
                textinfo="percent",
                hovertemplate="<b>%{label}</b><br>Revenue: " + CURRENCY_SYMBOL + "%{value:,.2f}<br>Share: %{percent}<extra></extra>",
            )
        )
        apply_theme_to_figure(fig_donut, height=380)
        st.plotly_chart(fig_donut, use_container_width=True)

    # Full Geographical Ranking Table
    st.markdown("### Comprehensive Country Performance Table")
    formatted_countries = df_countries.copy()
    formatted_countries["Revenue"] = formatted_countries["Revenue"].apply(lambda v: format_currency(v))
    formatted_countries["Transactions"] = formatted_countries["Transactions"].apply(lambda v: format_number(v))
    formatted_countries["Quantity"] = formatted_countries["Quantity"].apply(lambda v: format_number(v))
    formatted_countries["AvgOrderValue"] = formatted_countries["AvgOrderValue"].apply(lambda v: format_currency(v))
    formatted_countries["Revenue_Contribution_Pct"] = formatted_countries["Revenue_Contribution_Pct"].apply(
        lambda v: f"{v:.2f}%"
    )

    st.dataframe(
        formatted_countries[
            ["Country", "Revenue", "Revenue_Contribution_Pct", "Transactions", "Quantity", "AvgOrderValue"]
        ].rename(
            columns={
                "Country": "Country / Region",
                "Revenue": "Total Revenue (£)",
                "Revenue_Contribution_Pct": "Global Share (%)",
                "Transactions": "Completed Orders",
                "Quantity": "Units Shipped",
                "AvgOrderValue": "AOV (£)",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )


if __name__ == "__main__":
    st.set_page_config(
        page_title=f"Geographical Analytics — {APP_NAME}",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_custom_css()
    with st.sidebar:
        render_sidebar_header()
        st.markdown(
            f"<div style='background:#EFF6FF; border:1px solid #DBEAFE; border-radius:8px; padding:8px 12px; margin-bottom:12px;'>"
            f"<span style='font-size:13px; font-weight:700; color:{THEME['primary']};'>🌍 Geographical Analytics</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<hr style='border:0; border-top:1px solid #E2E8F0; margin:16px 0;'>", unsafe_allow_html=True)
        render_sidebar_provenance()
    render_geographical_analytics()
