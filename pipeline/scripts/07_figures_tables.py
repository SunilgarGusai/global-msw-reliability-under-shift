\
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config import DATA_PROCESSED, OUT_RESULTS, OUT_FIGURES, OUT_TABLES, INCOME_ORDER
from common import checkpoint

def savefig(name):
    plt.tight_layout()
    plt.savefig(OUT_FIGURES / f"{name}.png", dpi=300, bbox_inches="tight")
    plt.savefig(OUT_FIGURES / f"{name}.pdf", bbox_inches="tight")
    plt.close()

def main():
    cohort = pd.read_csv(DATA_PROCESSED / "primary_collection_cohort.csv")
    pred = pd.read_csv(OUT_RESULTS / "primary_logo_predictions.csv")

    # Figure 1: target distribution
    plt.figure(figsize=(7.2, 4.6))
    plt.hist(cohort["y"], bins=15)
    plt.xlabel("National regular MSW collection coverage (%)")
    plt.ylabel("Countries")
    plt.title("Distribution of the primary outcome")
    savefig("fig01_target_distribution")

    # Figure 2: model MAE
    model_mae = pred.groupby("model").apply(
        lambda x: np.mean(np.abs(x["pred"] - x["y"])),
        include_groups=False
    ).sort_values()
    plt.figure(figsize=(7.2, 4.6))
    plt.bar(model_mae.index, model_mae.values)
    plt.ylabel("Leave-one-region-out MAE (percentage points)")
    plt.xticks(rotation=25, ha="right")
    plt.title("Geographic generalization performance")
    savefig("fig02_model_mae")

    # Use best non-dummy model for subgroup figures.
    candidates = [m for m in model_mae.index if m != "dummy_mean"]
    best = candidates[0]
    bp = pred[pred["model"] == best].copy()

    # Figure 3: income MAE
    income_mae = {}
    income_bias = {}
    for inc in INCOME_ORDER:
        z = bp[bp["income_group"] == inc]
        if len(z):
            income_mae[inc] = np.mean(np.abs(z["pred"] - z["y"]))
            income_bias[inc] = np.mean(z["pred"] - z["y"])

    plt.figure(figsize=(7.2, 4.8))
    plt.bar(list(income_mae), list(income_mae.values()))
    plt.ylabel("MAE (percentage points)")
    plt.xticks(rotation=20, ha="right")
    plt.title(f"Income-group prediction error ({best})")
    savefig("fig03_income_mae")

    plt.figure(figsize=(7.2, 4.8))
    plt.bar(list(income_bias), list(income_bias.values()))
    plt.axhline(0, linewidth=1)
    plt.ylabel("Mean signed error (prediction − observed)")
    plt.xticks(rotation=20, ha="right")
    plt.title(f"Income-group prediction bias ({best})")
    savefig("fig04_income_bias")

    # Figure 5: region MAE
    reg = bp.groupby("region").apply(
        lambda x: np.mean(np.abs(x["pred"] - x["y"])),
        include_groups=False
    ).sort_values(ascending=False)
    plt.figure(figsize=(8.0, 4.8))
    plt.bar(reg.index, reg.values)
    plt.ylabel("MAE (percentage points)")
    plt.xticks(rotation=35, ha="right")
    plt.title(f"Held-region errors ({best})")
    savefig("fig05_region_mae")

    # Figure 6: selective risk-coverage curve if phase 04 exists.
    conf_path = OUT_TABLES / "conformal_selective_summary.csv"
    if conf_path.exists():
        cs = pd.read_csv(conf_path)
        x = cs[
            (cs["interval_method"] == "scaled") &
            (cs["policy"].str.startswith("retain_global_q", na=False))
        ].copy()
        if len(x):
            x = x.sort_values("retention")
            plt.figure(figsize=(6.5, 4.5))
            plt.plot(x["retention"], x["mae"], marker="o")
            plt.xlabel("Retention")
            plt.ylabel("Retained-case MAE")
            plt.title("Selective prediction risk–coverage curve")
            savefig("fig06_risk_coverage")

            plt.figure(figsize=(6.5, 4.5))
            plt.plot(x["retention"], x["coverage"], marker="o")
            plt.axhline(0.90, linestyle="--")
            plt.xlabel("Retention")
            plt.ylabel("Empirical interval coverage")
            plt.title("Coverage under selective prediction")
            savefig("fig07_interval_coverage")

    checkpoint("07_figures_tables", {"best_model": best})
    print(f"BEST MODEL FOR FIGURES: {best}")
    print("PHASE 07 COMPLETE")

if __name__ == "__main__":
    main()
