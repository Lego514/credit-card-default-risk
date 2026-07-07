"""Default-prediction models: interpretable baseline vs gradient boosting.

- Logistic regression (class_weight=balanced, scaled) — the explainable baseline
  a model-risk committee can sign off on.
- XGBoost (scale_pos_weight for imbalance) — the accuracy benchmark.
- SHAP on the XGBoost model — closes the explainability gap.
- Decile lift table — translates AUC into the number a portfolio manager uses:
  "the top-scored 10% of customers captures X% of all defaults".

Outputs: charts/roc_comparison.png, charts/shap_beeswarm.png,
reports/model_metrics.json, reports/lift_table.csv, reports/logistic_coefficients.csv
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[1]
CHARTS = ROOT / "charts"
REPORTS = ROOT / "reports"

NUMERIC = [
    "limit_bal", "age", "utilization", "max_delay", "n_months_delayed",
    "delay_trend", "avg_pay_ratio",
    "pay_1", "pay_2", "pay_3", "pay_4", "pay_5", "pay_6",
    "bill_amt1", "pay_amt1", "pay_amt2",
]
CATEGORICAL = ["sex_label", "education_label", "marriage_label"]
SEED = 42


def build_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    X = pd.get_dummies(df[NUMERIC + CATEGORICAL], columns=CATEGORICAL, drop_first=True)
    X["avg_pay_ratio"] = X["avg_pay_ratio"].fillna(0)  # customers with no bills
    return X, df["default_next_month"]


def lift_table(y_true: np.ndarray, proba: np.ndarray) -> pd.DataFrame:
    df = pd.DataFrame({"y": y_true, "p": proba}).sort_values("p", ascending=False)
    df["decile"] = np.ceil(np.arange(1, len(df) + 1) / (len(df) / 10)).astype(int)
    base_rate = df["y"].mean()
    out = (df.groupby("decile")
           .agg(customers=("y", "size"), defaults=("y", "sum"), default_rate=("y", "mean"))
           .reset_index())
    out["pct_of_all_defaults"] = (out["defaults"] / out["defaults"].sum() * 100).round(1)
    out["cum_capture_pct"] = out["pct_of_all_defaults"].cumsum().round(1)
    out["lift_vs_random"] = (out["default_rate"] / base_rate).round(2)
    out["default_rate"] = (out["default_rate"] * 100).round(2)
    return out


def main() -> None:
    CHARTS.mkdir(exist_ok=True)
    REPORTS.mkdir(exist_ok=True)

    df = pd.read_csv(ROOT / "data" / "processed" / "credit_default_clean.csv")
    X, y = build_features(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEED)

    # ---- logistic regression baseline ----
    scaler = StandardScaler().fit(X_train)
    logit = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=SEED)
    logit.fit(scaler.transform(X_train), y_train)
    p_logit = logit.predict_proba(scaler.transform(X_test))[:, 1]
    auc_logit = roc_auc_score(y_test, p_logit)

    coefs = (pd.DataFrame({"feature": X.columns, "coefficient": logit.coef_[0]})
             .sort_values("coefficient", key=abs, ascending=False).round(4))
    coefs.to_csv(REPORTS / "logistic_coefficients.csv", index=False)

    # ---- XGBoost ----
    xgb = XGBClassifier(
        n_estimators=400, max_depth=4, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9,
        scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),
        eval_metric="auc", random_state=SEED, n_jobs=-1)
    xgb.fit(X_train, y_train)
    p_xgb = xgb.predict_proba(X_test)[:, 1]
    auc_xgb = roc_auc_score(y_test, p_xgb)

    # ---- ROC comparison ----
    fig, ax = plt.subplots(figsize=(5.5, 4.5), dpi=150)
    for label, p, color in [(f"XGBoost (AUC {auc_xgb:.3f})", p_xgb, "#dc2626"),
                            (f"Logistic (AUC {auc_logit:.3f})", p_logit, "#2563eb")]:
        fpr, tpr, _ = roc_curve(y_test, p)
        ax.plot(fpr, tpr, label=label, color=color, lw=2)
    ax.plot([0, 1], [0, 1], "--", color="#9ca3af", lw=1, label="Random")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title("Held-out ROC — 6,000 test customers", fontweight="bold", fontsize=11)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(CHARTS / "roc_comparison.png", bbox_inches="tight")
    plt.close(fig)

    # ---- lift ----
    lift = lift_table(y_test.to_numpy(), p_xgb)
    lift.to_csv(REPORTS / "lift_table.csv", index=False)

    # ---- SHAP explainability ----
    sample = X_test.sample(2000, random_state=SEED)
    explainer = shap.TreeExplainer(xgb)
    shap_values = explainer.shap_values(sample)
    shap.summary_plot(shap_values, sample, show=False, max_display=12, plot_size=(8, 5))
    plt.title("What drives the model's risk scores (SHAP)", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(CHARTS / "shap_beeswarm.png", dpi=150, bbox_inches="tight")
    plt.close()

    top10 = lift.iloc[0]
    metrics = {
        "test_customers": int(len(y_test)),
        "base_default_rate_pct": round(float(y_test.mean()) * 100, 2),
        "auc_logistic": round(float(auc_logit), 4),
        "auc_xgboost": round(float(auc_xgb), 4),
        "top_decile_default_rate_pct": float(top10["default_rate"]),
        "top_decile_capture_pct": float(top10["pct_of_all_defaults"]),
        "top_decile_lift": float(top10["lift_vs_random"]),
        "top2_decile_cum_capture_pct": float(lift.iloc[1]["cum_capture_pct"]),
    }
    (REPORTS / "model_metrics.json").write_text(json.dumps(metrics, indent=2))

    print(json.dumps(metrics, indent=2))
    print("\nLift table:")
    print(lift.to_string(index=False))
    print("\nTop logistic coefficients:")
    print(coefs.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
