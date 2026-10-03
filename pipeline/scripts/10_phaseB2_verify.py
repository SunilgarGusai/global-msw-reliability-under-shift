\
from pathlib import Path
import hashlib
import json
import pandas as pd

from config import ROOT, OUT_TABLES, OUT_FIGURES, REPRO
from common import checkpoint, current_environment, save_json

REQUIRED = [
    OUT_TABLES / "phaseB2_primary_overall_ci.csv",
    OUT_TABLES / "phaseB2_income_metric_ci.csv",
    OUT_TABLES / "phaseB2_low_high_contrasts.csv",
    OUT_TABLES / "phaseB2_measurement_unit_ci.csv",
    OUT_TABLES / "phaseB2_measurement_unit_contrasts.csv",
    OUT_TABLES / "phaseB2_conformal_coverage_audit.csv",
    OUT_TABLES / "phaseB2_ood_error_audit.csv",
    OUT_TABLES / "phaseB2_selective_policy_fairness.csv",
    OUT_TABLES / "phaseB2_linear_coefficient_stability.csv",
    OUT_TABLES / "phaseB2_linear_coefficient_summary.csv",
    REPRO / "PHASE_B2_SCIENTIFIC_LOCK.md",
]

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    missing=[str(p) for p in REQUIRED if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing Phase B2 outputs:\n"+"\n".join(missing))

    manifest=[]
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and ".venv" not in p.parts:
            manifest.append({
                "path":str(p.relative_to(ROOT)),
                "bytes":p.stat().st_size,
                "sha256":sha256(p),
            })

    pd.DataFrame(manifest).to_csv(REPRO/"file_manifest_phaseB2.csv",index=False)
    with open(REPRO/"checksums_phaseB2.sha256","w",encoding="utf-8") as f:
        for x in manifest:
            f.write(f'{x["sha256"]}  {x["path"]}\n')

    report = [
        "# PAPER19 Phase B2 Verification",
        "",
        f"- Files hashed: {len(manifest)}",
        "- Statistical audit outputs: present",
        "- Subgroup confidence intervals: present",
        "- Conformal coverage audit: present",
        "- OOD/error audit: present",
        "- Measurement-basis audit: present",
        "- Linear coefficient stability audit: present",
        "- Scientific result lock: present",
        "",
        "PHASE B2 VERIFIED.",
    ]
    (REPRO/"PHASE_B2_VERIFICATION_REPORT.md").write_text("\n".join(report),encoding="utf-8")
    checkpoint("10_phaseB2_verify",{"files_hashed":len(manifest)})
    print("\n".join(report))
    print("PHASE 10 COMPLETE")

if __name__=="__main__":
    main()
