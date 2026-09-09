# Socializing with Friends: predicted vs. actual happiness, by predictor subgroup

Happiness scale: 1 = Not too happy, 2 = Pretty happy, 3 = Very happy.

- **True (GSS) averages**: WTSSNRPS-weighted GSS 2004-2024, design-based 95% CIs.
- **Predicted averages**: unweighted mean of survey respondents' single guesses at the subgroup's average happiness, split by the predictor's own Socializing with Friends subgroup (via demographic_gss_crosswalk.csv). SE = sd / sqrt(n); 95% CI = mean +/- 1.96 SE.
- Overall GSS weighted average happiness: 2.114 (n=28,889).
- Rows are ordered happiest to least happy by the true GSS average.

## True GSS averages

| Subgroup | N (GSS) | True mean | SE | 95% CI |
|---|---|---|---|---|
| Weekly or more | 7,390 | 2.170 | 0.010 | (2.150, 2.189) |
| Sometimes | 9,743 | 2.135 | 0.008 | (2.119, 2.152) |
| Never | 2,097 | 1.981 | 0.018 | (1.945, 2.016) |

## Predicted averages by predictor subgroup

`Pred - true` is the predictor subgroup's average guess minus that subgroup's true GSS average (positive = over-estimated happiness).

| Subgroup | Predictor subgroup | N (predictors) | Predicted mean | SE | 95% CI | Pred - true |
|---|---|---|---|---|---|---|
| Weekly or more | Weekly or more (own group) | 817 | 2.351 | 0.005 | (2.341, 2.360) | +0.181 |
| Weekly or more | Sometimes | 934 | 2.321 | 0.005 | (2.311, 2.330) | +0.151 |
| Weekly or more | Never | 200 | 2.303 | 0.011 | (2.282, 2.324) | +0.134 |
| Sometimes | Weekly or more | 817 | 2.115 | 0.005 | (2.104, 2.125) | -0.020 |
| Sometimes | Sometimes (own group) | 934 | 2.131 | 0.005 | (2.122, 2.141) | -0.004 |
| Sometimes | Never | 200 | 2.105 | 0.011 | (2.083, 2.127) | -0.030 |
| Never | Weekly or more | 817 | 1.883 | 0.007 | (1.869, 1.896) | -0.098 |
| Never | Sometimes | 934 | 1.910 | 0.006 | (1.898, 1.921) | -0.071 |
| Never | Never (own group) | 200 | 1.923 | 0.015 | (1.894, 1.952) | -0.058 |
