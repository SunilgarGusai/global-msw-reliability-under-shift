\
import numpy as np
import pandas as pd

from config import DATA_PROCESSED, OUT_TABLES
from common import checkpoint, regression_metrics, safe_group_metrics
from modeling import logo_predictions

def evaluate_case(name, df):
    # Robustness deliberately focuses on interpretable linear and tree models.
    pred, _ = logo_predictions(
        df, target_col="y",
        model_names=["linear", "ridge", "random_forest"]
    )
    rows = []
    for model, p in pred.groupby("model"):
        m = regression_metrics(p["y"], p["pred"])
        m.update({"case": name, "model": model})
        low = p[p["income_group"] == "Low income"]
        m["low_n"] = int(len(low))
        m["low_mae"] = float(np.mean(np.abs(low["pred"] - low["y"]))) if len(low) else np.nan
        m["low_bias"] = float(np.mean(low["pred"] - low["y"])) if len(low) else np.nan
        rows.append(m)
    return rows

def main():
    df = pd.read_csv(DATA_PROCESSED / "primary_collection_cohort.csv")
    cases = {
        "all": df,
        "since_2015": df[df["year"] >= 2015].copy(),
        "since_2018": df[df["year"] >= 2018].copy(),
        "since_2020": df[df["year"] >= 2020].copy(),
        "msw_weight_only": df[df["unit"] == "PT_MSW"].copy(),
        "population_only": df[df["unit"] == "PT_POP"].copy(),
        "household_only": df[df["unit"] == "PT_HH"].copy(),
    }
    rows = []
    for name, part in cases.items():
        if len(part) < 25 or part["region"].nunique() < 3:
            continue
        print(f"[ROBUSTNESS] {name}: n={len(part)}")
        rows.extend(evaluate_case(name, part))
    out = pd.DataFrame(rows)
    out.to_csv(OUT_TABLES / "primary_robustness_summary.csv", index=False)
    checkpoint("05_robustness", {"cases": int(out["case"].nunique())})
    print(out.to_string(index=False))
    print("PHASE 05 COMPLETE")

if __name__ == "__main__":
    main()
