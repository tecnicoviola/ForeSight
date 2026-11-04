"""
Module 4: Geographical Analytics Page.
Redesigned with Linear / Stripe SaaS visual hierarchy:
- High-contrast natural earth choropleth map
- Domestic UK vs International export segmentation
- Top export market rankings and revenue contribution donut
- Comprehensive country performance data table
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


def render_geographical_analytics():
    theme = get_current_theme()
    is_dark = theme["mode"] == "dark"

    # Section A: Header
    render_page_header(
        title="Geographical Analytics",
        description="Worldwide retail footprint, destination distribution and export penetration across 43 sovereign states.",
        badge="Global Distribution",
    )

    df_countries = load_country_sales()
    uk_vs_intl = compute_uk_vs_international(df_countries)

    # Section B: 4 Equal-Height KPIs
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.markdown(
            render_kpi_card_html(
                "Domestic UK Revenue",
                format_currency(uk_vs_intl["uk_revenue"]),
                f"{uk_vs_intl['uk_share_pct']}% of global retail volume",
                badge="UK Core",
                badge_type="primary",
                accent_bar="#2563EB",
            ),
            unsafe_allow_html=True,
        )
    with g2:
        st.markdown(
            render_kpi_card_html(
                "International Revenue",
                format_currency(uk_vs_intl["intl_revenue"]),
                f"{uk_vs_intl['intl_share_pct']}% export revenue share",
                badge="Exports",
                badge_type="success",
                accent_bar="#059669",
            ),
            unsafe_allow_html=True,
        )
    with g3:
        st.markdown(
            render_kpi_card_html(
                "Export Destinations",
                f"{uk_vs_intl['intl_countries_count']} Countries",
                "Non-UK sovereign markets served",
                badge="Markets",
                badge_type="neutral",
                accent_bar="#D97706",
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
                badge="Leader",
                badge_type="warning",
                accent_bar="#8B5CF6",
            ),
            unsafe_allow_html=True,
        )

    st.markdown(f"<hr style='border:0; border-top:1px solid {theme['border']}; margin: 24px 0;'>", unsafe_allow_html=True)

    # Section C: Global Sales Density Choropleth Map
    st.markdown("### Global Sales Density Map")
    colorscale = [
        (0.0, "#182238" if is_dark else "#EFF6FF"),
        (0.02, "#3B82F6" if is_dark else "#93C5FD"),
        (0.1, "#2563EB" if is_dark else "#3B82F6"),
        (0.5, "#1D4ED8" if is_dark else "#1D4ED8"),
        (1.0, "#60A5FA" if is_dark else "#0F172A"),
    ]
    fig_map = px.choropleth(
        df_countries,
        locations="Country",
        locationmode="country names",
        color="Revenue",
        hover_name="Country",
        hover_data={"Revenue": ":,.2f", "Transactions": ":,", "Quantity": ":,"},
        color_continuous_scale=colorscale,
    )
    apply_theme_to_figure(fig_map, height=440)
    fig_map.update_geos(
        showcoastlines=True,
        coastlinecolor="#374151" if is_dark else "#CBD5E1",
        showland=True,
        landcolor="#141C2E" if is_dark else "#F8FAFC",
        showocean=True,
        oceancolor="#090D16" if is_dark else "#FFFFFF",
        projection_type="natural earth",
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Section D: Two-Column Row (Export Markets + Revenue Donut)
    c_left, c_right = st.columns([3, 2])
    with c_left:
        st.markdown("### Top 10 International Export Markets (Excl. UK)")
        top_intl = get_top_countries(df_countries, top_n=10, exclude_uk=True)
        fig_intl = go.Figure(
            go.Bar(
                x=top_intl["Revenue"][::-1],
                y=top_intl["Country"][::-1],
                orientation="h",
                marker=dict(color=theme["primary"], cornerradius=3),
                hovertemplate="<b>%{y}</b><br>Revenue: " + CURRENCY_SYMBOL + "%{x:,.2f}<extra></extra>",
            )
        )
        apply_theme_to_figure(fig_intl, height=360)
        st.plotly_chart(fig_intl, use_container_width=True)

    with c_right:
        st.markdown("### Global Revenue Contribution Share")
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
                hole=0.62,
                marker=dict(colors=theme["chart_palette"]),
                textinfo="percent",
                hovertemplate="<b>%{label}</b><br>Revenue: " + CURRENCY_SYMBOL + "%{value:,.2f}<br>Share: %{percent}<extra></extra>",
            )
        )
        apply_theme_to_figure(fig_donut, height=360)
        st.plotly_chart(fig_donut, use_container_width=True)

    # Section E: Comprehensive Country Performance Table
    st.markdown("### Country Performance Breakdown")
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
                "Country": "Destination Market",
                "Revenue": "Total Revenue (£)",
                "Revenue_Contribution_Pct": "Global Share (%)",
                "Transactions": "Orders",
                "Quantity": "Units Sold",
                "AvgOrderValue": "AOV (£)",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )


if __name__ == "__main__":
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "Light"
    st.set_page_config(
        page_title=f"Geographical Analytics — {APP_NAME}",
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
    render_geographical_analytics()
