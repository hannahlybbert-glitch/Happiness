# Region: predicted vs. actual happiness, by predictor subgroup

Happiness scale: 1 = Not too happy, 2 = Pretty happy, 3 = Very happy.

- **True (GSS) averages**: WTSSNRPS-weighted GSS 2004-2024, design-based 95% CIs.
- **Predicted averages**: unweighted mean of survey respondents' single guesses at the subgroup's average happiness, split by the predictor's own Region subgroup (via demographic_gss_crosswalk.csv). SE = sd / sqrt(n); 95% CI = mean +/- 1.96 SE.
- Overall GSS weighted average happiness: 2.114 (n=28,889).
- Rows are ordered happiest to least happy by the true GSS average.

## True GSS averages

| Subgroup | N (GSS) | True mean | SE | 95% CI |
|---|---|---|---|---|
| Midwest | 6,780 | 2.122 | 0.011 | (2.101, 2.143) |
| South | 11,044 | 2.120 | 0.009 | (2.103, 2.137) |
| West | 6,415 | 2.110 | 0.011 | (2.088, 2.131) |
| Northeast | 4,650 | 2.100 | 0.013 | (2.074, 2.125) |

## Predicted averages by predictor subgroup

`Pred - true` is the predictor subgroup's average guess minus that subgroup's true GSS average (positive = over-estimated happiness).

| Subgroup | Predictor subgroup | N (predictors) | Predicted mean | SE | 95% CI | Pred - true |
|---|---|---|---|---|---|---|
| Midwest | Midwest (own group) | 393 | 2.196 | 0.008 | (2.179, 2.212) | +0.073 |
| Midwest | South | 804 | 2.181 | 0.006 | (2.170, 2.192) | +0.059 |
| Midwest | West | 389 | 2.165 | 0.009 | (2.148, 2.182) | +0.043 |
| Midwest | Northeast | 365 | 2.181 | 0.009 | (2.164, 2.199) | +0.059 |
| South | Midwest | 393 | 2.168 | 0.010 | (2.149, 2.187) | +0.048 |
| South | South (own group) | 804 | 2.191 | 0.007 | (2.178, 2.204) | +0.071 |
| South | West | 389 | 2.147 | 0.010 | (2.128, 2.167) | +0.027 |
| South | Northeast | 365 | 2.176 | 0.010 | (2.156, 2.195) | +0.056 |
| West | Midwest | 393 | 2.220 | 0.008 | (2.204, 2.237) | +0.110 |
| West | South | 804 | 2.197 | 0.006 | (2.185, 2.209) | +0.087 |
| West | West (own group) | 389 | 2.248 | 0.009 | (2.231, 2.265) | +0.138 |
| West | Northeast | 365 | 2.198 | 0.009 | (2.181, 2.216) | +0.089 |
| Northeast | Midwest | 393 | 2.176 | 0.008 | (2.159, 2.192) | +0.076 |
| Northeast | South | 804 | 2.148 | 0.006 | (2.136, 2.159) | +0.048 |
| Northeast | West | 389 | 2.163 | 0.009 | (2.146, 2.180) | +0.063 |
| Northeast | Northeast (own group) | 365 | 2.163 | 0.009 | (2.146, 2.180) | +0.063 |
