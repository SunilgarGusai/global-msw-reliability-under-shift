\
import numpy as np
import pandas as pd

from sklearn.covariance import LedoitWolf
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from config import (
    DATA_PROCESSED, OUT_RESULTS, OUT_TABLES,
    SEED, ALPHA, CAL_FRAC, INCOME_ORDER
)
from common import FEATURES, checkpoint, finite_quantile, regression_metrics

def make_linear():
    return Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("model", Ridge(alpha=1.0)),
    ])

def split_source(source_df, seed):
    rng = np.random.default_rng(seed)
    idx = np.arange(len(source_df))
    rng.shuffle(idx)
    n_cal = max(20, int(round(CAL_FRAC * len(source_df))))
    n_cal = min(n_cal, len(source_df) - 10)
    return source_df.iloc[idx[n_cal:]].copy(), source_df.iloc[idx[:n_cal]].copy()

def fit_ood(train_df):
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    X = imputer.fit_transform(train_df[FEATURES])
    Z = scaler.fit_transform(X)
    cov = LedoitWolf().fit(Z)
    return imputer, scaler, cov

def ood_score(df, imputer, scaler, cov):
    X = imputer.transform(df[FEATURES])
    Z = scaler.transform(X)
    return np.sqrt(np.maximum(cov.mahalanobis(Z), 0.0))

def conformal_fold(source_df, test_df, fold_seed):
    proper, cal = split_source(source_df, fold_seed)

    model = make_linear()
    model.fit(proper[FEATURES], proper["y"])
    cal_pred = np.clip(model.predict(cal[FEATURES]), 0, 100)
    test_pred = np.clip(model.predict(test_df[FEATURES]), 0, 100)

    imputer, scaler, cov = fit_ood(proper)
    cal_ood = ood_score(cal, imputer, scaler, cov)
    test_ood = ood_score(test_df, imputer, scaler, cov)

    # Global split-conformal.
    cal_res = np.abs(cal["y"].to_numpy() - cal_pred)
    q_global = finite_quantile(cal_res, ALPHA)

    # Scaled split-conformal: local width expands with OOD score.
    cal_scale = 1.0 + cal_ood
    score_scaled = cal_res / cal_scale
    q_scaled = finite_quantile(score_scaled, ALPHA)
    test_scale = 1.0 + test_ood

    # Mondrian income-group conformal, fallback to global if calibration n<5.
    q_income = {}
    for income in INCOME_ORDER:
        mask = cal["income_group"].astype(str).eq(income).to_numpy()
        if mask.sum() >= 5:
            q_income[income] = finite_quantile(cal_res[mask], ALPHA)
        else:
            q_income[income] = q_global

    out = test_df[["iso3", "country", "region", "income_group", "year", "y"]].copy()
    out["pred"] = test_pred
    out["ood"] = test_ood

    out["lo_global"] = np.maximum(0, test_pred - q_global)
    out["hi_global"] = np.minimum(100, test_pred + q_global)

    out["lo_scaled"] = np.maximum(0, test_pred - q_scaled * test_scale)
    out["hi_scaled"] = np.minimum(100, test_pred + q_scaled * test_scale)

    qrow = out["income_group"].map(q_income).fillna(q_global).to_numpy(float)
    out["lo_income"] = np.maximum(0, test_pred - qrow)
    out["hi_income"] = np.minimum(100, test_pred + qrow)

    # Thresholds are learned ONLY from calibration OOD.
    for q in [0.50, 0.60, 0.70, 0.80, 0.90]:
        thr = float(np.quantile(cal_ood, q))
        out[f"retain_global_q{int(q*100)}"] = (test_ood <= thr).astype(int)

    # Equalized retention policy is evaluated separately at each target retention;
    # this is diagnostic, not a deployable rule because it requires a batch.
    for q in [0.50, 0.60, 0.70, 0.80]:
        out[f"retain_equal_income_q{int(q*100)}"] = 0
        for income, idx in out.groupby("income_group").groups.items():
            idx = list(idx)
            n_keep = max(1, int(round(q * len(idx)))) if len(idx) else 0
            keep = out.loc[idx].sort_values("ood").head(n_keep).index
            out.loc[keep, f"retain_equal_income_q{int(q*100)}"] = 1

    return out

def interval_stats(df, lo, hi, retain_col=None):
    x = df if retain_col is None else df[df[retain_col] == 1]
    if len(x) == 0:
        return {
            "n": 0, "retention": 0.0, "mae": np.nan, "bias": np.nan,
            "coverage": np.nan, "mean_width": np.nan
        }
    cov = ((x["y"] >= x[lo]) & (x["y"] <= x[hi])).mean()
    return {
        "n": int(len(x)),
        "retention": float(len(x) / len(df)),
        "mae": float(np.mean(np.abs(x["pred"] - x["y"]))),
        "bias": float(np.mean(x["pred"] - x["y"])),
        "coverage": float(cov),
        "mean_width": float(np.mean(x[hi] - x[lo])),
    }

def main():
    df = pd.read_csv(DATA_PROCESSED / "primary_collection_cohort.csv")
    pieces = []
    for i, region in enumerate(sorted(df["region"].dropna().unique()), start=1):
        source = df[df["region"] != region].copy()
        test = df[df["region"] == region].copy()
        out = conformal_fold(source, test, SEED + i)
        out["held_region"] = region
        pieces.append(out)

    pred = pd.concat(pieces, ignore_index=True)
    pred.to_csv(OUT_RESULTS / "primary_conformal_predictions.csv", index=False)

    rows = []
    intervals = {
        "global": ("lo_global", "hi_global"),
        "scaled": ("lo_scaled", "hi_scaled"),
        "income_mondrian": ("lo_income", "hi_income"),
    }
    for method, (lo, hi) in intervals.items():
        r = interval_stats(pred, lo, hi)
        r.update({"interval_method": method, "policy": "all"})
        rows.append(r)
        for q in [50, 60, 70, 80, 90]:
            rc = f"retain_global_q{q}"
            if rc in pred:
                rr = interval_stats(pred, lo, hi, rc)
                rr.update({"interval_method": method, "policy": rc})
                rows.append(rr)
        for q in [50, 60, 70, 80]:
            rc = f"retain_equal_income_q{q}"
            rr = interval_stats(pred, lo, hi, rc)
            rr.update({"interval_method": method, "policy": rc})
            rows.append(rr)

    summary = pd.DataFrame(rows)
    summary.to_csv(OUT_TABLES / "conformal_selective_summary.csv", index=False)

    # Group audit at the diagnostically useful 60% equal-income policy.
    group_rows = []
    policy = "retain_equal_income_q60"
    for income, p in pred.groupby("income_group"):
        for method, (lo, hi) in intervals.items():
            r = interval_stats(p, lo, hi, policy)
            r.update({
                "group_type": "income_group",
                "group": income,
                "interval_method": method,
                "policy": policy,
            })
            group_rows.append(r)
    pd.DataFrame(group_rows).to_csv(
        OUT_TABLES / "conformal_income_audit.csv", index=False
    )

    checkpoint("04_conformal_selective", {
        "n": len(pred),
        "nominal_coverage": 1 - ALPHA,
    })
    print(summary.to_string(index=False))
    print("PHASE 04 COMPLETE")

if __name__ == "__main__":
    main()
