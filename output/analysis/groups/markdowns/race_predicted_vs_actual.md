# Race: predicted vs. actual happiness, by predictor subgroup

Happiness scale: 1 = Not too happy, 2 = Pretty happy, 3 = Very happy.

- **True (GSS) averages**: WTSSNRPS-weighted GSS 2004-2024, design-based 95% CIs.
- **Predicted averages**: unweighted mean of survey respondents' single guesses at the subgroup's average happiness, split by the predictor's own Race subgroup (via demographic_gss_crosswalk.csv). SE = sd / sqrt(n); 95% CI = mean +/- 1.96 SE.
- Overall GSS weighted average happiness: 2.114 (n=28,889).
- Rows are ordered happiest to least happy by the true GSS average.
- 'Other' pools Hispanic, Asian, and other / American-Indian respondents. True 'Other' is the design-weighted GSS average over every non-White, non-Black respondent with RACECEN1 recorded; predicted 'Other' is each survey respondent's average of their Hispanic and Asian guesses, since the survey asked no 'other race' question.

## True GSS averages

| Subgroup | N (GSS) | True mean | SE | 95% CI |
|---|---|---|---|---|
| White | 21,401 | 2.132 | 0.006 | (2.121, 2.144) |
| Other | 2,941 | 2.114 | 0.016 | (2.083, 2.146) |
| Black | 4,282 | 2.007 | 0.014 | (1.979, 2.034) |

## Predicted averages by predictor subgroup

`Pred - true` is the predictor subgroup's average guess minus that subgroup's true GSS average (positive = over-estimated happiness).

| Subgroup | Predictor subgroup | N (predictors) | Predicted mean | SE | 95% CI | Pred - true |
|---|---|---|---|---|---|---|
| White | White (own group) | 1,348 | 2.215 | 0.004 | (2.207, 2.224) | +0.083 |
| White | Other | 332 | 2.236 | 0.009 | (2.219, 2.253) | +0.104 |
| White | Black | 271 | 2.275 | 0.012 | (2.251, 2.298) | +0.142 |
| Other | White | 1,348 | 2.171 | 0.004 | (2.163, 2.178) | +0.056 |
| Other | Other (own group) | 332 | 2.150 | 0.008 | (2.134, 2.165) | +0.035 |
| Other | Black | 271 | 2.189 | 0.011 | (2.169, 2.210) | +0.075 |
| Black | White | 1,348 | 2.081 | 0.005 | (2.072, 2.091) | +0.075 |
| Black | Other | 332 | 2.072 | 0.009 | (2.054, 2.091) | +0.066 |
| Black | Black (own group) | 271 | 2.156 | 0.014 | (2.130, 2.183) | +0.149 |
