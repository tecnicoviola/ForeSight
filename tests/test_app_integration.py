"""
Integration test for full application modules and page renders.
"""

import pytest
import pandas as pd
from src.data.loader import (
    load_cleaned_transactions,
    load_weekly_sales,
    load_daily_sales,
    load_monthly_sales,
    load_product_sales,
    load_country_sales,
)
from src.analytics.sales_metrics import compute_overview_kpis, compute_time_series_growth
from src.analytics.product_analysis import get_top_products, compute_pareto_distribution
from src.analytics.country_analysis import compute_uk_vs_international, get_top_countries
from pages.sales_forecasting import get_trained_models_and_evaluation


def test_overview_analytics_integration():
    df_tx = load_cleaned_transactions()
    kpis = compute_overview_kpis(df_tx)
    assert kpis["total_revenue"] == 20476260.43
    assert kpis["total_transactions"] == 40077
    assert kpis["total_units_sold"] == 11205148
    assert kpis["average_order_value"] > 0
    assert kpis["number_of_products"] == 4916
    assert kpis["number_of_countries"] == 43


def test_sales_analytics_integration():
    df_weekly = load_weekly_sales()
    growth_df = compute_time_series_growth(df_weekly, "Revenue")
    assert "Growth_Pct" in growth_df.columns
    assert len(growth_df) == len(df_weekly)


def test_product_analytics_integration():
    df_products = load_product_sales()
    top10 = get_top_products(df_products, by="Revenue", top_n=10)
    assert len(top10) == 10
    pareto = compute_pareto_distribution(df_products)
    assert pareto["products_for_80_pct"] > 0
    assert pareto["pct_of_catalog_for_80_pct"] < 50.0  # Demonstrating classic skew


def test_geographical_analytics_integration():
    df_countries = load_country_sales()
    uk_vs_intl = compute_uk_vs_international(df_countries)
    assert uk_vs_intl["uk_share_pct"] > 70.0  # UK is majority
    assert uk_vs_intl["intl_countries_count"] >= 35
    top_intl = get_top_countries(df_countries, top_n=5, exclude_uk=True)
    assert "United Kingdom" not in top_intl["Country"].values


def test_sales_forecasting_integration():
    state = get_trained_models_and_evaluation(holdout_weeks=12)
    assert "models" in state
    assert "eval_results" in state
    comp = state["eval_results"]["comparison_table"]
    assert len(comp) == 3
