"""
Geographical Analytics Engine for SalesPulse.
Analyzes sales performance across countries, market shares, and UK vs International distribution.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


def compute_uk_vs_international(df_countries: pd.DataFrame) -> Dict[str, Any]:
    """Computes comparative metrics between UK domestic sales and international markets."""
    uk_row = df_countries[df_countries["Country"] == "United Kingdom"]
    intl_rows = df_countries[df_countries["Country"] != "United Kingdom"]

    uk_rev = float(uk_row["Revenue"].sum()) if not uk_row.empty else 0.0
    intl_rev = float(intl_rows["Revenue"].sum())
    total_rev = uk_rev + intl_rev

    uk_pct = round((uk_rev / total_rev * 100), 2) if total_rev > 0 else 0.0
    intl_pct = round((intl_rev / total_rev * 100), 2) if total_rev > 0 else 0.0

    return {
        "uk_revenue": round(uk_rev, 2),
        "uk_share_pct": uk_pct,
        "intl_revenue": round(intl_rev, 2),
        "intl_share_pct": intl_pct,
        "intl_countries_count": len(intl_rows),
    }


def get_top_countries(df_countries: pd.DataFrame, top_n: int = 10, exclude_uk: bool = False) -> pd.DataFrame:
    """Returns top performing countries by revenue, optionally excluding UK for international comparison."""
    df = df_countries
    if exclude_uk:
        df = df[df["Country"] != "United Kingdom"]
    return df.nlargest(top_n, "Revenue").reset_index(drop=True)
