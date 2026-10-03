\
import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.compose import TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import LeaveOneGroupOut, GridSearchCV, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from common import FEATURES, regression_metrics
from config import SEED, N_JOBS

def candidate_specs():
    common_steps = [("impute", SimpleImputer(strategy="median"))]
    return {
        "dummy_mean": {
            "estimator": Pipeline(common_steps + [("model", DummyRegressor(strategy="mean"))]),
            "param_grid": {},
        },
        "linear": {
            "estimator": Pipeline(common_steps + [
                ("scale", StandardScaler()),
                ("model", LinearRegression()),
            ]),
            "param_grid": {},
        },
        "ridge": {
            "estimator": Pipeline(common_steps + [
                ("scale", StandardScaler()),
                ("model", Ridge()),
            ]),
            "param_grid": {"model__alpha": [0.1, 1.0, 10.0, 100.0]},
        },
        "random_forest": {
            "estimator": Pipeline(common_steps + [
                ("model", RandomForestRegressor(
                    random_state=SEED,
                    n_estimators=500,
                    n_jobs=N_JOBS,
                )),
            ]),
            "param_grid": {
                "model__max_depth": [None, 3, 5],
                "model__min_samples_leaf": [2, 4, 6],
                "model__max_features": [0.7, 1.0],
            },
        },
        "hist_gbr": {
            "estimator": Pipeline(common_steps + [
                ("model", HistGradientBoostingRegressor(
                    random_state=SEED,
                    max_iter=300,
                )),
            ]),
            "param_grid": {
                "model__learning_rate": [0.03, 0.05, 0.10],
                "model__max_leaf_nodes": [7, 15],
                "model__l2_regularization": [0.0, 1.0, 10.0],
            },
        },
    }

def fit_inner_tuned(spec, X, y, seed=SEED):
    est = clone(spec["estimator"])
    grid = spec.get("param_grid") or {}
    if not grid:
        est.fit(X, y)
        return est, {}
    n_splits = min(5, max(3, len(y) // 20))
    cv = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    gs = GridSearchCV(
        est,
        grid,
        scoring="neg_mean_absolute_error",
        cv=cv,
        n_jobs=N_JOBS,
        refit=True,
    )
    gs.fit(X, y)
    return gs.best_estimator_, gs.best_params_

def logo_predictions(df, target_col="y", model_names=None):
    specs = candidate_specs()
    if model_names is None:
        model_names = list(specs)

    logo = LeaveOneGroupOut()
    X = df[FEATURES]
    y = df[target_col].astype(float)
    groups = df["region"].astype(str)

    all_pred = []
    tuning_rows = []

    for fold_id, (tr_idx, te_idx) in enumerate(logo.split(X, y, groups), start=1):
        held_region = str(groups.iloc[te_idx].iloc[0])
        Xtr, Xte = X.iloc[tr_idx], X.iloc[te_idx]
        ytr, yte = y.iloc[tr_idx], y.iloc[te_idx]

        for model_name in model_names:
            model, best_params = fit_inner_tuned(
                specs[model_name], Xtr, ytr, seed=SEED + fold_id
            )
            pred = np.clip(model.predict(Xte), 0.0, 100.0)
            z = df.iloc[te_idx][["iso3", "country", "region", "income_group", "year", "unit"]].copy() \
                if "unit" in df.columns else df.iloc[te_idx][["iso3", "country", "region", "income_group", "year"]].copy()
            z["fold"] = fold_id
            z["model"] = model_name
            z["y"] = yte.to_numpy()
            z["pred"] = pred
            z["abs_error"] = np.abs(z["pred"] - z["y"])
            z["signed_error"] = z["pred"] - z["y"]
            all_pred.append(z)
            tuning_rows.append({
                "fold": fold_id,
                "held_region": held_region,
                "model": model_name,
                "best_params": str(best_params),
            })

    return pd.concat(all_pred, ignore_index=True), pd.DataFrame(tuning_rows)

def summarize_predictions(pred):
    rows = []
    for model, p in pred.groupby("model"):
        m = regression_metrics(p["y"], p["pred"])
        m["model"] = model
        rows.append(m)
    return pd.DataFrame(rows).sort_values("mae")
