# Income: predicted vs. actual happiness, by predictor subgroup

Happiness scale: 1 = Not too happy, 2 = Pretty happy, 3 = Very happy.

- **True (GSS) averages**: WTSSNRPS-weighted GSS 2004-2024, design-based 95% CIs.
- **Predicted averages**: unweighted mean of survey respondents' single guesses at the subgroup's average happiness, split by the predictor's own Income subgroup (via demographic_gss_crosswalk.csv). SE = sd / sqrt(n); 95% CI = mean +/- 1.96 SE.
- Overall GSS weighted average happiness: 2.114 (n=28,889).
- Rows are ordered happiest to least happy by the true GSS average.

## True GSS averages

| Subgroup | N (GSS) | True mean | SE | 95% CI |
|---|---|---|---|---|
| High | 7,374 | 2.264 | 0.009 | (2.246, 2.282) |
| Mid | 8,665 | 2.130 | 0.009 | (2.112, 2.148) |
| Low | 9,583 | 1.968 | 0.009 | (1.949, 1.986) |

## Predicted averages by predictor subgroup

`Pred - true` is the predictor subgroup's average guess minus that subgroup's true GSS average (positive = over-estimated happiness).

| Subgroup | Predictor subgroup | N (predictors) | Predicted mean | SE | 95% CI | Pred - true |
|---|---|---|---|---|---|---|
| High | High (own group) | 449 | 2.314 | 0.007 | (2.300, 2.328) | +0.050 |
| High | Mid | 876 | 2.334 | 0.005 | (2.324, 2.345) | +0.070 |
| High | Low | 627 | 2.334 | 0.007 | (2.320, 2.348) | +0.070 |
| Mid | High | 449 | 2.155 | 0.007 | (2.142, 2.168) | +0.025 |
| Mid | Mid (own group) | 876 | 2.148 | 0.005 | (2.138, 2.158) | +0.017 |
| Mid | Low | 627 | 2.160 | 0.006 | (2.148, 2.172) | +0.030 |
| Low | High | 449 | 1.938 | 0.008 | (1.921, 1.954) | -0.030 |
| Low | Mid | 876 | 1.923 | 0.006 | (1.912, 1.934) | -0.045 |
| Low | Low (own group) | 627 | 1.937 | 0.008 | (1.922, 1.953) | -0.030 |
