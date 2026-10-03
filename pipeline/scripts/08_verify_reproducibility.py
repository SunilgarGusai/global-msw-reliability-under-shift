\
import hashlib
import json
from pathlib import Path

import pandas as pd

from config import ROOT, DATA_PROCESSED, OUT_RESULTS, OUT_TABLES, REPRO
from common import checkpoint, current_environment, save_json

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    required = [
        DATA_PROCESSED / "primary_collection_cohort.csv",
        DATA_PROCESSED / "secondary_treatment_cohort.csv",
        OUT_RESULTS / "primary_logo_predictions.csv",
        OUT_TABLES / "primary_model_summary.csv",
        OUT_TABLES / "primary_subgroup_metrics.csv",
        OUT_TABLES / "primary_robustness_summary.csv",
        OUT_TABLES / "secondary_model_summary.csv",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing required outputs:\n" + "\n".join(missing))

    manifest = []
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and ".venv" not in p.parts:
            manifest.append({
                "path": str(p.relative_to(ROOT)),
                "bytes": p.stat().st_size,
                "sha256": sha256(p),
            })

    save_json(current_environment(), REPRO / "environment.json")
    pd.DataFrame(manifest).to_csv(REPRO / "file_manifest.csv", index=False)

    with open(REPRO / "checksums.sha256", "w", encoding="utf-8") as f:
        for x in manifest:
            f.write(f'{x["sha256"]}  {x["path"]}\n')

    summary = pd.read_csv(OUT_TABLES / "primary_model_summary.csv")
    best = summary.iloc[0].to_dict()
    report = [
        "# PAPER19 Reproducibility Verification",
        "",
        f"- Files hashed: {len(manifest)}",
        f'- Best primary held-region model: {best["model"]}',
        f'- MAE: {best["mae"]:.6f}',
        f'- RMSE: {best["rmse"]:.6f}',
        f'- R2: {best["r2"]:.6f}',
        "",
        "All generated numerical outputs should be treated as authoritative only when this verification phase completes without error.",
    ]
    (REPRO / "verification_report.md").write_text("\n".join(report), encoding="utf-8")
    checkpoint("08_verify_reproducibility", {"files_hashed": len(manifest), "best_model": best["model"]})
    print("\n".join(report))
    print("PHASE 08 COMPLETE")

if __name__ == "__main__":
    main()
