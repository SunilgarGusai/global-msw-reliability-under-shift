\
import numpy as np
import pandas as pd

from config import DATA_PROCESSED, OUT_RESULTS, OUT_TABLES
from common import checkpoint, regression_metrics, safe_group_metrics
from modeling import logo_predictions, summarize_predictions

def run_target(df, target_col, label):
    x = df.copy()
    x["y"] = x[target_col].astype(float)
    pred, tune = logo_predictions(
        x,
        target_col="y",
        model_names=["dummy_mean", "linear", "ridge", "random_forest", "hist_gbr"],
    )
    pred["secondary_definition"] = label
    return pred, tune

def main():
    df = pd.read_csv(DATA_PROCESSED / "secondary_treatment_cohort.csv")
    strict_pred, strict_tune = run_target(df, "strict_controlled", "strict")
    perm_pred, perm_tune = run_target(df, "permissive_controlled", "permissive")

    pred = pd.concat([strict_pred, perm_pred], ignore_index=True)
    pred.to_csv(OUT_RESULTS / "secondary_logo_predictions.csv", index=False)

    rows = []
    for definition, p0 in pred.groupby("secondary_definition"):
        for model, p in p0.groupby("model"):
            m = regression_metrics(p["y"], p["pred"])
            m.update({"definition": definition, "model": model})
            rows.append(m)
    summary = pd.DataFrame(rows).sort_values(["definition", "mae"])
    summary.to_csv(OUT_TABLES / "secondary_model_summary.csv", index=False)

    ambiguity = df["ambiguity_delta"].describe().to_dict()
    pd.DataFrame([ambiguity]).to_csv(
        OUT_TABLES / "secondary_ambiguity_summary.csv", index=False
    )

    checkpoint("06_secondary_endpoint", {
        "n": len(df),
        "ambiguity_mean": float(df["ambiguity_delta"].mean()),
        "ambiguity_median": float(df["ambiguity_delta"].median()),
    })
    print(summary.to_string(index=False))
    print("PHASE 06 COMPLETE")

if __name__ == "__main__":
    main()
