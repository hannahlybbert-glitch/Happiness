# Sexual Orientation: predicted vs. actual happiness, by predictor subgroup

Happiness scale: 1 = Not too happy, 2 = Pretty happy, 3 = Very happy.

- **True (GSS) averages**: WTSSNRPS-weighted GSS 2004-2024, design-based 95% CIs.
- **Predicted averages**: unweighted mean of survey respondents' single guesses at the subgroup's average happiness, split by the predictor's own Sexual Orientation subgroup (via demographic_gss_crosswalk.csv). SE = sd / sqrt(n); 95% CI = mean +/- 1.96 SE.
- Overall GSS weighted average happiness: 2.114 (n=28,889).
- Rows are ordered happiest to least happy by the true GSS average.

## True GSS averages

| Subgroup | N (GSS) | True mean | SE | 95% CI |
|---|---|---|---|---|
| Heterosexual/Straight | 16,694 | 2.104 | 0.007 | (2.090, 2.117) |
| Gay/Lesbian/Homosexual | 405 | 2.021 | 0.042 | (1.939, 2.102) |
| Bisexual | 569 | 1.896 | 0.036 | (1.826, 1.966) |

## Predicted averages by predictor subgroup

`Pred - true` is the predictor subgroup's average guess minus that subgroup's true GSS average (positive = over-estimated happiness).

| Subgroup | Predictor subgroup | N (predictors) | Predicted mean | SE | 95% CI | Pred - true |
|---|---|---|---|---|---|---|
| Heterosexual/Straight | Heterosexual/Straight (own group) | 1,590 | 2.239 | 0.004 | (2.231, 2.247) | +0.136 |
| Heterosexual/Straight | Gay/Lesbian/Homosexual | 101 | 2.223 | 0.020 | (2.183, 2.263) | +0.119 |
| Heterosexual/Straight | Bisexual | 216 | 2.192 | 0.012 | (2.169, 2.216) | +0.089 |
| Gay/Lesbian/Homosexual | Heterosexual/Straight | 1,590 | 2.110 | 0.005 | (2.101, 2.120) | +0.089 |
| Gay/Lesbian/Homosexual | Gay/Lesbian/Homosexual (own group) | 101 | 2.144 | 0.021 | (2.103, 2.185) | +0.123 |
| Gay/Lesbian/Homosexual | Bisexual | 216 | 2.139 | 0.013 | (2.113, 2.165) | +0.118 |
| Bisexual | Heterosexual/Straight | 1,590 | 2.118 | 0.005 | (2.109, 2.127) | +0.222 |
| Bisexual | Gay/Lesbian/Homosexual | 101 | 2.143 | 0.019 | (2.106, 2.180) | +0.247 |
| Bisexual | Bisexual (own group) | 216 | 2.162 | 0.012 | (2.138, 2.186) | +0.266 |
