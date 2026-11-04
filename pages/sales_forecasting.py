"""
Module 5 & 6: Sales Forecasting & Model Comparison.
Redesigned with Linear / Stripe SaaS visual hierarchy:
- Supervised regression benchmarking on chronological holdout data
- Compact parameter configuration bar
- Equal-height model metric cards
- Actual vs Predicted validation curves
- Recursive forward projection with clear historical demarcation line
- Projected revenue schedule table & cumulative summary card
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

from src.data.loader import load_weekly_sales
from src.forecasting.feature_engineering import prepare_training_data
from src.forecasting.train import chronological_split, train_models
from src.forecasting.evaluate import compare_models
from src.forecasting.predict import forecast_future_weeks
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


@st.cache_data(show_spinner=False)
def get_trained_models_and_evaluation(holdout_weeks: int = 12):
    """Caches chronological model training and evaluation results for responsive UI execution."""
    weekly_df = load_weekly_sales()
    X, y, clean_df = prepare_training_data(weekly_df)
    X_train, X_test, y_train, y_test = chronological_split(X, y, holdout_weeks=holdout_weeks)
    models = train_models(X_train, y_train)
    eval_results = compare_models(models, X_test, y_test, selection_metric="RMSE")
    return {
        "weekly_df": weekly_df,
        "clean_df": clean_df,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "models": models,
        "eval_results": eval_results,
    }


def render_sales_forecasting():
    theme = get_current_theme()
    is_dark = theme["mode"] == "dark"

    # Section A: Header
    render_page_header(
        title="Sales Forecasting",
        description="Forecast future weekly revenue using historical sales data and regression-based machine learning models.",
        badge="Supervised ML Engine",
    )

    # Section B: Forecast Configuration Bar
    with st.container():
        f_bg = theme["surface"]
        f_border = theme["border"]
        f_header = (
            f'<div class="fs-filter-bar" style="background:{f_bg}; border:1px solid {f_border}; border-radius:8px; padding:10px 14px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center;">'
            f'<span style="font-size:11px; font-weight:700; color:{theme["text_primary"]}; text-transform:uppercase; letter-spacing:0.04em;">Model Configuration Parameters</span>'
            f'<span style="font-size:11px; color:{theme["text_muted"]};">Chronological Holdout Splitting • Zero Target Leakage</span>'
            f'</div>'
        )
        st.markdown(f_header, unsafe_allow_html=True)

        col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
        with col_c1:
            holdout_weeks = st.selectbox(
                "Holdout Evaluation Period:",
                [8, 12, 16],
                index=1,
                key="sf_holdout_select",
                help="Unseen chronological test weeks reserved for validation.",
            )
        with col_c2:
            horizon_weeks = st.selectbox(
                "Future Forecast Horizon:",
                [4, 8, 12],
                index=1,
                key="sf_horizon_select",
                help="Weeks to project into the future beyond observed history.",
            )
        with col_c3:
            selected_model_name = st.selectbox(
                "Active Forecasting Model:",
                ["Best Model (Auto-Selected)", "Linear Regression", "Polynomial Regression", "Random Forest"],
                index=0,
                key="sf_model_select",
            )

    # Train and evaluate models
    state = get_trained_models_and_evaluation(holdout_weeks=holdout_weeks)
    weekly_df = state["weekly_df"]
    clean_df = state["clean_df"]
    models = state["models"]
    eval_results = state["eval_results"]
    comp_table = eval_results["comparison_table"]
    best_model_name = eval_results["best_model_name"]
    holdout_preds = eval_results["predictions"]
    y_test = state["y_test"]

    active_model_name = best_model_name if selected_model_name.startswith("Best Model") else selected_model_name
    active_model = models[active_model_name]
    active_row = comp_table[comp_table["Model"] == active_model_name].iloc[0]

    # Section C: Selected Model Performance (4 Equal-Height Cards)
    st.write("")  # spacing
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            render_kpi_card_html(
                "Active Architecture",
                active_model_name,
                "Optimal Model" if selected_model_name.startswith("Best Model") else "Manual Selection",
                badge="Active",
                badge_type="primary",
                accent_bar="#2563EB",
            ),
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            render_kpi_card_html(
                "Root Mean Squared Error",
                format_currency(active_row["RMSE (£)"]),
                f"Tested on {holdout_weeks} holdout weeks",
                badge="RMSE",
                badge_type="neutral",
                accent_bar="#D97706",
            ),
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            render_kpi_card_html(
                "Mean Absolute Error",
                format_currency(active_row["MAE (£)"]),
                "Mean absolute deviation per week",
                badge="MAE",
                badge_type="neutral",
                accent_bar="#8B5CF6",
            ),
            unsafe_allow_html=True,
        )
    with k4:
        r2_val = active_row["R²"]
        b_type = "success" if r2_val > 0.3 else ("warning" if r2_val > 0 else "danger")
        accent_color = "#059669" if r2_val > 0.3 else "#D97706"
        st.markdown(
            render_kpi_card_html(
                "R² Coefficient",
                f"{r2_val:.4f}",
                "Variance explained by model",
                badge="Holdout R²",
                badge_type=b_type,
                accent_bar=accent_color,
            ),
            unsafe_allow_html=True,
        )

    st.markdown(f"<hr style='border:0; border-top:1px solid {theme['border']}; margin: 24px 0;'>", unsafe_allow_html=True)

    # Section D: Model Comparison Benchmarking Table
    st.markdown("### Model Comparison & Holdout Benchmark")
    st.markdown(
        f"<p style='color:{theme['text_muted']}; font-size:12.5px; margin-top:-6px; margin-bottom:12px;'>"
        f"Chronological evaluation on identical held-out test data ({holdout_weeks} weeks). "
        f"<b>Best performing architecture: {best_model_name}</b> ({eval_results['selection_criterion']})."
        f"</p>",
        unsafe_allow_html=True,
    )

    styled_comp = comp_table.copy()
    styled_comp["MAE (£)"] = styled_comp["MAE (£)"].apply(lambda v: format_currency(v))
    styled_comp["RMSE (£)"] = styled_comp["RMSE (£)"].apply(lambda v: format_currency(v))
    styled_comp["R²"] = styled_comp["R²"].apply(lambda v: f"{v:.4f}")
    styled_comp["Evaluation Status"] = styled_comp["Model"].apply(
        lambda m: "★ Best Performing Model" if m == best_model_name else "Baseline Model"
    )

    st.dataframe(styled_comp, hide_index=True, use_container_width=True)

    # Section E: Holdout Actual vs Predicted Line Chart
    st.markdown("### Holdout Validation: Actual vs. Predicted Weekly Sales")
    test_dates = clean_df.iloc[-holdout_weeks:]["Week_Start"].reset_index(drop=True)
    
    fig_holdout = go.Figure()
    ground_color = "#F8FAFC" if is_dark else "#0F172A"
    fig_holdout.add_trace(
        go.Scatter(
            x=test_dates,
            y=y_test.values,
            mode="lines+markers",
            name="Ground Truth (Actual Sales)",
            line=dict(color=ground_color, width=2.5),
            marker=dict(size=6),
            hovertemplate="<b>Actual</b>: %{x|%d %b %Y}<br>Revenue: " + CURRENCY_SYMBOL + "%{y:,.2f}<extra></extra>",
        )
    )

    colors = {
        "Linear Regression": "#14B8A6" if is_dark else "#0D9488",
        "Polynomial Regression": "#A78BFA" if is_dark else "#8B5CF6",
        "Random Forest": "#FBBF24" if is_dark else "#D97706",
    }
    for m_name in models.keys():
        pred_vals = holdout_preds[m_name]
        is_active = m_name == active_model_name
        fig_holdout.add_trace(
            go.Scatter(
                x=test_dates,
                y=pred_vals,
                mode="lines+markers",
                name=f"{m_name}" + (" (Active)" if is_active else ""),
                line=dict(color=colors.get(m_name, "#2563EB"), width=2.5 if is_active else 1.5, dash="solid" if is_active else "dot"),
                marker=dict(size=5 if is_active else 3),
                hovertemplate=f"<b>{m_name}</b>: %{{x|%d %b %Y}}<br>Revenue: " + CURRENCY_SYMBOL + "%{y:,.2f}<extra></extra>",
            )
        )

    apply_theme_to_figure(fig_holdout, height=360)
    st.plotly_chart(fig_holdout, use_container_width=True)

    # Section F: Future Recursive Sales Forecast Chart
    st.markdown(f"### Future Weekly Forecast ({horizon_weeks} Weeks Horizon)")
    st.markdown(
        f"<p style='color:{theme['text_muted']}; font-size:12.5px; margin-top:-6px; margin-bottom:12px;'>"
        f"Generated via recursive autoregression with <b>{active_model_name}</b>. "
        f"Predictions update subsequent lag features dynamically."
        f"</p>",
        unsafe_allow_html=True,
    )

    future_df = forecast_future_weeks(active_model, weekly_df, horizon_weeks=horizon_weeks, model_name=active_model_name)
    recent_history = weekly_df.tail(24).copy()

    fig_future = go.Figure()

    fig_future.add_trace(
        go.Scatter(
            x=recent_history["Week_Start"],
            y=recent_history["Revenue"],
            mode="lines+markers",
            name="Observed History",
            line=dict(color=theme["primary"], width=2.2),
            marker=dict(size=4),
            hovertemplate="<b>Actual</b>: %{x|%d %b %Y}<br>Revenue: " + CURRENCY_SYMBOL + "%{y:,.2f}<extra></extra>",
        )
    )

    last_actual_point = pd.DataFrame([{
        "Week_Start": recent_history["Week_Start"].iloc[-1],
        "Predicted_Revenue": recent_history["Revenue"].iloc[-1],
    }])
    forecast_bridge = pd.concat([last_actual_point, future_df[["Week_Start", "Predicted_Revenue"]]], ignore_index=True)

    fig_future.add_trace(
        go.Scatter(
            x=forecast_bridge["Week_Start"],
            y=forecast_bridge["Predicted_Revenue"],
            mode="lines+markers",
            name=f"Recursive Forecast ({active_model_name})",
            line=dict(color="#059669" if not is_dark else "#10B981", width=2.5, dash="dash"),
            marker=dict(size=6, color="#059669" if not is_dark else "#10B981"),
            hovertemplate="<b>Forecast</b>: %{x|%d %b %Y}<br>Projected: " + CURRENCY_SYMBOL + "%{y:,.2f}<extra></extra>",
        )
    )

    last_hist_date = recent_history["Week_Start"].iloc[-1]
    fig_future.add_vline(
        x=last_hist_date.timestamp() * 1000,
        line_width=1.5,
        line_dash="dot",
        line_color="#64748B",
        annotation_text="Forecast Horizon Start",
        annotation_position="top left",
        annotation_font=dict(size=11, color=theme["text_muted"]),
    )

    apply_theme_to_figure(fig_future, height=380)
    st.plotly_chart(fig_future, use_container_width=True)

    # Section G: Forecast Details & Cumulative Summary
    f_tbl_col1, f_tbl_col2 = st.columns([3, 2])
    with f_tbl_col1:
        st.markdown("#### Projected Weekly Revenue Schedule")
        display_forecast = future_df.copy()
        display_forecast["Week_Start"] = display_forecast["Week_Start"].dt.strftime("%d %b %Y")
        display_forecast["Projected_Revenue"] = display_forecast["Predicted_Revenue"].apply(lambda v: format_currency(v))
        st.dataframe(
            display_forecast[["Horizon_Week", "Week_Start", "Projected_Revenue", "Model"]].rename(
                columns={
                    "Horizon_Week": "Week Ahead",
                    "Week_Start": "Week Commencing Date",
                    "Projected_Revenue": "Forecasted Revenue (£)",
                    "Model": "Model Architecture",
                }
            ),
            hide_index=True,
            use_container_width=True,
        )

    with f_tbl_col2:
        st.markdown("#### Cumulative Forecast Summary")
        total_projected = future_df["Predicted_Revenue"].sum()
        mean_projected = future_df["Predicted_Revenue"].mean()
        min_proj = future_df["Predicted_Revenue"].min()
        max_proj = future_df["Predicted_Revenue"].max()

        card_summary_html = (
            f'<div style="background:{theme["surface"]}; border:1px solid {theme["border"]}; border-radius:10px; padding:16px 18px; box-shadow:0 1px 3px rgba(0,0,0,0.06);">'
            f'<div style="font-size:11px; font-weight:700; color:{theme["text_muted"]}; text-transform:uppercase; letter-spacing:0.05em;">CUMULATIVE FORECAST TOTAL</div>'
            f'<div style="font-size:25px; font-weight:800; color:{theme["primary"]}; margin:5px 0; letter-spacing:-0.03em;">{format_currency(total_projected)}</div>'
            f'<div style="font-size:12px; color:{theme["text_muted"]};">Expected retail revenue across next {horizon_weeks} weeks</div>'
            f'<hr style="border:0; border-top:1px solid {theme["border"]}; margin:12px 0;">'
            f'<div style="font-size:12.5px; color:{theme["text_secondary"]}; line-height:1.75;">'
            f'<b>Weekly Mean:</b> {format_currency(mean_projected)}<br>'
            f'<b>Projected Min:</b> {format_currency(min_proj)}<br>'
            f'<b>Projected Max:</b> {format_currency(max_proj)}<br>'
            f'<b>Forecast Scope:</b> {horizon_weeks} Weeks Out'
            f'</div>'
            f'</div>'
        )
        st.markdown(card_summary_html, unsafe_allow_html=True)


if __name__ == "__main__":
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "Light"
    st.set_page_config(
        page_title=f"Sales Forecasting — {APP_NAME}",
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
    render_sales_forecasting()
