# Frozen results

## Primary point model

The selected model by pooled leave-one-region-out MAE is ordinary linear regression:

- MAE: **13.981873** percentage points;
- RMSE: **18.913204**;
- R²: **0.562552**;
- mean signed error: **-0.326551**.

The model comparison is stored in `results/verified_baseline/tables/primary_model_summary.csv`.

## Income-group reliability

For the frozen linear LORO predictions:

- low income: **n=13**, MAE **25.47**, RMSE **27.90**, bias **+17.70**;
- lower middle income: **n=42**, MAE **20.15**, bias **+4.48**;
- upper middle income: **n=51**, MAE **13.06**, bias **-5.44**;
- high income: **n=48**, MAE **6.46**, RMSE **10.00**, bias **-3.98**.

The Phase-B2 statistical lock reports a low-minus-high MAE difference of **19.01** percentage points with bootstrap 95% CI **[12.28, 25.40]** and two-sided permutation `p = 4.99975e-05`.

## Conformal/OOD reliability

From the frozen conformal predictions:

- nominal-90% global interval coverage: **0.850649** overall;
- low-income coverage: **0.538462**;
- high-income coverage: **0.979167**;
- Mahalanobis OOD score vs absolute error: Spearman **ρ = 0.035232**, `p = 0.664438`.

The Phase-B2 lock records Wilson 95% CIs of **[0.291, 0.768]** for low income and **[0.891, 0.996]** for high income.

## Measurement-basis robustness

The Phase-B2 lock reports:

- household-based coverage MAE: **27.74** [22.24, 32.93];
- MSW-weight coverage MAE: **12.65** [10.09, 15.36];
- MSW-weight-only low-income MAE: **19.18**, bias **+7.88**.

## V2 outcome-severity audit

The lowest observed-coverage quartile (`n=39`, mean observed coverage 29.37%) has:

- MAE **23.72** [19.31, 28.12];
- mean signed error **+23.20** [18.48, 27.84].

Across all 154 countries:

- observed coverage vs signed error: Spearman **ρ = -0.625871**, `p = 3.997e-18`;
- observed coverage vs absolute error: Spearman **ρ = -0.401865**, `p = 2.394e-07`.

## V2 service-deficit prioritization audit

For true deficit `100 - observed coverage` and predicted deficit `100 - predicted coverage`:

- rank Spearman **ρ = 0.807489**, `p = 1.143e-36`;
- recall of worst 10% true deficits: **0.375**;
- worst 20% recall: **0.645**;
- worst 25% recall: **0.667**;
- worst 33% recall: **0.765**.

At an observed-coverage threshold of 25%, 18 countries are truly at or below the threshold while none are predicted at or below it. At the 50% threshold, sensitivity is **0.472** with precision **0.739**.

These diagnostics illustrate why good overall rank correspondence does not imply reliable capture of the most severe deficits.
