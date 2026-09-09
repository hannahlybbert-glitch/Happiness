# Age: predicted vs. actual happiness, by predictor subgroup

Happiness scale: 1 = Not too happy, 2 = Pretty happy, 3 = Very happy.

- **True (GSS) averages**: WTSSNRPS-weighted GSS 2004-2024, design-based 95% CIs.
- **Predicted averages**: unweighted mean of survey respondents' single guesses at the subgroup's average happiness, split by the predictor's own Age subgroup (via demographic_gss_crosswalk.csv). SE = sd / sqrt(n); 95% CI = mean +/- 1.96 SE.
- Overall GSS weighted average happiness: 2.114 (n=28,889).
- Rows are ordered happiest to least happy by the true GSS average.

## True GSS averages

| Subgroup | N (GSS) | True mean | SE | 95% CI |
|---|---|---|---|---|
| 65+ | 6,250 | 2.161 | 0.012 | (2.138, 2.183) |
| 35-64 | 14,764 | 2.120 | 0.007 | (2.107, 2.134) |
| 18-34 | 7,185 | 2.080 | 0.010 | (2.060, 2.100) |

## Predicted averages by predictor subgroup

`Pred - true` is the predictor subgroup's average guess minus that subgroup's true GSS average (positive = over-estimated happiness).

| Subgroup | Predictor subgroup | N (predictors) | Predicted mean | SE | 95% CI | Pred - true |
|---|---|---|---|---|---|---|
| 65+ | 65+ (own group) | 103 | 2.242 | 0.020 | (2.203, 2.281) | +0.081 |
| 65+ | 35-64 | 1,203 | 2.217 | 0.005 | (2.206, 2.227) | +0.056 |
| 65+ | 18-34 | 645 | 2.234 | 0.007 | (2.221, 2.248) | +0.074 |
| 35-64 | 65+ | 103 | 2.243 | 0.017 | (2.210, 2.276) | +0.122 |
| 35-64 | 35-64 (own group) | 1,203 | 2.171 | 0.005 | (2.162, 2.181) | +0.051 |
| 35-64 | 18-34 | 645 | 2.167 | 0.006 | (2.155, 2.179) | +0.047 |
| 18-34 | 65+ | 103 | 2.208 | 0.019 | (2.171, 2.245) | +0.128 |
| 18-34 | 35-64 | 1,203 | 2.183 | 0.006 | (2.171, 2.195) | +0.103 |
| 18-34 | 18-34 (own group) | 645 | 2.117 | 0.008 | (2.100, 2.133) | +0.036 |
