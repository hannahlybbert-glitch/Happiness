# Marital Status: predicted vs. actual happiness, by predictor subgroup

Happiness scale: 1 = Not too happy, 2 = Pretty happy, 3 = Very happy.

- **True (GSS) averages**: WTSSNRPS-weighted GSS 2004-2024, design-based 95% CIs.
- **Predicted averages**: unweighted mean of survey respondents' single guesses at the subgroup's average happiness, split by the predictor's own Marital Status subgroup (via demographic_gss_crosswalk.csv). SE = sd / sqrt(n); 95% CI = mean +/- 1.96 SE.
- Overall GSS weighted average happiness: 2.114 (n=28,889).
- Rows are ordered happiest to least happy by the true GSS average. Excluded subgroup(s): Widowed.

## True GSS averages

| Subgroup | N (GSS) | True mean | SE | 95% CI |
|---|---|---|---|---|
| Married | 13,005 | 2.277 | 0.007 | (2.264, 2.291) |
| Never Married | 7,906 | 1.957 | 0.010 | (1.937, 1.977) |
| Separated | 5,608 | 1.919 | 0.011 | (1.897, 1.941) |

## Predicted averages by predictor subgroup

`Pred - true` is the predictor subgroup's average guess minus that subgroup's true GSS average (positive = over-estimated happiness).

| Subgroup | Predictor subgroup | N (predictors) | Predicted mean | SE | 95% CI | Pred - true |
|---|---|---|---|---|---|---|
| Married | Married (own group) | 793 | 2.247 | 0.006 | (2.236, 2.259) | -0.030 |
| Married | Never Married | 898 | 2.179 | 0.005 | (2.168, 2.190) | -0.098 |
| Married | Separated | 223 | 2.161 | 0.012 | (2.137, 2.185) | -0.116 |
| Never Married | Married | 793 | 2.208 | 0.006 | (2.195, 2.220) | +0.251 |
| Never Married | Never Married (own group) | 898 | 2.202 | 0.006 | (2.190, 2.214) | +0.245 |
| Never Married | Separated | 223 | 2.223 | 0.012 | (2.200, 2.247) | +0.266 |
| Separated | Married | 793 | 2.023 | 0.007 | (2.010, 2.037) | +0.105 |
| Separated | Never Married | 898 | 2.015 | 0.006 | (2.002, 2.027) | +0.096 |
| Separated | Separated (own group) | 223 | 2.090 | 0.015 | (2.060, 2.120) | +0.171 |
