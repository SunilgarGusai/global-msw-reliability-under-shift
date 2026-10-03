# Reproducibility model

## Three reproducibility layers

### Layer 1 — frozen-result verification

This is the strongest reviewer-facing path because it does not depend on mutable upstream data. `scripts/validate_public_artifact.py` checks file presence, cohort/model dimensions, numerical invariants, subgroup findings, conformal/OOD diagnostics, V2 decision-audit values, and the public SHA-256 manifest.

### Layer 2 — deterministic V2 audit replay

`pipeline/scripts/11_oof_decision_audit.py` starts from the committed frozen LORO prediction file. A clean replay with seed 19019 and 20,000 bootstrap replicates reproduces all seven committed V2 CSV outputs exactly.

### Layer 3 — fresh end-to-end source rerun

The original phase-separated pipeline can reacquire World Bank source data and rebuild the analysis. A future fresh retrieval may differ if upstream public files or APIs have been revised. Such a rerun is scientifically useful but is not a substitute for the frozen article state.

## Recommended verification commands

```bash
python -m pip install -r requirements.txt
python scripts/validate_public_artifact.py
pytest -q
python scripts/summarize_key_results.py
python scripts/regenerate_public_figures.py
```

## Windows full-pipeline route

The `pipeline/cmd/` directory preserves one-click launchers for source acquisition, cohort construction, point models, conformal/selective analysis, robustness, secondary endpoint analysis, figures/tables, verification, statistical audit and Phase-B2 verification.

## Output protection

Do not overwrite committed frozen result files during exploratory reruns. V2 replay writes to `results/v2_upgrade_reproduced/` and figure regeneration writes to `figures/reproduced*`.

## Manuscript boundary

The public reproducibility repository is not a mirror of the journal-submission package. Cover letters, portal-specific forms, reviewer correspondence, and other administrative submission files are kept outside the repository so that the computational artifact remains focused and auditable.
