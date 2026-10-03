# Results freeze

## Scientific freeze identity

The article's primary numerical state is the verified Phase-B2 analysis, augmented by a V2 decision audit computed from the already-frozen ordinary-linear-regression leave-one-region-out predictions.

## Primary freeze

- primary cohort: 154 countries;
- selected point model: ordinary linear regression;
- primary pooled LORO MAE: 13.981873;
- primary pooled LORO RMSE: 18.913204;
- primary pooled LORO R²: 0.562552;
- seed: 19019;
- subgroup/statistical bootstrap replicates: 20,000;
- complete Phase-B2 local verification: 138 files hashed.

## V2 decision-audit freeze

The reviewer-stage V2 audit does not change model fitting, hyperparameters, source cohort or LORO predictions. It derives outcome-severity and prioritization diagnostics from the frozen linear-model OOF predictions.

A clean repository replay reproduced all seven V2 audit CSVs exactly on 3 October 2026.

## Immutability rule

After creation of the `v1.0.0-submission` tag, do not replace files inside that release. Any correction affecting scientific content should use a new version and document the change in `CHANGELOG.md`.
