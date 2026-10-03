# PAPER19 Scientific Result Lock — Phase B2

## Status

The numerical phase is considered scientifically interpretable only after this Phase B2 audit completes.

## Primary held-region model

- Selected model by leave-one-region-out MAE: **linear**.
- Overall MAE (95% bootstrap CI): **13.98 [12.01, 16.00]** percentage points.
- Overall RMSE (95% bootstrap CI): **18.91 [16.63, 21.11]**.
- Overall R2 (95% bootstrap CI): **0.56 [0.46, 0.64]**.

## Income-group reliability

- Low-income MAE: **25.47** [19.22, 31.58].
- High-income MAE: **6.46** [4.40, 8.77].
- Low-minus-high MAE gap: **19.01** [12.28, 25.40], permutation p=4.99975e-05.
- Low-income mean signed error: **17.70** [5.26, 28.63] (positive = overestimation).

## Conformal reliability

- Global nominal-90% interval empirical coverage: **0.851**.
- Low-income coverage: **0.538**, Wilson 95% CI [0.291, 0.768].
- High-income coverage: **0.979**, Wilson 95% CI [0.891, 0.996].

## OOD and abstention

- Overall Spearman association between Mahalanobis OOD score and absolute error: rho=0.035, p=0.6644.
- Therefore, covariate-distance abstention must not be described as a generally effective error detector unless the selective-policy audit demonstrates otherwise.

## Measurement heterogeneity

- Household-based coverage MAE: **27.74** [22.24, 32.93].
- MSW-weight coverage MAE: **12.65** [10.09, 15.36].
- In the MSW-weight-only robustness subset, low-income MAE remains **19.18** with bias **7.88**.

## Manuscript claim lock

1. Do **not** claim that abstention solves the fairness/reliability problem.
2. Do **not** claim novelty for conformal prediction, OOD detection, or waste-management ML itself.
3. The defensible contribution is a country-scale reliability audit under true geographic holdout using WAW 3.0, showing that apparently acceptable aggregate performance can coexist with severe subgroup error and interval undercoverage.
4. Measurement-basis heterogeneity must be discussed as a contributor, not hidden.
5. The persistence of low-income error in recency and MSW-weight-only robustness subsets supports—but does not prove—a broader data-support/generalization problem.
6. The paper should frame abstention as a decision-support safeguard whose usefulness is conditional and can itself become inequitable when uncertainty scores poorly track error.

## Recommended manuscript direction

**Reliability Gaps and the Limits of Abstention in Global Municipal Waste Service Prediction**

Alternative title preserving the original question framing:

**When Should Environmental AI Abstain? Reliability Gaps in Global Municipal Waste Service Prediction**