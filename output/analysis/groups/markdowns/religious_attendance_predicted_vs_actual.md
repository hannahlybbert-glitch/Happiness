# Religious Attendance: predicted vs. actual happiness, by predictor subgroup

Happiness scale: 1 = Not too happy, 2 = Pretty happy, 3 = Very happy.

- **True (GSS) averages**: WTSSNRPS-weighted GSS 2004-2024, design-based 95% CIs.
- **Predicted averages**: unweighted mean of survey respondents' single guesses at the subgroup's average happiness, split by the predictor's own Religious Attendance subgroup (via demographic_gss_crosswalk.csv). SE = sd / sqrt(n); 95% CI = mean +/- 1.96 SE.
- Overall GSS weighted average happiness: 2.114 (n=28,889).
- Rows are ordered happiest to least happy by the true GSS average.

## True GSS averages

| Subgroup | N (GSS) | True mean | SE | 95% CI |
|---|---|---|---|---|
| Weekly or more | 6,416 | 2.245 | 0.012 | (2.222, 2.269) |
| Sometimes | 14,511 | 2.109 | 0.007 | (2.095, 2.123) |
| Never | 7,751 | 2.018 | 0.009 | (1.999, 2.037) |

## Predicted averages by predictor subgroup

`Pred - true` is the predictor subgroup's average guess minus that subgroup's true GSS average (positive = over-estimated happiness).

| Subgroup | Predictor subgroup | N (predictors) | Predicted mean | SE | 95% CI | Pred - true |
|---|---|---|---|---|---|---|
| Weekly or more | Weekly or more (own group) | 245 | 2.352 | 0.010 | (2.332, 2.372) | +0.107 |
| Weekly or more | Sometimes | 741 | 2.284 | 0.006 | (2.272, 2.296) | +0.039 |
| Weekly or more | Never | 966 | 2.178 | 0.006 | (2.166, 2.190) | -0.067 |
| Sometimes | Weekly or more | 245 | 2.176 | 0.009 | (2.158, 2.194) | +0.067 |
| Sometimes | Sometimes (own group) | 741 | 2.183 | 0.005 | (2.174, 2.192) | +0.074 |
| Sometimes | Never | 966 | 2.149 | 0.004 | (2.141, 2.157) | +0.040 |
| Never | Weekly or more | 245 | 2.027 | 0.013 | (2.002, 2.051) | +0.009 |
| Never | Sometimes | 741 | 2.108 | 0.007 | (2.095, 2.121) | +0.090 |
| Never | Never (own group) | 966 | 2.203 | 0.006 | (2.191, 2.215) | +0.185 |
