# Party: predicted vs. actual happiness, by predictor subgroup

Happiness scale: 1 = Not too happy, 2 = Pretty happy, 3 = Very happy.

- **True (GSS) averages**: WTSSNRPS-weighted GSS 2004-2024, design-based 95% CIs.
- **Predicted averages**: unweighted mean of survey respondents' single guesses at the subgroup's average happiness, split by the predictor's own Party subgroup (via demographic_gss_crosswalk.csv). SE = sd / sqrt(n); 95% CI = mean +/- 1.96 SE.
- Overall GSS weighted average happiness: 2.114 (n=28,889).
- Rows are ordered happiest to least happy by the true GSS average.

## True GSS averages

| Subgroup | N (GSS) | True mean | SE | 95% CI |
|---|---|---|---|---|
| Republican | 9,369 | 2.198 | 0.010 | (2.179, 2.217) |
| Democrat | 12,837 | 2.075 | 0.007 | (2.061, 2.090) |
| Independent | 5,723 | 2.064 | 0.012 | (2.042, 2.087) |

## Predicted averages by predictor subgroup

`Pred - true` is the predictor subgroup's average guess minus that subgroup's true GSS average (positive = over-estimated happiness).

| Subgroup | Predictor subgroup | N (predictors) | Predicted mean | SE | 95% CI | Pred - true |
|---|---|---|---|---|---|---|
| Republican | Republican (own group) | 523 | 2.253 | 0.007 | (2.239, 2.267) | +0.055 |
| Republican | Democrat | 1,082 | 2.124 | 0.006 | (2.111, 2.136) | -0.075 |
| Republican | Independent | 326 | 2.119 | 0.010 | (2.099, 2.139) | -0.079 |
| Democrat | Republican | 523 | 1.993 | 0.009 | (1.975, 2.011) | -0.083 |
| Democrat | Democrat (own group) | 1,082 | 2.091 | 0.006 | (2.079, 2.103) | +0.016 |
| Democrat | Independent | 326 | 2.016 | 0.011 | (1.995, 2.038) | -0.059 |
| Independent | Republican | 523 | 2.186 | 0.007 | (2.173, 2.200) | +0.122 |
| Independent | Democrat | 1,082 | 2.124 | 0.005 | (2.114, 2.135) | +0.060 |
| Independent | Independent (own group) | 326 | 2.169 | 0.012 | (2.145, 2.193) | +0.105 |
