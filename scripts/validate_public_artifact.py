from __future__ import annotations

from pathlib import Path
import hashlib
import math
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md", "QUICKSTART.md", "CITATION.cff", "LICENSE", "THIRD_PARTY_LICENSES.md",
    "environment.yml", "requirements.txt", "REPOSITORY_MANIFEST.csv", "PUBLIC_SHA256SUMS.txt",
    "docs/METHOD_PROTOCOL.md", "docs/FROZEN_RESULTS.md", "docs/DATA_PROVENANCE.md",
    "docs/REPRODUCIBILITY.md", "docs/CLAIM_BOUNDARIES.md", "docs/RESULTS_FREEZE.md",
    "docs/RELEASE_POLICY.md", "docs/assets/repository-banner.svg",
    "results/verified_baseline/results/primary_logo_predictions.csv",
    "results/verified_baseline/results/primary_conformal_predictions.csv",
    "results/verified_baseline/tables/primary_model_summary.csv",
    "results/verified_baseline/tables/primary_subgroup_metrics.csv",
    "results/v2_upgrade/v2_target_severity_audit.csv",
    "results/v2_upgrade/v2_prioritization_rank_metrics.csv",
    "pipeline/scripts/11_oof_decision_audit.py",
]

def near(a,b,tol=1e-9):
    if not math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=tol):
        raise AssertionError(f"Expected {b}, found {a}")

def verify_sha_manifest():
    manifest=ROOT/"PUBLIC_SHA256SUMS.txt"
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split("  ",1)
        p=ROOT/rel
        if not p.is_file():
            raise AssertionError(f"Manifest file missing: {rel}")
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != digest:
            raise AssertionError(f"SHA-256 mismatch: {rel}")

def main():
    for rel in REQUIRED:
        if not (ROOT/rel).exists():
            raise AssertionError(f"Required repository artifact missing: {rel}")

    pred=pd.read_csv(ROOT/"results/verified_baseline/results/primary_logo_predictions.csv")
    if pred.shape[0] != 770: raise AssertionError(f"Expected 770 point-prediction rows, found {len(pred)}")
    if set(pred["model"]) != {"dummy_mean","linear","ridge","random_forest","hist_gbr"}: raise AssertionError("Unexpected model set")
    lin=pred[pred.model=="linear"].copy()
    if len(lin)!=154 or lin.iso3.nunique()!=154: raise AssertionError("Linear LORO cohort is not 154 unique countries")
    if lin.region.nunique()!=7: raise AssertionError("Expected seven held-region groups")

    models=pd.read_csv(ROOT/"results/verified_baseline/tables/primary_model_summary.csv").set_index("model")
    near(models.loc["linear","mae"],13.981872987542106)
    near(models.loc["linear","rmse"],18.913203517654964)
    near(models.loc["linear","r2"],0.5625520466303008)

    sg=pd.read_csv(ROOT/"results/verified_baseline/tables/primary_subgroup_metrics.csv")
    sg=sg[(sg.model=="linear") & (sg.group_type=="income_group")].set_index("group")
    near(sg.loc["Low income","mae"],25.466207351326837)
    near(sg.loc["Low income","bias"],17.701214390261097)
    near(sg.loc["High income","mae"],6.460379317391663)

    cp=pd.read_csv(ROOT/"results/verified_baseline/results/primary_conformal_predictions.csv")
    cov=(cp.y>=cp.lo_global)&(cp.y<=cp.hi_global)
    near(cov.mean(),0.8506493506493507)
    near(cov[cp.income_group=="Low income"].mean(),0.5384615384615384)
    near(cov[cp.income_group=="High income"].mean(),0.9791666666666666)
    rho,p=spearmanr(cp.ood,(cp.pred-cp.y).abs())
    near(rho,0.03523236690524286)
    near(p,0.6644375336370665)

    sev=pd.read_csv(ROOT/"results/v2_upgrade/v2_target_severity_audit.csv").set_index("target_quartile")
    near(sev.loc["Q1_lowest_coverage","mae"],23.724859145807)
    near(sev.loc["Q1_lowest_coverage","bias"],23.202126667851758)

    rank=pd.read_csv(ROOT/"results/v2_upgrade/v2_prioritization_rank_metrics.csv").set_index("metric")
    near(rank.loc["deficit_rank_spearman","value"],0.8074889754750134)
    near(rank.loc["top_10pct_deficit_recall","value"],0.375)

    verify_sha_manifest()
    print("Repository structure: PASS")
    print("Frozen LORO evidence: PASS")
    print("Income reliability invariants: PASS")
    print("Conformal/OOD invariants: PASS")
    print("V2 decision-audit invariants: PASS")
    print("Public SHA-256 manifest: PASS")

if __name__ == "__main__":
    main()
