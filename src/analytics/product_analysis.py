"""
Product Analytics Engine for SalesPulse.
Calculates product rankings, volume vs value, revenue contribution, and pareto distribution.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


def get_top_products(
    df_products: pd.DataFrame,
    by: str = "Revenue",
    top_n: int = 10
) -> pd.DataFrame:
    """Returns top N products ranked by Revenue or Quantity."""
    col = "Revenue" if by.lower() == "revenue" else "Quantity"
    return df_products.nlargest(top_n, col).reset_index(drop=True)


def compute_pareto_distribution(df_products: pd.DataFrame) -> Dict[str, Any]:
    """Computes Pareto (80/20 rule) metrics for product revenue."""
    sorted_df = df_products.sort_values("Revenue", ascending=False).reset_index(drop=True)
    total_rev = sorted_df["Revenue"].sum()
    total_prods = len(sorted_df)

    if total_rev == 0 or total_prods == 0:
        return {
            "products_for_80_pct": 0,
            "pct_of_catalog_for_80_pct": 0.0,
            "top_10_pct_revenue_share": 0.0,
        }

    sorted_df["CumRevenuePct"] = (sorted_df["Revenue"].cumsum() / total_rev) * 100
    idx_80 = (sorted_df["CumRevenuePct"] <= 80).sum() + 1
    pct_for_80 = round((idx_80 / total_prods) * 100, 2)

    top_10_pct_count = max(1, int(total_prods * 0.10))
    top_10_rev = sorted_df.iloc[:top_10_pct_count]["Revenue"].sum()
    top_10_pct_share = round((top_10_rev / total_rev) * 100, 2)

    return {
        "products_for_80_pct": idx_80,
        "total_catalog_size": total_prods,
        "pct_of_catalog_for_80_pct": pct_for_80,
        "top_10_pct_revenue_share": top_10_pct_share,
    }
