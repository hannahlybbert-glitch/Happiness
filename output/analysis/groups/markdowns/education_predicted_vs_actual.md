# Education: predicted vs. actual happiness, by predictor subgroup

Happiness scale: 1 = Not too happy, 2 = Pretty happy, 3 = Very happy.

- **True (GSS) averages**: WTSSNRPS-weighted GSS 2004-2024, design-based 95% CIs.
- **Predicted averages**: unweighted mean of survey respondents' single guesses at the subgroup's average happiness, split by the predictor's own Education subgroup (via demographic_gss_crosswalk.csv). SE = sd / sqrt(n); 95% CI = mean +/- 1.96 SE.
- Overall GSS weighted average happiness: 2.114 (n=28,889).
- Rows are ordered happiest to least happy by the true GSS average.

## True GSS averages

| Subgroup | N (GSS) | True mean | SE | 95% CI |
|---|---|---|---|---|
| Bachelors+Graduate | 9,344 | 2.211 | 0.009 | (2.194, 2.228) |
| HS+some college | 16,205 | 2.091 | 0.007 | (2.078, 2.105) |
| Less than HS | 3,307 | 2.010 | 0.016 | (1.979, 2.042) |

## Predicted averages by predictor subgroup

`Pred - true` is the predictor subgroup's average guess minus that subgroup's true GSS average (positive = over-estimated happiness).

| Subgroup | Predictor subgroup | N (predictors) | Predicted mean | SE | 95% CI | Pred - true |
|---|---|---|---|---|---|---|
| Bachelors+Graduate | Bachelors+Graduate (own group) | 1,128 | 2.237 | 0.005 | (2.227, 2.246) | +0.026 |
| Bachelors+Graduate | HS+some college | 806 | 2.249 | 0.006 | (2.237, 2.261) | +0.038 |
| Bachelors+Graduate | Less than HS | 17 | 2.301 | 0.042 | (2.219, 2.382) | +0.090 |
| HS+some college | Bachelors+Graduate | 1,128 | 2.158 | 0.004 | (2.150, 2.165) | +0.066 |
| HS+some college | HS+some college (own group) | 806 | 2.170 | 0.005 | (2.160, 2.181) | +0.079 |
| HS+some college | Less than HS | 17 | 2.211 | 0.031 | (2.151, 2.270) | +0.119 |
| Less than HS | Bachelors+Graduate | 1,128 | 2.034 | 0.006 | (2.022, 2.045) | +0.023 |
| Less than HS | HS+some college | 806 | 2.013 | 0.007 | (2.000, 2.027) | +0.003 |
| Less than HS | Less than HS (own group) | 17 | 2.037 | 0.041 | (1.957, 2.117) | +0.027 |
