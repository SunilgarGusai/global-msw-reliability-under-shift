\
import pandas as pd

from config import DATA_PROCESSED, OUT_RESULTS, OUT_TABLES
from common import checkpoint, safe_group_metrics
from modeling import logo_predictions, summarize_predictions

def main():
    df = pd.read_csv(DATA_PROCESSED / "primary_collection_cohort.csv")
    pred, tune = logo_predictions(df, target_col="y")

    pred.to_csv(OUT_RESULTS / "primary_logo_predictions.csv", index=False)
    tune.to_csv(OUT_RESULTS / "primary_tuning_log.csv", index=False)

    overall = summarize_predictions(pred)
    overall.to_csv(OUT_TABLES / "primary_model_summary.csv", index=False)

    subgroup_rows = []
    for model, p in pred.groupby("model"):
        for group_col in ["region", "income_group"]:
            t = safe_group_metrics(p, group_col)
            t["model"] = model
            t["group_type"] = group_col
            t = t.rename(columns={group_col: "group"})
            subgroup_rows.append(t)
    subgroup = pd.concat(subgroup_rows, ignore_index=True)
    subgroup.to_csv(OUT_TABLES / "primary_subgroup_metrics.csv", index=False)

    best = overall.iloc[0].to_dict()
    checkpoint("03_primary_models", {
        "best_model": best["model"],
        "best_mae": best["mae"],
        "best_rmse": best["rmse"],
        "best_r2": best["r2"],
    })

    print(overall.to_string(index=False))
    print("PHASE 03 COMPLETE")

if __name__ == "__main__":
    main()
