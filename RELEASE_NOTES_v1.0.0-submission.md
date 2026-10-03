# v1.0.0-submission — Frozen reproducibility archive

This release freezes the computational evidence supporting **Reliability Gaps Under Geographic Shift in Global Municipal Waste Service Prediction**.

The archive contains the verified Phase-B2 model, subgroup, conformal/OOD, robustness and secondary-endpoint outputs plus the V2 outcome-severity and service-deficit prioritization audit computed from frozen LORO predictions.

## Key freeze facts

- primary cohort: 154 countries;
- validation: seven-region leave-one-region-out;
- selected point model: ordinary linear regression;
- pooled LORO MAE: 13.98;
- low-income MAE: 25.47 with +17.70-point mean overestimation;
- nominal-90% low-income conformal coverage: 53.8%;
- Mahalanobis OOD vs absolute error: Spearman rho 0.035;
- deficit-rank Spearman: 0.807;
- worst-10% true-deficit recall: 37.5%;
- V2 decision audit replays exactly from committed frozen predictions.

## Public reproducibility state

This release is the public frozen computational state supporting the manuscript submission. Journal-portal administrative files are kept outside the repository so that the release remains focused on scientific reproducibility.

## Immutability

Do not replace files in this tag. Any scientific correction should use a new release version with an explicit changelog entry.
