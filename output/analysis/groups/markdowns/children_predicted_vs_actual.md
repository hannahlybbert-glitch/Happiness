# Children Ever Born: predicted vs. actual happiness, by predictor subgroup

Happiness scale: 1 = Not too happy, 2 = Pretty happy, 3 = Very happy.

- **True (GSS) averages**: WTSSNRPS-weighted GSS 2004-2024, design-based 95% CIs.
- **Predicted averages**: unweighted mean of survey respondents' single guesses at the subgroup's average happiness, split by the predictor's own Children Ever Born subgroup (via demographic_gss_crosswalk.csv). SE = sd / sqrt(n); 95% CI = mean +/- 1.96 SE.
- Overall GSS weighted average happiness: 2.114 (n=28,889).
- Rows are ordered happiest to least happy by the true GSS average.

## True GSS averages

| Subgroup | N (GSS) | True mean | SE | 95% CI |
|---|---|---|---|---|
| Children | 20,508 | 2.148 | 0.006 | (2.136, 2.160) |
| No Children | 8,262 | 2.040 | 0.009 | (2.021, 2.059) |

## Predicted averages by predictor subgroup

`Pred - true` is the predictor subgroup's average guess minus that subgroup's true GSS average (positive = over-estimated happiness).

| Subgroup | Predictor subgroup | N (predictors) | Predicted mean | SE | 95% CI | Pred - true |
|---|---|---|---|---|---|---|
| Children | Children (own group) | 950 | 2.280 | 0.005 | (2.269, 2.290) | +0.132 |
| Children | No Children | 1,000 | 2.170 | 0.006 | (2.159, 2.181) | +0.022 |
| No Children | Children | 950 | 2.175 | 0.006 | (2.163, 2.187) | +0.135 |
| No Children | No Children (own group) | 1,000 | 2.198 | 0.006 | (2.187, 2.209) | +0.158 |
