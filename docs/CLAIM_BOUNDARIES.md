# Scientific claim boundaries

The repository is intentionally explicit about what the frozen evidence does and does not support.

## Supported claims

- Socioeconomic predictors retain substantial signal under leave-one-region-out transfer.
- Ordinary linear regression has the lowest pooled LORO MAE among the frozen point models.
- Aggregate performance masks a large current-income-group reliability gradient.
- Low-income countries are systematically overestimated on average in the frozen linear LORO predictions.
- Nominal 90% global split-conformal intervals under-cover overall and severely under-cover the low-income subgroup under deliberate geographic shift.
- The frozen Mahalanobis OOD score is almost unrelated to realized absolute error.
- The low-income error gap is attenuated but persists in the MSW-weight-only sensitivity subset.
- Errors are larger for the lowest observed-coverage quartile.
- Service-deficit ranking is strongly correlated overall, yet capture of the worst 10% deficits is poor.

## Claims not supported

- The study does not show that all selective prediction or abstention methods fail.
- It does not establish causal effects of GDP, urbanization, region or income classification on waste-service coverage.
- It does not establish fairness in a legal or normative sense; income groups are used as policy-relevant reliability audit strata.
- It does not validate a field-deployed allocation or investment system.
- It does not claim exact conformal validity after deliberate geographic distribution shift.
- It does not show that deep or more complex models can never improve waste-service prediction.
- It does not treat national collection coverage as identical to the full city-level SDG 11.6.1 indicator.
- It does not infer that a historical income classification would yield identical subgroup results; the frozen audit uses current World Bank income groups.

## Decision-audit boundary

The V2 prioritization analysis uses frozen out-of-fold predictions. It quantifies ranking and threshold misses but does not simulate budgets, policy preferences, causal benefits, or downstream service delivery.
