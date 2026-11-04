"""
Module 5 & 6: Sales Forecasting & Model Comparison.
Weekly sales forecasting using genuine regression models:
- Linear Regression
- Polynomial Regression (Pipeline)
- Random Forest Regressor
Includes chronological holdout evaluation (MAE, RMSE, R2), model comparison benchmarking,
and recursive future multi-step forecasting across 4, 8, or 12 week horizons.
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
    get_current_theme,
)
from src.utils.config import CURRENCY_SYMBOL, APP_NAME
from src.utils.layout import load_custom_css, render_sidebar_header, render_sidebar_provenance, render_theme_toggle


@st.cache_data(show_spinner=False)
def get_trained_models_and_evaluation(holdout_weeks: int = 12):
    """Caches chronological model training and evaluation results to ensure snappy UI responsiveness."""
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

    st.markdown("## Sales Forecasting & Regression Model Comparison")
    st.markdown(
        f"<p style='color:{theme['text_muted']}; font-size:14px; margin-top:-6px; margin-bottom:22px; font-weight:500;'>"
        "Supervised machine learning time-series regression models trained on historical weekly revenue to evaluate predictive accuracy and project future weekly demand."
        "</p>",
        unsafe_allow_html=True,
    )

    # Forecasting Configuration Controls
    with st.container():
        card_bg = theme["surface"]
        card_border = theme["border"]
        st.markdown(
            f"""
            <div style="background:{card_bg}; border:1px solid {card_border}; border-radius:10px; padding:12px 18px; margin-bottom:14px;">
                <span style="font-size:12px; font-weight:700; color:{theme['text_primary']}; text-transform:uppercase; letter-spacing:0.04em;">Forecasting Engine Parameters</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c_param1, c_param2, c_param3 = st.columns([1, 1, 1])
        with c_param1:
            holdout_weeks = st.selectbox(
                "Chronological Holdout Validation Period:",
                [8, 12, 16],
                index=1,
                key="fc_holdout_weeks",
                help="Number of most recent historical weeks reserved as strictly unseen test observations.",
            )
        with c_param2:
            horizon_weeks = st.selectbox(
                "Future Forecast Horizon:",
                [4, 8, 12],
                index=1,
                key="fc_horizon_weeks",
                help="Number of future weeks to forecast beyond the historical dataset timeline.",
            )
        with c_param3:
            selected_model_name = st.selectbox(
                "Active Forecasting Model:",
                ["Best Model (Auto-Selected)", "Linear Regression", "Polynomial Regression", "Random Forest"],
                index=0,
                key="fc_selected_model",
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

    # Metrics Summary Row for Active Model
    active_row = comp_table[comp_table["Model"] == active_model_name].iloc[0]

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            render_kpi_card_html(
                "Selected Model",
                active_model_name,
                "Auto-Selected Best" if selected_model_name.startswith("Best Model") else "User-Selected",
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
                f"Evaluation on {holdout_weeks} holdout weeks",
                badge="RMSE",
                badge_type="neutral",
                accent_bar="#F59E0B",
            ),
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            render_kpi_card_html(
                "Mean Absolute Error",
                format_currency(active_row["MAE (£)"]),
                "Average absolute error per week",
                badge="MAE",
                badge_type="neutral",
                accent_bar="#8B5CF6",
            ),
            unsafe_allow_html=True,
        )
    with k4:
        r2_val = active_row["R²"]
        b_type = "success" if r2_val > 0.3 else ("warning" if r2_val > 0 else "danger")
        accent_r2 = "#10B981" if r2_val > 0.3 else "#F59E0B"
        st.markdown(
            render_kpi_card_html(
                "R² Coefficient",
                f"{r2_val:.4f}",
                "Variance explained by model",
                badge="Holdout R²",
                badge_type=b_type,
                accent_bar=accent_r2,
            ),
            unsafe_allow_html=True,
        )

    st.markdown(f"<hr style='border:0; border-top:1px solid {theme['border']}; margin: 20px 0;'>", unsafe_allow_html=True)

    # Section 1: Model Comparison Benchmarking Table
    st.markdown("### Model Comparison & Holdout Validation Benchmark")
    st.markdown(
        f"<p style='color:{theme['text_muted']}; font-size:13px; margin-top:-6px;'>"
        f"Strict chronological evaluation across identical holdout period ({holdout_weeks} weeks). "
        f"<b>Best performing model: {best_model_name}</b> ({eval_results['selection_criterion']})."
        f"</p>",
        unsafe_allow_html=True,
    )

    styled_comp = comp_table.copy()
    styled_comp["MAE (£)"] = styled_comp["MAE (£)"].apply(lambda v: format_currency(v))
    styled_comp["RMSE (£)"] = styled_comp["RMSE (£)"].apply(lambda v: format_currency(v))
    styled_comp["R²"] = styled_comp["R²"].apply(lambda v: f"{v:.4f}")
    styled_comp["Status"] = styled_comp["Model"].apply(
        lambda m: "★ Best Performing Model" if m == best_model_name else "Baseline Model"
    )

    st.dataframe(styled_comp, hide_index=True, use_container_width=True)

    # Section 2: Actual vs Predicted on Holdout Period
    st.markdown("### Holdout Period Validation: Actual vs. Predicted Weekly Sales")
    
    test_dates = clean_df.iloc[-holdout_weeks:]["Week_Start"].reset_index(drop=True)
    
    fig_holdout = go.Figure()
    ground_truth_color = "#FFFFFF" if is_dark else "#0F172A"
    fig_holdout.add_trace(
        go.Scatter(
            x=test_dates,
            y=y_test.values,
            mode="lines+markers",
            name="Actual Weekly Revenue (Ground Truth)",
            line=dict(color=ground_truth_color, width=2.5),
            marker=dict(size=7),
            hovertemplate="<b>Actual</b>: %{x|%d %b %Y}<br>Revenue: " + CURRENCY_SYMBOL + "%{y:,.2f}<extra></extra>",
        )
    )

    colors = {
        "Linear Regression": "#14B8A6" if is_dark else "#0D9488",
        "Polynomial Regression": "#A78BFA" if is_dark else "#8B5CF6",
        "Random Forest": "#FBBF24" if is_dark else "#F59E0B",
    }
    for m_name in models.keys():
        pred_vals = holdout_preds[m_name]
        is_active = m_name == active_model_name
        fig_holdout.add_trace(
            go.Scatter(
                x=test_dates,
                y=pred_vals,
                mode="lines+markers",
                name=f"{m_name} Prediction" + (" (Active)" if is_active else ""),
                line=dict(color=colors.get(m_name, "#2563EB"), width=2.5 if is_active else 1.5, dash="solid" if is_active else "dot"),
                marker=dict(size=6 if is_active else 4),
                hovertemplate=f"<b>{m_name}</b>: %{{x|%d %b %Y}}<br>Revenue: " + CURRENCY_SYMBOL + "%{y:,.2f}<extra></extra>",
            )
        )

    apply_theme_to_figure(fig_holdout, height=380)
    st.plotly_chart(fig_holdout, use_container_width=True)

    # Section 3: Future Recursive Sales Forecast
    st.markdown(f"### Future Weekly Sales Projection ({horizon_weeks} Weeks Ahead)")
    st.markdown(
        f"<p style='color:{theme['text_muted']}; font-size:13px; margin-top:-6px;'>"
        f"Generated using recursive autoregression via <b>{active_model_name}</b>. "
        f"Preceding predictions feed dynamically into subsequent weekly lag and rolling features."
        f"</p>",
        unsafe_allow_html=True,
    )

    future_df = forecast_future_weeks(active_model, weekly_df, horizon_weeks=horizon_weeks, model_name=active_model_name)

    recent_history = weekly_df.tail(26).copy()

    fig_future = go.Figure()

    fig_future.add_trace(
        go.Scatter(
            x=recent_history["Week_Start"],
            y=recent_history["Revenue"],
            mode="lines+markers",
            name="Historical Actual Revenue",
            line=dict(color=theme["primary"], width=2.5),
            marker=dict(size=5),
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
            line=dict(color="#10B981", width=2.5, dash="dash"),
            marker=dict(size=7, color="#10B981"),
            hovertemplate="<b>Forecast</b>: %{x|%d %b %Y}<br>Projected: " + CURRENCY_SYMBOL + "%{y:,.2f}<extra></extra>",
        )
    )

    last_hist_date = recent_history["Week_Start"].iloc[-1]
    fig_future.add_vline(
        x=last_hist_date.timestamp() * 1000,
        line_width=1.5,
        line_dash="dot",
        line_color="#94A3B8" if not is_dark else "#4B5563",
        annotation_text="Forecast Horizon Start",
        annotation_position="top left",
        annotation_font=dict(size=11, color=theme["text_muted"]),
    )

    apply_theme_to_figure(fig_future, height=400)
    st.plotly_chart(fig_future, use_container_width=True)

    # Forecast Details Table
    f_tbl_col1, f_tbl_col2 = st.columns([3, 2])
    with f_tbl_col1:
        st.markdown("#### Projected Future Weekly Revenue Schedule")
        display_forecast = future_df.copy()
        display_forecast["Week_Start"] = display_forecast["Week_Start"].dt.strftime("%d %b %Y")
        display_forecast["Projected_Revenue"] = display_forecast["Predicted_Revenue"].apply(lambda v: format_currency(v))
        st.dataframe(
            display_forecast[["Horizon_Week", "Week_Start", "Projected_Revenue", "Model"]].rename(
                columns={
                    "Horizon_Week": "Week # Ahead",
                    "Week_Start": "Projected Week Start Date",
                    "Projected_Revenue": "Forecasted Revenue (£)",
                    "Model": "Model Used",
                }
            ),
            hide_index=True,
            use_container_width=True,
        )

    with f_tbl_col2:
        st.markdown("#### Forecast Summary Statistics")
        total_projected = future_df["Predicted_Revenue"].sum()
        mean_projected = future_df["Predicted_Revenue"].mean()
        min_proj = future_df["Predicted_Revenue"].min()
        max_proj = future_df["Predicted_Revenue"].max()

        card_summary_html = (
            f'<div style="background:{theme["surface"]}; border:1px solid {theme["border"]}; border-radius:12px; padding:18px 20px; box-shadow:0 1px 3px rgba(0,0,0,0.08);">'
            f'<div style="font-size:11px; font-weight:700; color:{theme["text_secondary"]}; text-transform:uppercase; letter-spacing:0.05em;">TOTAL CUMULATIVE FORECAST</div>'
            f'<div style="font-size:26px; font-weight:800; color:{theme["primary"]}; margin:6px 0; letter-spacing:-0.03em;">{format_currency(total_projected)}</div>'
            f'<div style="font-size:12px; color:{theme["text_muted"]};">Expected revenue across next {horizon_weeks} weeks</div>'
            f'<hr style="border:0; border-top:1px solid {theme["border"]}; margin:14px 0;">'
            f'<div style="font-size:13px; color:{theme["text_secondary"]}; line-height:1.8;">'
            f'<b>Weekly Average:</b> {format_currency(mean_projected)}<br>'
            f'<b>Projected Minimum:</b> {format_currency(min_proj)}<br>'
            f'<b>Projected Maximum:</b> {format_currency(max_proj)}<br>'
            f'<b>Target Horizon:</b> {horizon_weeks} Weeks'
            f'</div>'
            f'</div>'
        )
        st.markdown(card_summary_html, unsafe_allow_html=True)


if __name__ == "__main__":
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "Light"
    st.set_page_config(
        page_title=f"Sales Forecasting — {APP_NAME}",
        page_icon="🔮",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_custom_css()
    with st.sidebar:
        render_sidebar_header()
        render_theme_toggle()
        st.markdown("<hr style='border:0; border-top:1px solid rgba(226, 232, 240, 0.4); margin:14px 0;'>", unsafe_allow_html=True)
        render_sidebar_provenance()
    render_sales_forecasting()
