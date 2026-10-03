from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import matplotlib.pyplot as plt


def bootstrap_mean_ci(values, rng, reps=20000):
    x = np.asarray(pd.Series(values).dropna(), dtype=float)
    idx = rng.integers(0, len(x), size=(reps, len(x)))
    means = x[idx].mean(axis=1)
    return float(x.mean()), float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def main():
    ap = argparse.ArgumentParser(description="PAPER19 reviewer-stage audit using frozen LORO OOF predictions only.")
    ap.add_argument("--predictions", default="results/verified_baseline/results/primary_logo_predictions.csv")
    ap.add_argument("--out", default="results/v2_upgrade_reproduced")
    ap.add_argument("--figures", default="figures/reproduced")
    ap.add_argument("--seed", type=int, default=19019)
    ap.add_argument("--bootstrap", type=int, default=20000)
    args = ap.parse_args()

    pred_path = Path(args.predictions)
    out = Path(args.out); figdir = Path(args.figures)
    out.mkdir(parents=True, exist_ok=True); figdir.mkdir(parents=True, exist_ok=True)
    p = pd.read_csv(pred_path)
    p = p[p["model"] == "linear"].copy().reset_index(drop=True)
    if len(p) != 154:
        raise RuntimeError(f"Expected 154 linear OOF rows, found {len(p)}")

    p["abs_error"] = (p["pred"] - p["y"]).abs()
    p["signed_error"] = p["pred"] - p["y"]
    p["true_deficit"] = 100 - p["y"]
    p["pred_deficit"] = 100 - p["pred"]
    p["target_quartile"] = pd.qcut(
        p["y"], 4, labels=["Q1_lowest_coverage", "Q2", "Q3", "Q4_highest_coverage"]
    )

    rng = np.random.default_rng(args.seed)
    rows = []
    for q, g in p.groupby("target_quartile", observed=True):
        mae, ml, mh = bootstrap_mean_ci(g["abs_error"], rng, args.bootstrap)
        bias, bl, bh = bootstrap_mean_ci(g["signed_error"], rng, args.bootstrap)
        rows.append(dict(target_quartile=str(q), n=len(g), mean_observed_coverage=g["y"].mean(),
                         mae=mae, mae_ci95_low=ml, mae_ci95_high=mh,
                         bias=bias, bias_ci95_low=bl, bias_ci95_high=bh))
    severity = pd.DataFrame(rows)
    severity.to_csv(out / "v2_target_severity_audit.csv", index=False)

    rho_s, p_s = spearmanr(p["y"], p["signed_error"])
    rho_a, p_a = spearmanr(p["y"], p["abs_error"])
    pd.DataFrame([
        {"analysis":"observed_coverage_vs_signed_error","spearman_rho":rho_s,"p_value":p_s},
        {"analysis":"observed_coverage_vs_absolute_error","spearman_rho":rho_a,"p_value":p_a},
    ]).to_csv(out / "v2_target_error_correlations.csv", index=False)
    pd.crosstab(p["income_group"], p["target_quartile"], margins=True).to_csv(out / "v2_income_by_target_quartile.csv")

    rho, pv = spearmanr(p["true_deficit"], p["pred_deficit"])
    rank = [{"metric":"deficit_rank_spearman","value":rho,"p_value":pv}]
    for frac in [0.10, 0.20, 0.25, 0.33]:
        k = int(np.ceil(frac * len(p)))
        truth = set(p.nlargest(k, "true_deficit")["iso3"])
        pred = set(p.nlargest(k, "pred_deficit")["iso3"])
        rank.append({"metric":f"top_{int(frac*100)}pct_deficit_recall","value":len(truth & pred)/k,"p_value":np.nan})
    pd.DataFrame(rank).to_csv(out / "v2_prioritization_rank_metrics.csv", index=False)

    cutrows, misses = [], []
    for cut in [25, 50, 75]:
        actual = p["y"] <= cut; flagged = p["pred"] <= cut
        tp = int((actual & flagged).sum()); fn = int((actual & ~flagged).sum()); fp = int((~actual & flagged).sum())
        cutrows.append({"coverage_threshold":cut,"n_actual_below_or_equal":int(actual.sum()),
                        "n_predicted_below_or_equal":int(flagged.sum()),"true_positive":tp,
                        "false_negative":fn,"false_positive":fp,
                        "sensitivity":tp/int(actual.sum()) if actual.sum() else np.nan,
                        "precision":tp/int(flagged.sum()) if flagged.sum() else np.nan})
        m = p[actual & ~flagged].copy(); m["threshold"] = cut
        misses.append(m[["iso3","country","region","income_group","year","unit","y","pred","signed_error","threshold"]])
    pd.DataFrame(cutrows).to_csv(out / "v2_service_deficit_threshold_audit.csv", index=False)
    pd.concat(misses, ignore_index=True).to_csv(out / "v2_service_deficit_missed_cases.csv", index=False)
    p.to_csv(out / "v2_decision_audit_country_rows.csv", index=False)

    # Severity figure
    f, ax = plt.subplots(figsize=(7,4.8))
    x = np.arange(4); labels = ["Lowest\ncoverage", "Q2", "Q3", "Highest\ncoverage"]
    ax.bar(x, severity["mae"].values, hatch=["///","xx","..","\\\\"])
    ax.errorbar(x, severity["mae"].values,
                yerr=[severity["mae"].values-severity["mae_ci95_low"].values,
                      severity["mae_ci95_high"].values-severity["mae"].values],
                fmt="none", capsize=4)
    ax.set_xticks(x, labels); ax.set_ylabel("MAE (percentage points)")
    ax.set_xlabel("Observed collection-coverage quartile")
    f.tight_layout(); f.savefig(figdir / "Fig7_Target_Severity_Audit.pdf"); f.savefig(figdir / "Fig7_Target_Severity_Audit.png", dpi=300); plt.close(f)

    # Deficit-ranking figure
    f, ax = plt.subplots(figsize=(6.6,5.4))
    ax.scatter(p["true_deficit"], p["pred_deficit"], s=26)
    lo = min(p["true_deficit"].min(), p["pred_deficit"].min()); hi = max(p["true_deficit"].max(), p["pred_deficit"].max())
    ax.plot([lo,hi],[lo,hi],linestyle="--",linewidth=1)
    ax.set_xlabel("Observed service deficit (100 - coverage)"); ax.set_ylabel("Predicted service deficit")
    ax.text(.04,.95,rf"Spearman $\rho$ = {rho:.3f}", transform=ax.transAxes, va="top")
    f.tight_layout(); f.savefig(figdir / "Fig8_Deficit_Prioritization.pdf"); f.savefig(figdir / "Fig8_Deficit_Prioritization.png", dpi=300); plt.close(f)

    lock = {
        "n":len(p), "signed_error_rho":float(rho_s), "signed_error_p":float(p_s),
        "abs_error_rho":float(rho_a), "abs_error_p":float(p_a),
        "deficit_rank_rho":float(rho), "deficit_rank_p":float(pv),
        "pred_min":float(p["pred"].min()), "true_min":float(p["y"].min()),
        "top10_recall":rank[1]["value"], "top20_recall":rank[2]["value"],
        "top25_recall":rank[3]["value"], "top33_recall":rank[4]["value"],
    }
    (out / "V2_UPGRADE_NUMERICAL_LOCK.txt").write_text("\n".join(f"{k}={v}" for k,v in lock.items())+"\n", encoding="utf-8")
    print("PAPER19 reviewer-stage audit complete")
    for k, v in lock.items(): print(f"{k}={v}")

if __name__ == "__main__":
    main()
