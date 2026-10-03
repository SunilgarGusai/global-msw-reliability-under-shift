# Data provenance

## What is archived here

The repository contains the frozen analytical outputs required to verify the article's reported calculations: point-model out-of-fold predictions, conformal/OOD predictions, tuning summaries, subgroup tables, robustness summaries, secondary-endpoint predictions, V2 decision-audit outputs, and historical Phase-B2 integrity manifests.

## What is not redistributed

The repository does not present the original World Bank/Data360 and WDI datasets as project-owned data. Fresh source acquisition is performed from official public endpoints by the phase-separated pipeline.

## Source endpoints frozen in the analysis code

- What a Waste collection coverage: `https://data360files.worldbank.org/data360-data/data/WB_WAW/WM_COL_COV.csv`
- What a Waste treatment/disposal: `https://data360files.worldbank.org/data360-data/data/WB_WAW/WM_MSW_TREAT.csv`
- World Development Indicators API: `https://api.worldbank.org/v2`

## Primary derived cohort

The harmonized primary cohort contains **154 countries** with outcome years from **2001–2025**. The final model-facing LORO prediction file contains one row per country per model, with 154 rows for each of five point-model families.

## Integrity history

The later Phase-B2 verification supersedes the earlier Phase-08 file count. The Phase-B2 verification states that **138 files** were hashed in the complete local scientific state and confirms the statistical-audit, subgroup-CI, conformal-coverage, OOD/error, measurement-basis, coefficient-stability and scientific-lock artifacts.

The original Phase-B2 checksum/manifest files are retained under `provenance/` as historical evidence. The curated public repository has its own `PUBLIC_SHA256SUMS.txt` because it intentionally excludes private journal-submission files and some development-only materials.
