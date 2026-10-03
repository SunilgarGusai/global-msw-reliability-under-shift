\
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.stats import spearmanr, pearsonr, binomtest, norm
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score

from config import (
    DATA_PROCESSED, OUT_RESULTS, OUT_TABLES, OUT_FIGURES,
    REPRO, CHECKPOINTS, SEED
)
from common import FEATURES, checkpoint, save_json

B = 20000
RNG = np.random.default_rng(SEED + 902)

def qci(x, alpha=0.05):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return (np.nan, np.nan)
    return tuple(np.quantile(x, [alpha/2, 1-alpha/2]))

def wilson_ci(k, n, alpha=0.05):
    if n == 0:
        return (np.nan, np.nan)
    z = norm.ppf(1-alpha/2)
    p = k/n
    den = 1 + z*z/n
    cen = (p + z*z/(2*n))/den
    half = z*math.sqrt((p*(1-p)/n)+(z*z/(4*n*n)))/den
    return max(0.0, cen-half), min(1.0, cen+half)

def bh_adjust(pvals):
    p = np.asarray(pvals, dtype=float)
    order = np.argsort(p)
    ranked = p[order]
    adj = np.empty_like(ranked)
    m = len(p)
    running = 1.0
    for i in range(m-1, -1, -1):
        val = ranked[i] * m / (i+1)
        running = min(running, val)
        adj[i] = running
    out = np.empty_like(adj)
    out[order] = np.minimum(adj, 1.0)
    return out

def bootstrap_mean_ci(values, B=B):
    x = np.asarray(values, dtype=float)
    n = len(x)
    boots = np.empty(B)
    for b in range(B):
        boots[b] = RNG.choice(x, size=n, replace=True).mean()
    return float(x.mean()), *qci(boots)

def bootstrap_metric_ci(y, pred, metric="mae", B=B):
    y = np.asarray(y, dtype=float)
    pred = np.asarray(pred, dtype=float)
    n = len(y)
    boots = np.empty(B)
    for b in range(B):
        idx = RNG.integers(0, n, n)
        yy, pp = y[idx], pred[idx]
        if metric == "mae":
            val = np.mean(np.abs(pp-yy))
        elif metric == "bias":
            val = np.mean(pp-yy)
        elif metric == "rmse":
            val = np.sqrt(np.mean((pp-yy)**2))
        elif metric == "r2":
            den = np.sum((yy-yy.mean())**2)
            val = np.nan if den == 0 else 1 - np.sum((yy-pp)**2)/den
        else:
            raise ValueError(metric)
        boots[b] = val
    if metric == "mae":
        obs = np.mean(np.abs(pred-y))
    elif metric == "bias":
        obs = np.mean(pred-y)
    elif metric == "rmse":
        obs = np.sqrt(np.mean((pred-y)**2))
    else:
        den = np.sum((y-y.mean())**2)
        obs = 1 - np.sum((y-pred)**2)/den
    lo, hi = qci(boots)
    return float(obs), float(lo), float(hi)

def bootstrap_group_contrast(a, b, metric="abs", B=B):
    # Returns mean(A)-mean(B), stratified bootstrap CI.
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    obs = float(a.mean() - b.mean())
    boots = np.empty(B)
    for i in range(B):
        aa = RNG.choice(a, size=len(a), replace=True)
        bb = RNG.choice(b, size=len(b), replace=True)
        boots[i] = aa.mean() - bb.mean()
    lo, hi = qci(boots)
    return obs, float(lo), float(hi)

def permutation_mean_diff(a, b, B=B):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    obs = abs(a.mean()-b.mean())
    pool = np.concatenate([a,b])
    n_a = len(a)
    ge = 0
    for _ in range(B):
        perm = RNG.permutation(pool)
        diff = abs(perm[:n_a].mean()-perm[n_a:].mean())
        ge += diff >= obs
    return float((ge+1)/(B+1))

def interval_cols(method):
    if method == "global":
        return "lo_global", "hi_global"
    if method == "scaled":
        return "lo_scaled", "hi_scaled"
    if method == "income_mondrian":
        return "lo_income", "hi_income"
    raise ValueError(method)

def primary_statistical_audit():
    model_summary = pd.read_csv(OUT_TABLES / "primary_model_summary.csv")
    best = str(model_summary.iloc[0]["model"])
    pred = pd.read_csv(OUT_RESULTS / "primary_logo_predictions.csv")
    p = pred[pred["model"] == best].copy()
    p["abs_error"] = np.abs(p["pred"]-p["y"])
    p["signed_error"] = p["pred"]-p["y"]

    # Overall bootstrap CIs.
    overall_rows = []
    for metric in ["mae","rmse","r2","bias"]:
        est, lo, hi = bootstrap_metric_ci(p["y"], p["pred"], metric)
        overall_rows.append({
            "model": best, "metric": metric,
            "estimate": est, "ci95_low": lo, "ci95_high": hi
        })
    pd.DataFrame(overall_rows).to_csv(
        OUT_TABLES / "phaseB2_primary_overall_ci.csv", index=False
    )

    # Income group CIs.
    group_rows = []
    for income, g in p.groupby("income_group"):
        for metric in ["mae","bias"]:
            est, lo, hi = bootstrap_metric_ci(g["y"], g["pred"], metric)
            group_rows.append({
                "income_group": income, "n": len(g), "metric": metric,
                "estimate": est, "ci95_low": lo, "ci95_high": hi
            })
    pd.DataFrame(group_rows).to_csv(
        OUT_TABLES / "phaseB2_income_metric_ci.csv", index=False
    )

    # Formal low-vs-high contrasts.
    low = p[p["income_group"] == "Low income"]
    high = p[p["income_group"] == "High income"]
    contrast_rows = []
    for col, label in [("abs_error","mae_gap_low_minus_high"),
                       ("signed_error","bias_gap_low_minus_high")]:
        obs, lo, hi = bootstrap_group_contrast(low[col], high[col])
        perm_p = permutation_mean_diff(low[col], high[col])
        contrast_rows.append({
            "contrast": label,
            "low_n": len(low), "high_n": len(high),
            "estimate": obs, "ci95_low": lo, "ci95_high": hi,
            "permutation_p_two_sided": perm_p,
        })
    pd.DataFrame(contrast_rows).to_csv(
        OUT_TABLES / "phaseB2_low_high_contrasts.csv", index=False
    )

    # Measurement-unit audit + income x unit cross-tab.
    unit_rows = []
    for unit, g in p.groupby("unit"):
        for metric in ["mae","bias"]:
            est, lo, hi = bootstrap_metric_ci(g["y"], g["pred"], metric)
            unit_rows.append({
                "unit": unit, "n": len(g), "metric": metric,
                "estimate": est, "ci95_low": lo, "ci95_high": hi
            })
    pd.DataFrame(unit_rows).to_csv(
        OUT_TABLES / "phaseB2_measurement_unit_ci.csv", index=False
    )

    cross = pd.crosstab(p["income_group"], p["unit"], margins=True)
    cross.to_csv(OUT_TABLES / "phaseB2_income_by_measurement_unit.csv")

    # Unit contrasts.
    ucontr = []
    units = sorted(p["unit"].dropna().unique())
    for a, b in [("PT_HH","PT_MSW"), ("PT_POP","PT_MSW"), ("PT_HH","PT_POP")]:
        if a in units and b in units:
            aa = p.loc[p["unit"]==a, "abs_error"]
            bb = p.loc[p["unit"]==b, "abs_error"]
            obs, lo, hi = bootstrap_group_contrast(aa, bb)
            ucontr.append({
                "contrast": f"{a}_minus_{b}_abs_error",
                "n_a":len(aa),"n_b":len(bb),
                "estimate":obs,"ci95_low":lo,"ci95_high":hi,
                "permutation_p_two_sided":permutation_mean_diff(aa,bb)
            })
    pd.DataFrame(ucontr).to_csv(
        OUT_TABLES / "phaseB2_measurement_unit_contrasts.csv", index=False
    )

    # Error vs year.
    rho, rho_p = spearmanr(p["year"], p["abs_error"], nan_policy="omit")
    pd.DataFrame([{
        "analysis":"observation_year_vs_abs_error",
        "spearman_rho":rho, "p_value":rho_p
    }]).to_csv(OUT_TABLES / "phaseB2_recency_error_association.csv", index=False)

    return best, p

def conformal_audit(best, p):
    c = pd.read_csv(OUT_RESULTS / "primary_conformal_predictions.csv")
    # Attach unit if not present.
    if "unit" not in c.columns:
        c = c.merge(p[["iso3","unit"]], on="iso3", how="left", validate="one_to_one")
    c["abs_error"] = np.abs(c["pred"]-c["y"])

    coverage_rows = []
    pvals = []
    row_refs = []

    for method in ["global","scaled","income_mondrian"]:
        lo, hi = interval_cols(method)
        for group_type in ["ALL","income_group","region","unit"]:
            if group_type == "ALL":
                iterable = [("ALL", c)]
            else:
                iterable = list(c.groupby(group_type, dropna=False))
            for group, g in iterable:
                covered = ((g["y"] >= g[lo]) & (g["y"] <= g[hi]))
                k, n = int(covered.sum()), int(len(g))
                lci, uci = wilson_ci(k,n)
                bp = float(binomtest(k,n,p=0.90,alternative="less").pvalue) if n else np.nan
                row = {
                    "interval_method":method,
                    "group_type":group_type,
                    "group":group,
                    "n":n,
                    "covered":k,
                    "coverage":k/n if n else np.nan,
                    "wilson95_low":lci,
                    "wilson95_high":uci,
                    "mean_width":float(np.mean(g[hi]-g[lo])) if n else np.nan,
                    "binomial_p_less_than_0_90":bp,
                }
                coverage_rows.append(row)
                pvals.append(bp)
                row_refs.append(len(coverage_rows)-1)

    adj = bh_adjust([1.0 if not np.isfinite(x) else x for x in pvals])
    for idx, q in zip(row_refs, adj):
        coverage_rows[idx]["fdr_bh_q"] = float(q)

    covdf = pd.DataFrame(coverage_rows)
    covdf.to_csv(OUT_TABLES / "phaseB2_conformal_coverage_audit.csv", index=False)

    # OOD usefulness.
    ood_rows = []
    for group_type in ["ALL","income_group","region","unit"]:
        iterable = [("ALL", c)] if group_type=="ALL" else list(c.groupby(group_type, dropna=False))
        for group,g in iterable:
            if len(g) < 4:
                continue
            rho, rp = spearmanr(g["ood"], g["abs_error"], nan_policy="omit")
            r, pp = pearsonr(g["ood"], g["abs_error"])
            threshold = float(c["abs_error"].quantile(.75))
            ybad = (g["abs_error"] >= threshold).astype(int)
            auc = np.nan
            ap = np.nan
            if ybad.nunique() == 2:
                auc = roc_auc_score(ybad, g["ood"])
                ap = average_precision_score(ybad, g["ood"])
            ood_rows.append({
                "group_type":group_type, "group":group, "n":len(g),
                "spearman_rho":rho, "spearman_p":rp,
                "pearson_r":r, "pearson_p":pp,
                "high_error_threshold_global_q75":threshold,
                "high_error_auc":auc, "high_error_average_precision":ap
            })
    pd.DataFrame(ood_rows).to_csv(
        OUT_TABLES / "phaseB2_ood_error_audit.csv", index=False
    )

    # Selective policy fairness audit.
    policy_cols = [x for x in c.columns if x.startswith("retain_")]
    sel_rows = []
    for policy in policy_cols:
        for method in ["global","scaled","income_mondrian"]:
            lo, hi = interval_cols(method)
            for group_type in ["ALL","income_group","region"]:
                iterable = [("ALL", c)] if group_type=="ALL" else list(c.groupby(group_type, dropna=False))
                for group,g in iterable:
                    r = g[g[policy] == 1]
                    coverage = np.nan
                    if len(r):
                        coverage = float(((r["y"]>=r[lo])&(r["y"]<=r[hi])).mean())
                    sel_rows.append({
                        "policy":policy,
                        "interval_method":method,
                        "group_type":group_type,
                        "group":group,
                        "n_total":len(g),
                        "n_retained":len(r),
                        "retention":len(r)/len(g) if len(g) else np.nan,
                        "retained_mae":float(r["abs_error"].mean()) if len(r) else np.nan,
                        "retained_bias":float((r["pred"]-r["y"]).mean()) if len(r) else np.nan,
                        "retained_coverage":coverage,
                        "retained_mean_width":float((r[hi]-r[lo]).mean()) if len(r) else np.nan,
                    })
    pd.DataFrame(sel_rows).to_csv(
        OUT_TABLES / "phaseB2_selective_policy_fairness.csv", index=False
    )

    return c, covdf

def coefficient_stability():
    df = pd.read_csv(DATA_PROCESSED / "primary_collection_cohort.csv")
    rows = []
    regions = sorted(df["region"].dropna().unique())

    for held in regions + ["FULL_SAMPLE"]:
        train = df.copy() if held=="FULL_SAMPLE" else df[df["region"] != held].copy()
        pipe = Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("model", LinearRegression()),
        ])
        pipe.fit(train[FEATURES], train["y"])
        coefs = pipe.named_steps["model"].coef_
        for feat, coef in zip(FEATURES, coefs):
            rows.append({
                "held_region":held,
                "n_train":len(train),
                "feature":feat,
                "standardized_coefficient":float(coef),
            })

    coefdf = pd.DataFrame(rows)
    coefdf.to_csv(OUT_TABLES / "phaseB2_linear_coefficient_stability.csv", index=False)

    summ = coefdf[coefdf["held_region"]!="FULL_SAMPLE"].groupby("feature")["standardized_coefficient"].agg(
        ["mean","std","min","max"]
    ).reset_index()
    summ.to_csv(OUT_TABLES / "phaseB2_linear_coefficient_summary.csv", index=False)
    return coefdf

def make_figures(best, p, c, covdf, coefdf):
    # Fig08: income MAE with bootstrap CIs.
    ci = pd.read_csv(OUT_TABLES / "phaseB2_income_metric_ci.csv")
    z = ci[ci["metric"]=="mae"].copy()
    order = ["Low income","Lower middle income","Upper middle income","High income"]
    z["ord"] = z["income_group"].map({x:i for i,x in enumerate(order)})
    z = z.sort_values("ord")
    plt.figure(figsize=(7.2,4.8))
    yerr = np.vstack([z["estimate"]-z["ci95_low"], z["ci95_high"]-z["estimate"]])
    plt.bar(z["income_group"], z["estimate"])
    plt.errorbar(np.arange(len(z)), z["estimate"], yerr=yerr, fmt="none", capsize=4)
    plt.ylabel("MAE (percentage points)")
    plt.xticks(rotation=20, ha="right")
    plt.title(f"Income-group held-region error with 95% bootstrap CI ({best})")
    plt.tight_layout()
    plt.savefig(OUT_FIGURES/"fig08_income_mae_bootstrap_ci.png",dpi=300,bbox_inches="tight")
    plt.savefig(OUT_FIGURES/"fig08_income_mae_bootstrap_ci.pdf",bbox_inches="tight")
    plt.close()

    # Fig09: global conformal coverage by income.
    cg = covdf[
        (covdf["interval_method"]=="global") &
        (covdf["group_type"]=="income_group")
    ].copy()
    cg["ord"] = cg["group"].map({x:i for i,x in enumerate(order)})
    cg = cg.sort_values("ord")
    plt.figure(figsize=(7.2,4.8))
    plt.bar(cg["group"], cg["coverage"])
    plt.axhline(.90, linestyle="--", linewidth=1)
    plt.ylim(0,1.05)
    plt.ylabel("Empirical 90% interval coverage")
    plt.xticks(rotation=20, ha="right")
    plt.title("Subgroup conformal coverage")
    plt.tight_layout()
    plt.savefig(OUT_FIGURES/"fig09_conformal_coverage_income.png",dpi=300,bbox_inches="tight")
    plt.savefig(OUT_FIGURES/"fig09_conformal_coverage_income.pdf",bbox_inches="tight")
    plt.close()

    # Fig10: OOD vs error.
    plt.figure(figsize=(6.6,4.7))
    plt.scatter(c["ood"], c["abs_error"], alpha=.75)
    plt.xlabel("Mahalanobis OOD score")
    plt.ylabel("Absolute prediction error")
    plt.title("Weak correspondence between covariate shift and prediction error")
    plt.tight_layout()
    plt.savefig(OUT_FIGURES/"fig10_ood_vs_error.png",dpi=300,bbox_inches="tight")
    plt.savefig(OUT_FIGURES/"fig10_ood_vs_error.pdf",bbox_inches="tight")
    plt.close()

    # Fig11: measurement-unit MAE.
    unitci = pd.read_csv(OUT_TABLES/"phaseB2_measurement_unit_ci.csv")
    uz = unitci[unitci["metric"]=="mae"].copy()
    plt.figure(figsize=(6.8,4.6))
    yerr=np.vstack([uz["estimate"]-uz["ci95_low"],uz["ci95_high"]-uz["estimate"]])
    plt.bar(uz["unit"],uz["estimate"])
    plt.errorbar(np.arange(len(uz)),uz["estimate"],yerr=yerr,fmt="none",capsize=4)
    plt.ylabel("MAE (percentage points)")
    plt.xlabel("Collection-coverage measurement basis")
    plt.title("Prediction error by measurement basis")
    plt.tight_layout()
    plt.savefig(OUT_FIGURES/"fig11_measurement_unit_mae.png",dpi=300,bbox_inches="tight")
    plt.savefig(OUT_FIGURES/"fig11_measurement_unit_mae.pdf",bbox_inches="tight")
    plt.close()

    # Fig12: coefficient stability.
    cc = coefdf[coefdf["held_region"]!="FULL_SAMPLE"].copy()
    feats = FEATURES
    means = [cc.loc[cc.feature==f,"standardized_coefficient"].mean() for f in feats]
    mins = [cc.loc[cc.feature==f,"standardized_coefficient"].min() for f in feats]
    maxs = [cc.loc[cc.feature==f,"standardized_coefficient"].max() for f in feats]
    err=np.vstack([np.array(means)-np.array(mins),np.array(maxs)-np.array(means)])
    plt.figure(figsize=(7.5,4.8))
    plt.bar(feats,means)
    plt.errorbar(np.arange(len(feats)),means,yerr=err,fmt="none",capsize=4)
    plt.axhline(0,linewidth=1)
    plt.ylabel("Standardized linear coefficient")
    plt.xticks(rotation=20,ha="right")
    plt.title("Coefficient stability across held-region training sets")
    plt.tight_layout()
    plt.savefig(OUT_FIGURES/"fig12_linear_coefficient_stability.png",dpi=300,bbox_inches="tight")
    plt.savefig(OUT_FIGURES/"fig12_linear_coefficient_stability.pdf",bbox_inches="tight")
    plt.close()

    # Fig13: low-income MAE robustness.
    rb = pd.read_csv(OUT_TABLES/"primary_robustness_summary.csv")
    rz = rb[rb["model"]==best].copy()
    keep = ["all","since_2015","since_2018","msw_weight_only"]
    rz = rz[rz["case"].isin(keep)]
    rz["ord"] = rz["case"].map({x:i for i,x in enumerate(keep)})
    rz=rz.sort_values("ord")
    plt.figure(figsize=(7.2,4.6))
    plt.bar(rz["case"],rz["low_mae"])
    plt.ylabel("Low-income MAE (percentage points)")
    plt.xticks(rotation=20,ha="right")
    plt.title("Low-income error persists across robustness definitions")
    plt.tight_layout()
    plt.savefig(OUT_FIGURES/"fig13_low_income_robustness.png",dpi=300,bbox_inches="tight")
    plt.savefig(OUT_FIGURES/"fig13_low_income_robustness.pdf",bbox_inches="tight")
    plt.close()

def write_scientific_lock(best, p, c, covdf):
    overall = pd.read_csv(OUT_TABLES/"phaseB2_primary_overall_ci.csv")
    inc = pd.read_csv(OUT_TABLES/"phaseB2_income_metric_ci.csv")
    contrast = pd.read_csv(OUT_TABLES/"phaseB2_low_high_contrasts.csv")
    unit = pd.read_csv(OUT_TABLES/"phaseB2_measurement_unit_ci.csv")
    ood = pd.read_csv(OUT_TABLES/"phaseB2_ood_error_audit.csv")
    rb = pd.read_csv(OUT_TABLES/"primary_robustness_summary.csv")

    def fmt_ci(df, metric):
        r=df[df.metric==metric].iloc[0]
        return f'{r.estimate:.2f} [{r.ci95_low:.2f}, {r.ci95_high:.2f}]'

    low_mae = inc[(inc.income_group=="Low income")&(inc.metric=="mae")].iloc[0]
    high_mae = inc[(inc.income_group=="High income")&(inc.metric=="mae")].iloc[0]
    low_bias = inc[(inc.income_group=="Low income")&(inc.metric=="bias")].iloc[0]
    gap = contrast[contrast.contrast=="mae_gap_low_minus_high"].iloc[0]

    cg = covdf[
        (covdf.interval_method=="global") &
        (covdf.group_type=="income_group")
    ]
    lowcov = cg[cg.group=="Low income"].iloc[0]
    highcov = cg[cg.group=="High income"].iloc[0]
    allcov = covdf[
        (covdf.interval_method=="global") &
        (covdf.group_type=="ALL")
    ].iloc[0]
    oall = ood[(ood.group_type=="ALL")&(ood.group=="ALL")].iloc[0]

    hh = unit[(unit.unit=="PT_HH")&(unit.metric=="mae")].iloc[0]
    msw = unit[(unit.unit=="PT_MSW")&(unit.metric=="mae")].iloc[0]

    mswrob = rb[(rb.case=="msw_weight_only")&(rb.model==best)]
    low_msw_mae = float(mswrob.low_mae.iloc[0]) if len(mswrob) else np.nan
    low_msw_bias = float(mswrob.low_bias.iloc[0]) if len(mswrob) else np.nan

    lines = [
        "# PAPER19 Scientific Result Lock — Phase B2",
        "",
        "## Status",
        "",
        "The numerical phase is considered scientifically interpretable only after this Phase B2 audit completes.",
        "",
        "## Primary held-region model",
        "",
        f"- Selected model by leave-one-region-out MAE: **{best}**.",
        f"- Overall MAE (95% bootstrap CI): **{fmt_ci(overall,'mae')}** percentage points.",
        f"- Overall RMSE (95% bootstrap CI): **{fmt_ci(overall,'rmse')}**.",
        f"- Overall R2 (95% bootstrap CI): **{fmt_ci(overall,'r2')}**.",
        "",
        "## Income-group reliability",
        "",
        f"- Low-income MAE: **{low_mae.estimate:.2f}** [{low_mae.ci95_low:.2f}, {low_mae.ci95_high:.2f}].",
        f"- High-income MAE: **{high_mae.estimate:.2f}** [{high_mae.ci95_low:.2f}, {high_mae.ci95_high:.2f}].",
        f"- Low-minus-high MAE gap: **{gap.estimate:.2f}** [{gap.ci95_low:.2f}, {gap.ci95_high:.2f}], permutation p={gap.permutation_p_two_sided:.6g}.",
        f"- Low-income mean signed error: **{low_bias.estimate:.2f}** [{low_bias.ci95_low:.2f}, {low_bias.ci95_high:.2f}] (positive = overestimation).",
        "",
        "## Conformal reliability",
        "",
        f"- Global nominal-90% interval empirical coverage: **{allcov.coverage:.3f}**.",
        f"- Low-income coverage: **{lowcov.coverage:.3f}**, Wilson 95% CI [{lowcov.wilson95_low:.3f}, {lowcov.wilson95_high:.3f}].",
        f"- High-income coverage: **{highcov.coverage:.3f}**, Wilson 95% CI [{highcov.wilson95_low:.3f}, {highcov.wilson95_high:.3f}].",
        "",
        "## OOD and abstention",
        "",
        f"- Overall Spearman association between Mahalanobis OOD score and absolute error: rho={oall.spearman_rho:.3f}, p={oall.spearman_p:.4g}.",
        "- Therefore, covariate-distance abstention must not be described as a generally effective error detector unless the selective-policy audit demonstrates otherwise.",
        "",
        "## Measurement heterogeneity",
        "",
        f"- Household-based coverage MAE: **{hh.estimate:.2f}** [{hh.ci95_low:.2f}, {hh.ci95_high:.2f}].",
        f"- MSW-weight coverage MAE: **{msw.estimate:.2f}** [{msw.ci95_low:.2f}, {msw.ci95_high:.2f}].",
        f"- In the MSW-weight-only robustness subset, low-income MAE remains **{low_msw_mae:.2f}** with bias **{low_msw_bias:.2f}**.",
        "",
        "## Manuscript claim lock",
        "",
        "1. Do **not** claim that abstention solves the fairness/reliability problem.",
        "2. Do **not** claim novelty for conformal prediction, OOD detection, or waste-management ML itself.",
        "3. The defensible contribution is a country-scale reliability audit under true geographic holdout using WAW 3.0, showing that apparently acceptable aggregate performance can coexist with severe subgroup error and interval undercoverage.",
        "4. Measurement-basis heterogeneity must be discussed as a contributor, not hidden.",
        "5. The persistence of low-income error in recency and MSW-weight-only robustness subsets supports—but does not prove—a broader data-support/generalization problem.",
        "6. The paper should frame abstention as a decision-support safeguard whose usefulness is conditional and can itself become inequitable when uncertainty scores poorly track error.",
        "",
        "## Recommended manuscript direction",
        "",
        "**Reliability Gaps and the Limits of Abstention in Global Municipal Waste Service Prediction**",
        "",
        "Alternative title preserving the original question framing:",
        "",
        "**When Should Environmental AI Abstain? Reliability Gaps in Global Municipal Waste Service Prediction**",
    ]
    path = REPRO/"PHASE_B2_SCIENTIFIC_LOCK.md"
    path.write_text("\n".join(lines),encoding="utf-8")
    return path

def main():
    best, p = primary_statistical_audit()
    c, covdf = conformal_audit(best, p)
    coefdf = coefficient_stability()
    make_figures(best, p, c, covdf, coefdf)
    lock = write_scientific_lock(best, p, c, covdf)

    checkpoint("09_statistical_audit", {
        "best_model": best,
        "bootstrap_replicates": B,
        "scientific_lock": str(lock),
    })
    print(f"BEST MODEL: {best}")
    print(f"BOOTSTRAP REPLICATES: {B}")
    print(f"SCIENTIFIC LOCK: {lock}")
    print("PHASE 09 COMPLETE")

if __name__ == "__main__":
    main()
