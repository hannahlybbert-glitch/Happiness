# Urban vs Rural: predicted vs. actual happiness, by predictor subgroup

Happiness scale: 1 = Not too happy, 2 = Pretty happy, 3 = Very happy.

- **True (GSS) averages**: WTSSNRPS-weighted GSS 2004-2024, design-based 95% CIs.
- **Predicted averages**: unweighted mean of survey respondents' single guesses at the subgroup's average happiness, split by the predictor's own Urban vs Rural subgroup (via demographic_gss_crosswalk.csv). SE = sd / sqrt(n); 95% CI = mean +/- 1.96 SE.
- Overall GSS weighted average happiness: 2.114 (n=28,889).
- Rows are ordered happiest to least happy by the true GSS average.

## True GSS averages

| Subgroup | N (GSS) | True mean | SE | 95% CI |
|---|---|---|---|---|
| Small/rural town | 4,878 | 2.131 | 0.014 | (2.104, 2.158) |
| Suburb | 15,074 | 2.118 | 0.007 | (2.105, 2.132) |
| Big city | 8,937 | 2.099 | 0.010 | (2.081, 2.118) |

## Predicted averages by predictor subgroup

`Pred - true` is the predictor subgroup's average guess minus that subgroup's true GSS average (positive = over-estimated happiness).

| Subgroup | Predictor subgroup | N (predictors) | Predicted mean | SE | 95% CI | Pred - true |
|---|---|---|---|---|---|---|
| Small/rural town | Small/rural town (own group) | 507 | 2.239 | 0.008 | (2.223, 2.255) | +0.108 |
| Small/rural town | Suburb | 719 | 2.215 | 0.007 | (2.201, 2.229) | +0.085 |
| Small/rural town | Big city | 726 | 2.186 | 0.008 | (2.171, 2.201) | +0.055 |
| Suburb | Small/rural town | 507 | 2.187 | 0.006 | (2.175, 2.199) | +0.069 |
| Suburb | Suburb (own group) | 719 | 2.213 | 0.005 | (2.203, 2.224) | +0.095 |
| Suburb | Big city | 726 | 2.204 | 0.005 | (2.193, 2.215) | +0.086 |
| Big city | Small/rural town | 507 | 2.100 | 0.008 | (2.084, 2.116) | +0.001 |
| Big city | Suburb | 719 | 2.134 | 0.007 | (2.121, 2.147) | +0.035 |
| Big city | Big city (own group) | 726 | 2.152 | 0.007 | (2.139, 2.166) | +0.053 |
