"""
Model Evaluation and Benchmarking Engine.
Evaluates regression models strictly on unseen chronological holdout observations.
Computes MAE, RMSE, and R2.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def evaluate_predictions(y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
    """Computes MAE, RMSE, and R-squared with error boundary handling."""
    # Ensure non-negative predictions for revenue
    y_pred_bounded = np.clip(y_pred, 0, None)
    
    mae = mean_absolute_error(y_true, y_pred_bounded)
    # Scikit-learn 1.4+ root_mean_squared_error or sqrt(MSE)
    mse = mean_squared_error(y_true, y_pred_bounded)
    rmse = np.sqrt(mse)
    
    # Handle edge case where y_true variance is zero
    if np.var(y_true) == 0:
        r2 = 0.0
    else:
        r2 = r2_score(y_true, y_pred_bounded)
        
    return {
        "MAE": round(float(mae), 2),
        "RMSE": round(float(rmse), 2),
        "R2": round(float(r2), 4),
    }


def compare_models(
    models: Dict[str, Any],
    X_test: pd.DataFrame,
    y_test: pd.Series,
    selection_metric: str = "RMSE"
) -> Dict[str, Any]:
    """
    Evaluates each model on the identical holdout test set and builds comparison table.
    Identifies the optimal model based on lowest error metric.
    """
    records = []
    predictions = {}

    for name, model in models.items():
        y_pred = model.predict(X_test)
        predictions[name] = np.clip(y_pred, 0, None)
        metrics = evaluate_predictions(y_test, predictions[name])
        records.append({
            "Model": name,
            "MAE (£)": metrics["MAE"],
            "RMSE (£)": metrics["RMSE"],
            "R²": metrics["R2"],
        })

    comparison_df = pd.DataFrame(records)
    
    # Identify best model (lowest RMSE or MAE)
    if selection_metric.upper() == "MAE":
        best_idx = comparison_df["MAE (£)"].idxmin()
    else:
        best_idx = comparison_df["RMSE (£)"].idxmin()
        
    best_model_name = comparison_df.loc[best_idx, "Model"]
    
    return {
        "comparison_table": comparison_df,
        "best_model_name": best_model_name,
        "selection_criterion": f"Lowest {selection_metric.upper()} on chronological holdout test set",
        "predictions": predictions,
    }
