# Method protocol

## Study objective

The study evaluates the reliability of country-level municipal-solid-waste collection prediction when an entire World Bank region is absent from model fitting. The primary contribution is a reliability and decision-support audit under geographic shift, not a claim to a new prediction algorithm.

## Primary endpoint

National regular MSW collection coverage from World Bank *What a Waste 3.0* is harmonized to one record per country. Where multiple reporting bases exist, the prespecified precedence is:

1. percentage of MSW collected (`PT_MSW`);
2. percentage of population served (`PT_POP`);
3. percentage of households served (`PT_HH`).

Within the preferred measurement basis, the latest available year is retained.

## Predictors

Four World Development Indicators are matched to the target reference year:

- GDP per capita, PPP, constant 2021 international dollars;
- urban population percentage;
- total population;
- population density.

GDP per capita, population and population density are transformed with `log(1+x)`; urban population is represented as a fraction. Missing predictors are imputed with training-fold medians. Scaling, where required, is fitted within the training fold.

## Geographic validation

The outer loop is leave-one-World-Bank-region-out. Every country in the held region is excluded from model fitting and predicted only by a model trained on the remaining regions. Final metrics pool out-of-fold predictions across all seven held-region iterations.

## Point models

The frozen comparison contains:

- training-mean dummy regressor;
- ordinary linear regression;
- ridge regression;
- random forest;
- histogram gradient boosting.

Model tuning, where applicable, is performed using source-region training data only. Predictions are clipped to the physically meaningful 0–100% range.

## Reliability audit

Reliability is examined by held-out region and current World Bank income group using MAE, RMSE, R² and signed error. The main subgroup contrast uses 20,000-replicate nonparametric bootstrap intervals and a two-sided permutation test for the low-versus-high-income MAE gap.

## Conformal uncertainty

The uncertainty module uses a ridge-regularized linear pipeline with a proper-training/calibration split inside each outer fold. Nominal 90% split-conformal intervals use absolute calibration residuals. Diagnostic variants include OOD-scaled intervals and income-group residual quantiles with global fallback. These variants are not claimed to provide exact conditional guarantees under deliberate region shift.

## OOD/selective prediction

The OOD score is Mahalanobis distance in transformed predictor space after training-fold imputation, standardization and Ledoit–Wolf covariance shrinkage. Selective policies retain cases below thresholds learned from the source calibration distribution. A separate equal-income-retention diagnostic tests whether similar access to predictions removes subgroup quality differences.

## Robustness

Robustness checks include outcome records from 2015 onward, 2018 onward and 2020 onward, plus measurement-basis-specific subsets. Treatment/disposal is analyzed separately as a secondary endpoint under strict and permissive definitions.

## V2 decision audit

The V2 upgrade does not refit or retune the model. It uses the frozen ordinary-linear-regression LORO predictions to evaluate:

- error as a function of observed collection-coverage severity;
- correlations between observed coverage and signed/absolute error;
- rank correspondence for service deficits (`100 - coverage`);
- recall of the worst 10%, 20%, 25% and 33% true service deficits;
- threshold-level false negatives for countries with observed coverage at or below 25%, 50% and 75%.

Primary seed: `19019`. Bootstrap replicates: `20,000`.
