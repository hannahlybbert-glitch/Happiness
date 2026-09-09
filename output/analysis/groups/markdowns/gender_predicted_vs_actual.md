# Gender: predicted vs. actual happiness, by predictor subgroup

Happiness scale: 1 = Not too happy, 2 = Pretty happy, 3 = Very happy.

- **True (GSS) averages**: WTSSNRPS-weighted GSS 2004-2024, design-based 95% CIs.
- **Predicted averages**: unweighted mean of survey respondents' single guesses at the subgroup's average happiness, split by the predictor's own Gender subgroup (via demographic_gss_crosswalk.csv). SE = sd / sqrt(n); 95% CI = mean +/- 1.96 SE.
- Overall GSS weighted average happiness: 2.114 (n=28,889).
- Rows are ordered happiest to least happy by the true GSS average.

## True GSS averages

| Subgroup | N (GSS) | True mean | SE | 95% CI |
|---|---|---|---|---|
| Woman | 15,884 | 2.121 | 0.007 | (2.107, 2.135) |
| Man | 12,876 | 2.108 | 0.007 | (2.093, 2.122) |

## Predicted averages by predictor subgroup

`Pred - true` is the predictor subgroup's average guess minus that subgroup's true GSS average (positive = over-estimated happiness).

| Subgroup | Predictor subgroup | N (predictors) | Predicted mean | SE | 95% CI | Pred - true |
|---|---|---|---|---|---|---|
| Woman | Woman (own group) | 1,053 | 2.177 | 0.005 | (2.166, 2.187) | +0.056 |
| Woman | Man | 883 | 2.167 | 0.006 | (2.156, 2.178) | +0.046 |
| Man | Woman | 1,053 | 2.209 | 0.006 | (2.198, 2.220) | +0.102 |
| Man | Man (own group) | 883 | 2.167 | 0.006 | (2.156, 2.179) | +0.060 |
