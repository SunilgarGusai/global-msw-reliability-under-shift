# Quick start

This repository separates **exact verification of the frozen article evidence** from a **fresh public-source rerun**.

## A. Verify the frozen manuscript-facing evidence

Recommended: Python 3.13.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/validate_public_artifact.py
pytest -q
python scripts/summarize_key_results.py
```

Expected result: all structural, numerical, and traceability checks pass.

## B. Reproduce the V2 decision audit from frozen LORO predictions

```bash
python pipeline/scripts/11_oof_decision_audit.py \
  --predictions results/verified_baseline/results/primary_logo_predictions.csv \
  --out results/v2_upgrade_reproduced \
  --figures figures/reproduced
```

The replay uses seed `19019` and 20,000 bootstrap replicates. It should reproduce the committed V2 audit CSVs exactly.

## C. Regenerate reviewer-facing summary figures

```bash
python scripts/regenerate_public_figures.py
```

This creates a clean `figures/reproduced_public/` directory from committed machine-readable evidence.

## D. Fresh full pipeline from World Bank sources

On Windows, use the phase launchers under `pipeline/cmd/`. The original source-acquisition phase contacts World Bank/Data360 and WDI endpoints. Fresh upstream data can change over time, so a new retrieval may not be byte-identical to the September 2026 frozen state.

For article verification, the authoritative state is the committed prediction arrays, tables, Phase-B2 provenance manifest, and V2 decision-audit outputs.

## Data policy

Do not treat the repository's derived analytical outputs as replacements for the upstream World Bank datasets. See `docs/DATA_PROVENANCE.md` and `THIRD_PARTY_LICENSES.md`.
