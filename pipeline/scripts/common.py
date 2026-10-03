\
import json
import math
import os
import platform
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from config import (
    SEED, ROOT, DATA_PROCESSED, OUT_RESULTS, OUT_TABLES, LOGS, CHECKPOINTS
)

def set_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)

def checkpoint(name, payload=None):
    CHECKPOINTS.mkdir(parents=True, exist_ok=True)
    p = CHECKPOINTS / f"{name}.done.json"
    obj = {"phase": name, "status": "done"}
    if payload:
        obj.update(payload)
    p.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")
    return p

def save_json(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")

def save_csv(df, path, index=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)

def finite_quantile(scores, alpha=0.10):
    """
    Split-conformal finite-sample quantile:
      kth order statistic with k = ceil((n+1)*(1-alpha)).
    """
    x = np.asarray(scores, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return np.nan
    k = int(np.ceil((len(x) + 1) * (1 - alpha)))
    k = max(1, min(k, len(x)))
    return float(np.sort(x)[k - 1])

def regression_metrics(y_true, y_pred):
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return {
        "n": int(len(y_true)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)) if len(np.unique(y_true)) > 1 else np.nan,
        "bias": float(np.mean(y_pred - y_true)),
    }

def current_environment():
    import numpy
    import pandas
    import scipy
    import sklearn
    import matplotlib
    import requests
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": numpy.__version__,
        "pandas": pandas.__version__,
        "scipy": scipy.__version__,
        "sklearn": sklearn.__version__,
        "matplotlib": matplotlib.__version__,
        "requests": requests.__version__,
    }

def safe_group_metrics(df, group_col, y_col="y", pred_col="pred"):
    rows = []
    for g, part in df.groupby(group_col, dropna=False):
        m = regression_metrics(part[y_col], part[pred_col])
        m[group_col] = g
        rows.append(m)
    return pd.DataFrame(rows)

def add_engineered_features(df):
    out = df.copy()
    # Do not impute here. Imputation must happen inside each training fold.
    out["log_gdp_ppp_pc"] = np.where(
        pd.to_numeric(out["gdp_ppp_pc"], errors="coerce").notna(),
        np.log1p(pd.to_numeric(out["gdp_ppp_pc"], errors="coerce")),
        np.nan,
    )
    out["urban_frac"] = pd.to_numeric(out["urban_pct"], errors="coerce") / 100.0
    out["log_population"] = np.where(
        pd.to_numeric(out["population"], errors="coerce").notna(),
        np.log1p(pd.to_numeric(out["population"], errors="coerce")),
        np.nan,
    )
    out["log_pop_density"] = np.where(
        pd.to_numeric(out["pop_density"], errors="coerce").notna(),
        np.log1p(pd.to_numeric(out["pop_density"], errors="coerce")),
        np.nan,
    )
    return out

FEATURES = ["log_gdp_ppp_pc", "urban_frac", "log_population", "log_pop_density"]
